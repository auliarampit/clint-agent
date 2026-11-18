#!/usr/bin/env python3
"""Pekerjaan mutu yang tertinggal di MR clint satu repo, tanpa token: bahan bagian status.

  utang-mutu.py <dir-project> [--hari N]

Sumber: kejadian `kirim` di ~/Library/Logs/clint/pr.jsonl untuk repo ini dalam N hari terakhir (default 14), lalu
deskripsi dan status MR lewat `glab api` (atau `gh pr view` bila `mr.cli` = gh).
- E2E tertunda tapi sudah merged: deskripsi MR masih memuat `E2E: tertunda` padahal MR sudah merged. Status Draft
  tidak dipakai, karena MR juga bisa Draft karena gerbang lain (mis. angka performa).
- PR feedback tanpa verifikasi jalur persis: branch `fix/fb-*` yang `verifikasi` di `kirim`-nya kosong atau `belum`
  (`develop/ship.md`: wajib `lulus` atau `tidak-terreproduksi` untuk PR dari bug/feedback).
"""
import argparse, json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

LOG = os.path.expanduser("~/Library/Logs/clint/pr.jsonl")
E2E = re.compile(r"E2E:\s*\**\s*([^\n]*)", re.I)
TERTUNDA = re.compile(r"^tertunda[\s,.:;*—–-]*", re.I)
MAKS = 10
FEEDBACK = re.compile(r"(^|/)fix/fb-")
SELESAI = ("lulus", "tidak-terreproduksi")


def kirim_repo(repo, sejak):
    out = {}
    try:
        baris = open(LOG, encoding="utf-8").readlines()
    except OSError:
        return []
    for b in baris:
        try:
            e = json.loads(b)
        except ValueError:
            continue
        if e.get("jadi") == "kirim" and e.get("mr") and e["t"][:10] >= sejak \
                and os.path.realpath(e["repo"].removesuffix("/.git")) == repo:
            out[e["mr"]] = e
    return [out[k] for k in sorted(out)]


def mr_info(repo, nomor, cli):
    """(state, deskripsi) atau None bila tidak terbaca."""
    if cli == "gh":
        cmd = ["gh", "pr", "view", str(nomor), "--json", "state,body"]
    else:
        cmd = ["glab", "api", f"projects/:id/merge_requests/{nomor}"]
    try:
        r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    if not d:
        return None
    return str(d.get("state", "")).lower(), d.get("description") or d.get("body") or ""


def e2e_tertunda(deskripsi):
    """Alasan singkat bila baris E2E terakhir di deskripsi menyatakan tertunda, selain itu None."""
    baris = E2E.findall(deskripsi)
    if not baris or not baris[-1].lower().startswith("tertunda"):
        return None
    return TERTUNDA.sub("", baris[-1]).replace("**", "").strip()[:110] or "tanpa alasan tertulis"


def susun(kirim, info):
    """kirim: daftar kejadian; info: nomor MR → (state, deskripsi) atau None."""
    tertunda, feedback, gagal = [], [], 0
    for e in kirim:
        i = info.get(e["mr"])
        if i is None:
            gagal += 1
        elif i[0] == "merged":
            alasan = e2e_tertunda(i[1])
            if alasan:
                tertunda.append(f"!{e['mr']} {e['branch']} · {alasan}")
        if FEEDBACK.search(e["branch"]) and e.get("verifikasi") not in SELESAI:
            feedback.append(f"!{e['mr']} {e['branch']} · verifikasi={e.get('verifikasi') or 'kosong'}")
    return tertunda, feedback, gagal


def daftar(baris):
    """Terbaru dulu, maksimal MAKS baris."""
    if not baris:
        return "(tidak ada)"
    terbaru = baris[::-1]
    sisa = f"\n(+{len(terbaru) - MAKS} lainnya)" if len(terbaru) > MAKS else ""
    return "\n".join(terbaru[:MAKS]) + sisa


def main():
    ap = argparse.ArgumentParser(description="E2E tertunda yang sudah merged dan PR feedback tanpa verifikasi")
    ap.add_argument("dir")
    ap.add_argument("--hari", type=int, default=14)
    a = ap.parse_args()
    repo = os.path.realpath(a.dir)
    try:
        cli = json.load(open(os.path.join(repo, ".claude", "clint.json"))).get("mr", {}).get("cli", "glab")
    except (OSError, ValueError):
        cli = "glab"
    sejak = (datetime.now() - timedelta(days=a.hari)).strftime("%Y-%m-%d")
    kirim = kirim_repo(repo, sejak)
    with ThreadPoolExecutor(8) as pool:
        info = dict(zip([e["mr"] for e in kirim], pool.map(lambda e: mr_info(repo, e["mr"], cli), kirim)))
    tertunda, feedback, gagal = susun(kirim, info)
    print(f"### E2E tertunda tapi MR sudah merged ({a.hari} hari; uji di base: /clint:test <fitur>): {len(tertunda)}")
    print(daftar(tertunda))
    print(f"### PR feedback tanpa verifikasi jalur persis ({a.hari} hari): {len(feedback)}")
    print(daftar(feedback))
    if gagal:
        print(f"({gagal} MR tidak terbaca dari {cli}; lihat manual)")


if __name__ == "__main__":
    main()
