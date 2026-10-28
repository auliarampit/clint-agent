#!/usr/bin/env python3
"""Potongan rencana untuk satu PR, tanpa token: yang dibaca developer dan peninjau, bukan rencana utuh.

  plan-slice.py <rencana> PR-<n> [--dir <path kerja>]

Bagian umum (lingkup, keputusan teknis, struktur berkas) tetap utuh. Baris tabel yang menyebut PR lain dan
subbagian `### PR-<lain>` dibuang; `## Status PR` dibuang. Baris tabel tanpa nomor PR tetap ada.
--dir: tulis ke `<git-common-dir>/clint/<branch>/rencana-PR-<n>.md` (folder kerja PR) dan cetak
`potongan=<path> ukuran=<byte>/<byte rencana>`. Tanpa --dir: cetak potongan ke stdout.
"""
import os, re, subprocess, sys

ID = re.compile(r"\bPR-\d+[a-z]?(?![\w-])")


def potong(teks, pr):
    out, buang_sub, buang_bagian = [], False, False
    for baris in teks.splitlines():
        judul = re.match(r"^(#+)\s+(.*)$", baris)
        if judul:
            level, isi = len(judul.group(1)), judul.group(2)
            if level <= 2:
                buang_bagian = isi.strip().lower() == "status pr"
                buang_sub = False
            if level >= 3:
                m = ID.match(isi)
                buang_sub = bool(m) and m.group(0) != pr
        if buang_bagian or buang_sub:
            continue
        if baris.lstrip().startswith("|"):
            disebut = set(ID.findall(baris))
            if disebut and pr not in disebut:
                continue
        out.append(baris)
    return "\n".join(out) + "\n"


def main():
    args = [a for a in sys.argv[1:]]
    kerja = None
    if "--dir" in args:
        i = args.index("--dir")
        kerja = os.path.abspath(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2 or not re.fullmatch(r"PR-\d+[a-z]?", args[1]):
        sys.exit(__doc__)
    rencana, pr = args
    teks = open(rencana, encoding="utf-8").read()
    hasil = potong(teks, pr)
    if not kerja:
        sys.stdout.write(hasil)
        return
    git = lambda *a: subprocess.run(["git", "-C", kerja, *a], capture_output=True, text=True,
                                    check=True).stdout.strip()
    folder = os.path.join(git("rev-parse", "--path-format=absolute", "--git-common-dir"), "clint",
                          git("branch", "--show-current"))
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"rencana-{pr}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(hasil)
    print(f"potongan={path} ukuran={len(hasil.encode())}/{len(teks.encode())}")


if __name__ == "__main__":
    main()
