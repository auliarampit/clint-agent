#!/usr/bin/env python3
"""Periksa hasil peninjau terhadap kasus uji emas, tanpa token: cacat yang ditanam harus ditemukan.

  golden-check.py <folder kasus> <folder temuan>

<folder kasus> = tests/golden/<nama>/ berisi diff.patch (perubahan dengan cacat yang ditanam) dan ekspektasi.json
(`wajib`: daftar {file, kata, tingkat_min}). <folder temuan> berisi temuan-<agent>.md hasil peninjau atas diff itu
(format seragam peninjau, diurai oleh merge-findings.py). Satu butir wajib terpenuhi bila ada temuan yang lokasinya
memuat `file`, teksnya memuat salah satu `kata` (tanpa beda huruf besar/kecil), dan tingkatnya >= `tingkat_min`.
Keluar 0 bila semua butir terpenuhi, 1 bila ada yang hilang. Jalankan setiap kali instruksi peninjau diubah.
"""
import glob, importlib.util, json, os, sys

AKAR = os.path.dirname(os.path.abspath(__file__))


def muat_parser():
    spek = importlib.util.spec_from_file_location("merge_findings", os.path.join(AKAR, "merge-findings.py"))
    mod = importlib.util.module_from_spec(spek)
    spek.loader.exec_module(mod)
    return mod


def periksa(wajib, temuan, tingkat):
    """[(butir, temuan yang cocok atau None)] untuk tiap butir wajib."""
    hasil = []
    for w in wajib:
        batas = tingkat.index(w["tingkat_min"])
        cocok = None
        for t in temuan:
            teks = (t["kepala"] + " " + " ".join(t["isi"])).lower()
            if (w["file"] in t["lokasi"] and tingkat.index(t["tingkat"]) <= batas
                    and any(k.lower() in teks for k in w["kata"])):
                cocok = t
                break
        hasil.append((w, cocok))
    return hasil


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    kasus, folder = sys.argv[1], sys.argv[2]
    mf = muat_parser()
    wajib = json.load(open(os.path.join(kasus, "ekspektasi.json"), encoding="utf-8"))["wajib"]
    berkas = sorted(glob.glob(os.path.join(folder, "temuan-*.md")))
    if not berkas:
        sys.exit(f"tidak ada temuan-*.md di {folder}")
    temuan = [t for b in berkas for t in mf.parse(b)[2]]
    hilang = 0
    for w, cocok in periksa(wajib, temuan, mf.TINGKAT):
        if cocok:
            print(f"ketemu  {w['file']} · [{cocok['tingkat']}] {cocok['kepala'][:120]} ({', '.join(cocok['agents'])})")
        else:
            hilang += 1
            print(f"HILANG  {w['file']} · minimal {w['tingkat_min']} · kata: {', '.join(w['kata'])}")
    print(f"kasus={os.path.basename(os.path.normpath(kasus))} wajib={len(wajib)} hilang={hilang} temuan={len(temuan)}")
    sys.exit(1 if hilang else 0)


if __name__ == "__main__":
    main()
