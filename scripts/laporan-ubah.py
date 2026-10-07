#!/usr/bin/env python3
"""Ubah laporan terakhir (~/Library/Logs/clint/terakhir.json) tanpa memeriksa ulang. Tanpa token.
  laporan-ubah.py selesai "<teks atau sumber>"
  laporan-ubah.py review  "<teks atau sumber>" "<MR !N>" "<url MR>"
  laporan-ubah.py periksa-mr          # hapus butir MR yang sudah merged/closed (glab/gh)"""
import json, os, subprocess, sys

P = os.path.expanduser("~/Library/Logs/clint/terakhir.json")
GRUP = ("gagal", "kerjakan", "cek", "tunggu")
if not os.path.exists(P):
    sys.exit(0)
d = json.load(open(P, encoding="utf-8"))
cocok = lambda x, k: k and (k == x.get("teks") or k == x.get("sumber") or k in (x.get("teks") or ""))

def simpan():
    tmp = P + ".tmp"; json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1); os.replace(tmp, P)

aksi = sys.argv[1] if len(sys.argv) > 1 else ""
if aksi == "selesai":
    for g in GRUP:
        d[g] = [x for x in d.get(g) or [] if not cocok(x, sys.argv[2])]
    simpan()
elif aksi == "review":
    k, mr, url = sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else ""
    pindah = None
    for g in ("gagal", "kerjakan", "tunggu"):
        for x in d.get(g) or []:
            if cocok(x, k) and pindah is None:
                pindah = x
        d[g] = [x for x in d.get(g) or [] if x is not pindah]
    if pindah:
        d.setdefault("cek", []).append({"teks": pindah.get("teks"), "proyek": pindah.get("proyek"),
                                       "sumber": mr, "url": url})
        simpan()
elif aksi == "periksa-mr":
    berubah = False
    for g in GRUP:
        sisa = []
        for x in d.get(g) or []:
            url = x.get("url") or ""
            if "/merge_requests/" in url or "/pull/" in url:
                cli = ["glab", "mr", "view", url, "-F", "json"] if "/merge_requests/" in url \
                    else ["gh", "pr", "view", url, "--json", "state"]
                try:
                    out = subprocess.run(cli, capture_output=True, text=True, timeout=20).stdout
                    st = (json.loads(out).get("state") or "").lower()
                except Exception:
                    st = ""
                if st in ("merged", "closed"):
                    berubah = True
                    continue
            sisa.append(x)
        d[g] = sisa
    if berubah:
        simpan()
