#!/usr/bin/env python3
"""Commit, rebase, push, MR, dan bersih-bersih satu PR dalam satu panggilan (skill develop 5.5–5.6), tanpa token.

  ship-pr.py --dir <path kerja> --commit <pesan.txt>:<daftar-file.txt> [--commit ...]
             [--plan <rencana> --pr PR-n --state review|draft|done]
             [--desc <deskripsi.md>] [--draft] [--saran <saran.json>]
             [--check "<perintah cek cepat>"]... [--butir "<ID/teks>" --proyek <nama>]
             [--asal <branch asal user> | --worktree] [--uji]

--commit dipakai berurutan: commit utama dulu, lalu commit perbaikan Low (`refactor: terapkan saran tinjauan`).
  daftar-file.txt berisi satu path per baris (stage eksplisit, tanpa `git add -A`).
--plan: status PR ditulis ke `## Status PR` lewat plan-status.py dan ikut commit pertama.
--check: dijalankan ulang hanya bila branch di-rebase; gagal → berhenti sebelum push.
--uji: cetak langkah tanpa menjalankan apa pun.
Mode MR dibaca dari .claude/clint.json (`mr.mode`, `mr.cli`, `mr.targetBranch`).
Keluaran key=value; exit ≠ 0 dengan `error=` saat berhenti. Tidak pernah force push.
"""
import argparse, json, os, subprocess, sys, time

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UJI = False


def jalan(args, cwd, cek=True, inp=None):
    if UJI:
        print("[uji] " + " ".join(args), file=sys.stderr)
        return ""
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, input=inp)
    if cek and r.returncode != 0:
        henti(f"{' '.join(args[:4])} gagal: {(r.stderr or r.stdout).strip()[:300]}")
    return r.stdout.strip()


def catat(data):
    """Satu baris per PR terkirim di ~/Library/Logs/clint/pr.jsonl, dibaca audit-usage.py."""
    if UJI:
        return
    log = os.path.expanduser("~/Library/Logs/clint/pr.jsonl")
    try:
        os.makedirs(os.path.dirname(log), exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "jadi": "kirim", **data}) + "\n")
    except OSError:
        pass


def mr_terbuka(lihat, cwd):
    if UJI:
        return None
    r = subprocess.run(lihat, cwd=cwd, capture_output=True, text=True)
    info = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}
    if str(info.get("state", "")).lower() not in ("open", "opened"):
        return None
    return info.get("iid") or info.get("number"), info.get("web_url") or info.get("url")


def henti(pesan, kode=1):
    print(f"error={pesan}")
    sys.exit(kode)


def main():
    global UJI
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--commit", action="append", default=[])
    ap.add_argument("--plan"); ap.add_argument("--pr"); ap.add_argument("--state")
    ap.add_argument("--desc"); ap.add_argument("--draft", action="store_true"); ap.add_argument("--saran")
    ap.add_argument("--check", action="append", default=[])
    ap.add_argument("--butir"); ap.add_argument("--proyek")
    ap.add_argument("--asal"); ap.add_argument("--worktree", action="store_true")
    ap.add_argument("--uji", action="store_true")
    a = ap.parse_args()
    UJI = a.uji
    kerja = os.path.abspath(a.dir)
    common = subprocess.run(["git", "-C", kerja, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True).stdout.strip()
    repo = os.path.dirname(common)
    cfg = json.load(open(os.path.join(repo, ".claude", "clint.json")))
    mode = cfg.get("mr", {}).get("mode", "mr")
    cli = cfg.get("mr", {}).get("cli", "glab")
    base = cfg.get("baseBranch", "dev")
    target = cfg.get("mr", {}).get("targetBranch", base)
    branch = subprocess.run(["git", "-C", kerja, "branch", "--show-current"], capture_output=True,
                            text=True).stdout.strip()
    if not branch or branch == base:
        henti(f"path kerja tidak berada di branch PR (sekarang: {branch or 'detached'})")

    for i, spec in enumerate(a.commit):
        pesan, daftar = spec.split(":", 1)
        files = [l.strip() for l in open(daftar) if l.strip()]
        if i == 0 and a.plan:
            jalan(["python3", f"{R}/scripts/plan-status.py", a.plan, "--repo", kerja,
                   "--set", f"{a.pr}={a.state}", "--write"], kerja)
            files.append(a.plan)
        jalan(["git", "add", "--", *files], kerja)
        if not jalan(["git", "diff", "--cached", "--name-only"], kerja) and not UJI:
            henti(f"tidak ada perubahan ter-stage untuk {pesan}")
        jalan(["git", "commit", "-q", "-F", pesan], kerja)
        print(f"commit={jalan(['git', 'log', '-1', '--format=%h %s'], kerja)}")
    sisa = jalan(["git", "status", "--porcelain", "--untracked-files=no"], kerja)
    if sisa:
        print("belum_dicommit=" + " ".join(l[3:] for l in sisa.splitlines()))

    jalan(["git", "fetch", "-q", "origin", base], kerja)
    tertinggal = jalan(["git", "rev-list", "--count", f"HEAD..origin/{base}"], kerja) or "0"
    if int(tertinggal) > 0:
        r = subprocess.run(["git", "rebase", "-q", f"origin/{base}"], cwd=kerja, capture_output=True, text=True) \
            if not UJI else None
        if r and r.returncode != 0:
            subprocess.run(["git", "rebase", "--abort"], cwd=kerja)
            henti(f"konflik rebase ke origin/{base}; branch dibiarkan seperti sebelum rebase", 3)
        print(f"rebase=origin/{base} ({tertinggal} commit)")
        for c in a.check:
            r = subprocess.run(c, shell=True, cwd=kerja, capture_output=True, text=True) if not UJI else None
            if r and r.returncode != 0:
                henti(f"cek setelah rebase gagal: {c}\n{(r.stdout + r.stderr)[-1500:]}", 4)
            print(f"cek={c} lulus")

    if mode == "push-base":
        jalan(["git", "switch", "-q", base], repo)
        jalan(["git", "merge", "-q", "--ff-only", f"origin/{base}"], repo)
        jalan(["git", "merge", "-q", "--ff-only", branch], repo)
        r = subprocess.run(["git", "push", "-q", "origin", base], cwd=repo, capture_output=True, text=True) \
            if not UJI else None
        if r and r.returncode != 0:
            henti(f"push ke {base} ditolak; commit ada di {base} lokal, jalankan `git push origin {base}`: "
                  f"{r.stderr.strip()[:200]}", 5)
        print(f"push={base}")
        catat({"repo": repo, "branch": branch, "mr": None, "mode": mode, "plan": a.plan, "pr": a.pr, "draft": False})
        if a.worktree:
            jalan(["git", "worktree", "remove", kerja], repo)
        jalan(["git", "branch", "-q", "-D", branch], repo)
        print(f"bersih=branch {branch} dihapus")
        return

    jalan(["git", "push", "-q", "-u", "origin", branch], kerja)
    judul = open(a.commit[0].split(":", 1)[0]).readline().strip() if a.commit else branch
    lihat = (["gh", "pr", "view", branch, "--json", "number,url,state"] if cli == "gh"
             else ["glab", "mr", "view", branch, "-F", "json"])
    mr = mr_terbuka(lihat, kerja)
    if mr:
        nomor, url = mr
        print(f"mr=!{nomor} {url} (sudah ada, hanya di-push)")
    else:
        if cli == "gh":
            args = ["gh", "pr", "create", "--base", target, "--head", branch, "--title", judul,
                    "--body-file", a.desc or os.devnull]
        else:
            args = ["glab", "mr", "create", "--source-branch", branch, "--target-branch", target, "--title", judul,
                    "--description", open(a.desc).read() if a.desc else "", "--yes"]
        jalan(args + (["--draft"] if a.draft else []), kerja)
        mr = mr_terbuka(lihat, kerja)
        if not mr and not UJI:
            henti(f"MR tidak ditemukan setelah dibuat; buat manual dari branch {branch}", 6)
        nomor, url = mr or ("?", "")
        print(f"mr=!{nomor} {url}" + (" draft" if a.draft else ""))
        catat({"repo": repo, "branch": branch, "mr": nomor, "mode": mode, "plan": a.plan, "pr": a.pr,
               "draft": bool(a.draft)})

    if a.saran and os.path.getsize(a.saran) > 2:
        blok = jalan(["python3", f"{R}/scripts/mr-suggestions.py", str(nomor), a.saran, "--deskripsi"], kerja)
        if blok:
            desk = (open(a.desc).read() if a.desc else "") + "\n\n" + blok
            if cli == "gh":
                jalan(["gh", "pr", "edit", str(nomor), "--body", desk], kerja)
            else:
                jalan(["glab", "mr", "update", str(nomor), "--description", desk], kerja)
            print("saran=ditambahkan ke deskripsi")
    if a.butir and a.proyek:
        jalan(["python3", f"{R}/scripts/update-report.py", "review", a.butir, f"MR !{nomor}", url or "",
               "--proyek", a.proyek], kerja, cek=False)

    if a.worktree:
        jalan(["git", "worktree", "remove", kerja], repo)
        jalan(["git", "worktree", "prune"], repo)
        jalan(["git", "branch", "-q", "-D", branch], repo)
        print(f"bersih=worktree {kerja} dihapus")
    elif a.asal:
        jalan(["git", "switch", "-q", a.asal], repo)
        jalan(["git", "branch", "-q", "-D", branch], repo)
        print(f"bersih=kembali ke {a.asal}, branch {branch} dihapus")


if __name__ == "__main__":
    main()
