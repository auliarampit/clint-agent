#!/usr/bin/env python3
"""Cek lokal satu PR sekaligus dan paralel, tanpa token: lint file yang berubah, typecheck, test terkait.

  run-checks.py <path kerja> [--base <ref>] [--penuh]

Perintah dari `.claude/clint.json` per surface: `lintRelated` + file yang berubah (tanpa `lintRelated`, atau
dengan --penuh: `lint` seluruh surface), `typecheck`, `testRelated` + file yang berubah. File berubah =
diff terhadap `--base` (default `origin/<baseBranch>`) + perubahan belum di-commit + file baru.
Keluaran lengkap disimpan di `<folder kerja PR>/checks/<surface>-<cek>.log`, ringkasan di `checks.md`.
Stdout: `<surface>.<cek>=lulus|gagal|lewat <detik>s`, lalu 40 baris terakhir keluaran cek yang gagal.
Exit 1 bila ada yang gagal.
"""
import json, os, re, shlex, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

KODE = re.compile(r"\.(ts|tsx|js|jsx|mjs|cjs|vue|svelte)$")
KOSONG = (None, "", "TIDAK ADA")


def git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True).stdout


def berubah(kerja, base):
    nama = set(git(kerja, "diff", "--name-only", "--diff-filter=d", f"{base}...HEAD").split())
    nama |= set(git(kerja, "diff", "--name-only", "--diff-filter=d", "HEAD").split())
    nama |= set(git(kerja, "ls-files", "--others", "--exclude-standard").split())
    return sorted(n for n in nama if os.path.exists(os.path.join(kerja, n)))


def jalan(nama, perintah, cwd, log):
    t = time.time()
    r = subprocess.run(perintah, shell=True, cwd=cwd, capture_output=True, text=True)
    keluaran = r.stdout + r.stderr
    with open(log, "w", encoding="utf-8") as f:
        f.write(f"$ {perintah}\n\n{keluaran}")
    return nama, r.returncode == 0, time.time() - t, keluaran, log


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    kerja = os.path.abspath(args[0])
    penuh = "--penuh" in args
    common = git(kerja, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    cfg = json.load(open(os.path.join(os.path.dirname(common), ".claude", "clint.json")))
    base = args[args.index("--base") + 1] if "--base" in args else f"origin/{cfg.get('baseBranch', 'dev')}"
    folder = os.path.join(common, "clint", git(kerja, "branch", "--show-current").strip() or "detached")
    os.makedirs(os.path.join(folder, "checks"), exist_ok=True)
    files = berubah(kerja, base)

    tugas, lewat = [], []
    for s in cfg.get("surfaces", []):
        root = os.path.normpath(s.get("root", "."))
        awalan = "" if root == "." else root + "/"
        kode = [shlex.quote(f[len(awalan):]) for f in files if f.startswith(awalan) and KODE.search(f)]
        cwd = os.path.join(kerja, root)
        cek = {}
        if s.get("lintRelated") not in KOSONG and not penuh:
            cek["lint"] = f"{s['lintRelated']} {' '.join(kode)}" if kode else None
        elif s.get("lint") not in KOSONG:
            cek["lint"] = s["lint"]
        if s.get("typecheck") not in KOSONG:
            cek["typecheck"] = s["typecheck"] if kode or penuh else None
        if s.get("testRelated") not in KOSONG:
            cek["test"] = f"{s['testRelated']} {' '.join(kode)}" if kode else None
        for c, perintah in cek.items():
            nama = f"{s.get('name', root)}.{c}"
            if perintah is None:
                lewat.append(nama)
            else:
                tugas.append((nama, perintah, cwd, os.path.join(folder, "checks", f"{nama}.log")))

    with ThreadPoolExecutor(max_workers=max(len(tugas), 1)) as ex:
        hasil = list(ex.map(lambda t: jalan(*t), tugas))

    ringkas = [f"# Cek lokal ({'penuh' if penuh else 'file berubah'}, {len(files)} file berubah)", ""]
    gagal = []
    for nama, ok, detik, keluaran, log in hasil:
        baris = f"{nama}={'lulus' if ok else 'gagal'} {detik:.0f}s"
        print(baris)
        ringkas.append(f"- {baris} · {log}")
        if not ok:
            gagal.append((nama, keluaran))
    for nama in lewat:
        print(f"{nama}=lewat (tidak ada file kode berubah)")
        ringkas.append(f"- {nama}=lewat")
    for nama, keluaran in gagal:
        print(f"\n--- {nama} ---\n" + "\n".join(keluaran.rstrip().splitlines()[-40:]))
    with open(os.path.join(folder, "checks.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(ringkas) + "\n")
    print(f"checks={os.path.join(folder, 'checks.md')}")
    sys.exit(1 if gagal else 0)


if __name__ == "__main__":
    main()
