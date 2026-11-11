#!/usr/bin/env python3
"""Hasil nyata tiap MR yang dikirim clint, tanpa token: lolos review manusia atau perlu direvisi.

  outcome-mr.py [--sejak YYYY-MM-DD] [--json <file>]

Sumber: kejadian `kirim` di ~/Library/Logs/clint/pr.jsonl (repo + nomor MR), lalu GitLab lewat `glab api` dari dalam
repo-nya. Per MR dicatat status, komentar manusia (bukan catatan sistem dan bukan akun bot), jumlah push susulan
setelah MR dibuka (perkiraan kasar pekerjaan ulang: push clint dan push manual tidak dibedakan), dan jam ke merge.
MR merged/closed disimpan di ~/Library/Logs/clint/outcome.jsonl supaya tidak ditarik ulang; MR open selalu ditarik ulang.
Kejadian `tinjau` ikut digabung untuk menunjukkan MR yang dikomentari manusia padahal clint sudah meninjaunya.
Hanya 100 catatan pertama tiap MR yang dibaca.
"""
import argparse, json, os, re, statistics, subprocess
from collections import defaultdict
from datetime import datetime

LOG = os.path.expanduser("~/Library/Logs/clint/pr.jsonl")
CACHE = os.path.expanduser("~/Library/Logs/clint/outcome.jsonl")
PUSH = re.compile(r"^added \d+ commits?")


def waktu(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def glab(repo, path):
    try:
        r = subprocess.run(["glab", "api", path], cwd=repo, capture_output=True, text=True, timeout=60)
        return json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def susun(mr, notes):
    """Satu baris hasil dari JSON MR dan daftar catatannya GitLab."""
    dibuka = waktu(mr["created_at"])
    merged = waktu(mr["merged_at"]) if mr.get("merged_at") else None
    manusia = [n for n in notes if not n.get("system") and not (n.get("author") or {}).get("bot")]
    push = [n for n in notes if n.get("system") and PUSH.match(n.get("body", ""))
            and waktu(n["created_at"]) > dibuka]
    return {"state": mr["state"], "komentar_manusia": len(manusia), "push_susulan": len(push),
            "jam_ke_merge": round((merged - dibuka).total_seconds() / 3600, 1) if merged else None}


def ambil(repo, nomor):
    mr = glab(repo, f"projects/:id/merge_requests/{nomor}")
    notes = glab(repo, f"projects/:id/merge_requests/{nomor}/notes?per_page=100&sort=asc")
    if mr is None or notes is None:
        return None
    return susun(mr, notes)


def baca_jsonl(path):
    try:
        for baris in open(path, encoding="utf-8"):
            try:
                yield json.loads(baris)
            except ValueError:
                continue
    except OSError:
        return


def tinjau_per_branch():
    """(repo, branch) → jumlah Critical+Major di putaran pertama dan jumlah putaran."""
    out = {}
    for e in baca_jsonl(LOG):
        if e.get("jadi") != "tinjau":
            continue
        k = (e["repo"].removesuffix("/.git"), e["branch"])
        lama = out.get(k, {"berat": 0, "putaran": 0})
        if e["putaran"] == 1:
            lama["berat"] = e["jumlah"]["Critical"] + e["jumlah"]["Major"]
        lama["putaran"] = max(lama["putaran"], e["putaran"])
        out[k] = lama
    return out


def ringkasan(rows, judul):
    n = len(rows)
    terbaca = [r for r in rows if r.get("state")]
    selesai = [r for r in terbaca if r["state"] in ("merged", "closed")]
    bersih = [r for r in selesai if r["komentar_manusia"] == 0]
    dikomentari = [r for r in terbaca if r["komentar_manusia"] > 0]
    susulan = [r for r in terbaca if r["push_susulan"] > 0]
    jam = [r["jam_ke_merge"] for r in terbaca if r.get("jam_ke_merge") is not None]
    out = [f"# Hasil MR clint {judul}", "",
           f"MR dikirim: {n} · terbaca {len(terbaca)} · selesai {len(selesai)} "
           f"(merged {sum(r['state'] == 'merged' for r in terbaca)}, closed {sum(r['state'] == 'closed' for r in terbaca)})"
           f" · open {sum(r['state'] == 'opened' for r in terbaca)} · tidak terbaca {n - len(terbaca)}"]
    if selesai:
        out.append(f"- Lolos tanpa komentar manusia: {len(bersih)} dari {len(selesai)} MR selesai "
                   f"({round(100 * len(bersih) / len(selesai))}%)")
    out.append(f"- MR dengan komentar manusia: {len(dikomentari)} · total {sum(r['komentar_manusia'] for r in dikomentari)} komentar")
    out.append(f"- MR dengan push susulan setelah dibuka: {len(susulan)} (perkiraan kasar pekerjaan ulang)")
    if jam:
        out.append(f"- Jam sampai merge: median {statistics.median(jam)} · maks {max(jam)}")
    per = defaultdict(list)
    for r in terbaca:
        per[r["repo"].rstrip("/").split("/")[-1]].append(r)
    if len(per) > 1:
        out += ["", "## Per repo"]
        for repo, L in sorted(per.items()):
            sel = [r for r in L if r["state"] in ("merged", "closed")]
            ok = sum(r["komentar_manusia"] == 0 for r in sel)
            out.append(f"- {repo}: {len(L)} MR · lolos tanpa komentar {ok}/{len(sel)} · "
                       f"komentar manusia {sum(r['komentar_manusia'] for r in L)}")
    if dikomentari:
        out += ["", "## MR yang dikomentari manusia (periksa apa yang lolos dari peninjau clint)"]
        for r in sorted(dikomentari, key=lambda r: -r["komentar_manusia"])[:15]:
            t = r.get("tinjau")
            clint = f"clint {t['putaran']} putaran, {t['berat']} Major di putaran 1" if t else "tanpa catatan tinjau"
            out.append(f"- !{r['mr']} {r['branch']} · {r['komentar_manusia']} komentar · {clint}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Hasil nyata MR clint (komentar manusia, push susulan, waktu merge)")
    ap.add_argument("--sejak", default="0000-00-00")
    ap.add_argument("--json")
    a = ap.parse_args()

    kirim = {}
    for e in baca_jsonl(LOG):
        if e.get("jadi") == "kirim" and e.get("mr") and e["t"][:10] >= a.sejak:
            kirim[(e["repo"], e["mr"])] = e
    cache = {(r["repo"], r["mr"]): r for r in baca_jsonl(CACHE)}
    tinjau = tinjau_per_branch()
    rows, baru = [], []
    for (repo, nomor), e in sorted(kirim.items(), key=lambda x: x[1]["t"]):
        r = cache.get((repo, nomor))
        if not r:
            hasil = ambil(repo, nomor)
            r = {"repo": repo, "mr": nomor, "branch": e["branch"], **(hasil or {})}
            if hasil and hasil["state"] in ("merged", "closed"):
                baru.append(r)
        r["tinjau"] = tinjau.get((repo.removesuffix("/.git"), e["branch"]))
        rows.append(r)
    if baru:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "a", encoding="utf-8") as f:
            for r in baru:
                f.write(json.dumps({k: v for k, v in r.items() if k != "tinjau"}, ensure_ascii=False) + "\n")
    judul = f"sejak {a.sejak}" if a.sejak != "0000-00-00" else "(semua)"
    print(ringkasan(rows, judul))
    if a.json:
        json.dump(rows, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
