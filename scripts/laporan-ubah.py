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

    def repo_untuk(url):
        """Folder repo lokal yang remote-nya sama dengan alamat MR/PR (glab/gh harus jalan di dalam repo)."""
        m = re.search(r"https?://[^/]+/(.+?)/(?:-/merge_requests|pull)/", url or "")
        if not m:
            return None
        for dirp in DIR.values():
            try:
                if m.group(1) in subprocess.run(["git", "-C", dirp, "remote", "get-url", "origin"],
                                                capture_output=True, text=True, timeout=5).stdout:
                    return dirp
            except Exception:
                pass
        return None

    _mr = {}
    def mr_terbaru(dirp):
        """MR/PR yang dibuat atau di-merge setelah laporan dibuat, sekali ambil per project (tanpa token)."""
        if dirp in _mr:
            return _mr[dirp]
        xs = []
        try:
            if "github.com" in subprocess.run(["git", "-C", dirp, "remote", "get-url", "origin"],
                                              capture_output=True, text=True, timeout=5).stdout:
                out = subprocess.run(["gh", "pr", "list", "--state", "all", "--limit", "30", "--json",
                                      "state,createdAt,mergedAt,title,body,url,number"],
                                     cwd=dirp, capture_output=True, text=True, timeout=20).stdout
                for x in json.loads(out or "[]"):
                    xs.append({"state": x["state"].lower(), "created_at": x.get("createdAt"), "merged_at": x.get("mergedAt"),
                               "teks": f"{x.get('title') or ''} {x.get('body') or ''}", "url": x.get("url"), "ref": f"PR #{x.get('number')}"})
            else:
                out = subprocess.run(["glab", "mr", "list", "--all", "--per-page", "30", "-F", "json"],
                                     cwd=dirp, capture_output=True, text=True, timeout=20).stdout
                for x in json.loads(out or "[]"):
                    xs.append({"state": x.get("state"), "created_at": x.get("created_at"), "merged_at": x.get("merged_at"),
                               "teks": f"{x.get('title') or ''} {x.get('description') or ''} {x.get('source_branch') or ''}",
                               "url": x.get("web_url"), "ref": f"MR !{x.get('iid')}"})
        except Exception:
            pass
        def waktu(v):
            try:
                return datetime.datetime.fromisoformat((v or "").replace("Z", "+00:00"))
            except ValueError:
                return None
        _mr[dirp] = [x for x in xs if (waktu(x["merged_at"]) or waktu(x["created_at"]) or dibuat) > dibuat]
        return _mr[dirp]

    def penanda(sumber):
        """ID dari sumber butir: kode seperti ABC-1/BUG-M-02, dan nomor seperti 'UI-mobile #12' (disertai kata
        di depannya supaya '#12' milik dokumen lain tidak ikut cocok)."""
        ids = [(i, []) for i in re.findall(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b", sumber)]
        for kata, no in re.findall(r"([A-Za-z][\w-]*)\s*#(\d+)", sumber):
            ids.append((f"#{no}", [w for w in re.split(r"[-_ ]", kata.lower()) if len(w) >= 2]))
        return ids

    def cocok(mr, ident, konteks):
        t = mr["teks"].upper()
        if ident.startswith("#"):
            no = ident[1:]
            ada = re.search(rf"(#|\b(?:UI|BUTIR|NO|NOMOR|FEEDBACK)[- ]?){no}\b", t) or re.search(rf"\b\w+-{no}\b", t)
            return bool(ada) and all(k.upper() in t for k in konteks[:1])
        return ident.upper() in t

    # Butir tanpa url:
    #  - semua ID disebut MR yang sudah merged setelah laporan → selesai (hilang);
    #  - salah satu ID disebut MR yang masih open → pindah ke "Menunggu review Anda" dengan tautannya.
    for g in ("gagal", "kerjakan", "cek"):
        sisa = []
        for x in d.get(g) or []:
            ids, dirp = penanda(x.get("sumber") or ""), DIR.get(x.get("proyek"))
            if x.get("url") or not ids or not dirp:
                sisa.append(x); continue
            mrs = mr_terbaru(dirp)
            if all(any(m["state"] == "merged" and cocok(m, i, k) for m in mrs) for i, k in ids):
                berubah = True; continue
            buka = next((m for m in mrs if m["state"] == "opened" or m["state"] == "open"
                         for i, k in ids if cocok(m, i, k)), None)
            if buka:
                berubah = True
                d.setdefault("cek", []).append({"teks": x.get("teks"), "proyek": x.get("proyek"),
                                                "sumber": buka["ref"], "url": buka["url"]})
                continue
            sisa.append(x)
        d[g] = sisa
    for g in GRUP:
        sisa = []
        for x in d.get(g) or []:
            url = x.get("url") or ""
            nomor = re.search(r"(?:MR\s*!|PR\s*#)(\d+)", x.get("sumber") or "")
            dirp = DIR.get(x.get("proyek")) or repo_untuk(url)
            cli = None
            if "/merge_requests/" in url or "/pull/" in url:
                cli = ["glab", "mr", "view", url, "-F", "json"] if "/merge_requests/" in url \
                    else ["gh", "pr", "view", url, "--json", "state"]
            elif nomor and dirp:     # butir hanya menyebut "MR !130" / "PR #12" tanpa tautan
                cli = ["gh", "pr", "view", nomor.group(1), "--json", "state"] if "PR" in nomor.group(0) \
                    else ["glab", "mr", "view", nomor.group(1), "-F", "json"]
            if cli:
                try:
                    out = subprocess.run(cli, capture_output=True, text=True, timeout=20, cwd=dirp or None).stdout
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
