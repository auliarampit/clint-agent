#!/usr/bin/env python3
"""Daftar temuan peninjau yang berulang per repo, tanpa token: bahan aturan di adapter project.

  pelajaran.py [--min N] [--repo <kata>] [--contoh K]

Membaca semua <repo>/.git/clint/**/temuan-*.md (format seragam peninjau, diurai oleh merge-findings.py) untuk repo yang
tercatat di ~/Library/Logs/clint/pr.jsonl. Satu kategori dihitung sekali per PR (folder kerja), jadi satu PR yang
mengulang kategori yang sama tidak menggelembungkan angka. Kategori yang muncul di >= N PR (default 3) dicetak
dengan contoh temuan dan tingkat tertingginya. Skrip tidak menulis aturan: rumuskan satu baris per kategori yang
memang berulang, tambahkan ke adapter bagian "Larangan khusus project ini", lalu minta persetujuan sebelum commit.
"""
import argparse, glob, importlib.util, json, os
from collections import defaultdict

LOG = os.path.expanduser("~/Library/Logs/clint/pr.jsonl")
AKAR = os.path.dirname(os.path.abspath(__file__))


def muat_parser():
    spek = importlib.util.spec_from_file_location("merge_findings", os.path.join(AKAR, "merge-findings.py"))
    mod = importlib.util.module_from_spec(spek)
    spek.loader.exec_module(mod)
    return mod


def repo_tercatat():
    ada = set()
    try:
        for baris in open(LOG, encoding="utf-8"):
            try:
                r = json.loads(baris).get("repo")
            except ValueError:
                continue
            if r:
                ada.add(r.removesuffix("/.git"))
    except OSError:
        pass
    return sorted(ada)


def kandidat(repo, mf, minimal):
    """kategori → {"pr": set folder, "tingkat": terberat, "contoh": [kepala, ...]} untuk satu repo."""
    kat = defaultdict(lambda: {"pr": set(), "tingkat": 99, "contoh": []})
    for berkas in glob.glob(os.path.join(repo, ".git", "clint", "**", "temuan-*.md"), recursive=True):
        folder = os.path.dirname(berkas)
        for it in mf.parse(berkas)[2]:
            if not it["kategori"]:
                continue
            k = kat[it["kategori"]]
            k["pr"].add(folder)
            k["tingkat"] = min(k["tingkat"], mf.TINGKAT.index(it["tingkat"]))
            k["contoh"].append(it["kepala"])
    return {n: k for n, k in kat.items() if len(k["pr"]) >= minimal}


def main():
    ap = argparse.ArgumentParser(description="Temuan peninjau yang berulang per repo")
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--repo", default="")
    ap.add_argument("--contoh", type=int, default=2)
    a = ap.parse_args()
    mf = muat_parser()
    ada = False
    for repo in repo_tercatat():
        if a.repo not in repo or not os.path.isdir(os.path.join(repo, ".git")):
            continue
        hasil = kandidat(repo, mf, a.min)
        if not hasil:
            continue
        ada = True
        print(f"## {repo}")
        for nama, k in sorted(hasil.items(), key=lambda x: (-len(x[1]["pr"]), x[0])):
            print(f"- {nama}: {len(k['pr'])} PR · terberat {mf.TINGKAT[k['tingkat']]}")
            for c in k["contoh"][:a.contoh]:
                print(f"    · {c[:160]}")
        print()
    if not ada:
        print(f"Tidak ada kategori yang muncul di >= {a.min} PR.")


if __name__ == "__main__":
    main()
