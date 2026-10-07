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
# Waktu laporan dibuat disimpan sekali; mtime berubah setiap kali butir diubah.
baru_dibuat = "_dibuat" not in d
d.setdefault("_dibuat", os.path.getmtime(P))
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
    import re, datetime
    berubah = baru_dibuat
    dibuat = datetime.datetime.fromtimestamp(d["_dibuat"]).astimezone()
    DIR = {x.get("nama"): x.get("dir") for x in d.get("proyek") or [] if x.get("dir")}

    def merged_setelah_laporan(dirp, ident):
        """Ada MR/PR merged setelah laporan dibuat yang menyebut ident di judul/deskripsi? (tanpa token)"""
        try:
            if "github.com" in subprocess.run(["git", "-C", dirp, "remote", "get-url", "origin"],
                                              capture_output=True, text=True, timeout=5).stdout:
                out = subprocess.run(["gh", "pr", "list", "--state", "merged", "--search", ident, "--limit", "5",
                                      "--json", "mergedAt,title,body"], cwd=dirp, capture_output=True, text=True, timeout=20).stdout
                xs = [{"merged_at": x.get("mergedAt"), "title": x.get("title"), "description": x.get("body")} for x in json.loads(out or "[]")]
            else:
                out = subprocess.run(["glab", "mr", "list", "--merged", "--search", ident, "--per-page", "5", "-F", "json"],
                                     cwd=dirp, capture_output=True, text=True, timeout=20).stdout
                xs = json.loads(out or "[]")
        except Exception:
            return False
        for x in xs:
            try:
                t = datetime.datetime.fromisoformat((x.get("merged_at") or "").replace("Z", "+00:00"))
            except ValueError:
                continue
            teks = f"{x.get('title') or ''} {x.get('description') or ''}".upper()
            if t > dibuat and ident.upper() in teks:
                return True
        return False

    # Butir tanpa url: selesai bila SEMUA ID-nya disebut MR yang merged setelah laporan dibuat.
    for g in ("gagal", "kerjakan", "cek"):
        sisa = []
        for x in d.get(g) or []:
            ids = re.findall(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b", x.get("sumber") or "")
            dirp = DIR.get(x.get("proyek"))
            if not x.get("url") and ids and dirp and all(merged_setelah_laporan(dirp, i) for i in ids):
                berubah = True
                continue
            sisa.append(x)
        d[g] = sisa
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
    if berubah:            # simpan hanya bila ada butir yang berubah (mtime tetap jujur)
        simpan()
