#!/usr/bin/env python3
"""Ubah laporan terakhir (~/Library/Logs/clint/terakhir.json) tanpa memeriksa ulang. Tanpa token.
  update-report.py merge   <laporan.json>                     # ganti entri project yang ada di file baru saja
  update-report.py selesai "<sumber|teks|b64:...>" [--proyek <nama>]
  update-report.py review  "<sumber|teks|b64:...>" "<MR !N>" "<url MR>" [--proyek <nama>]
  update-report.py periksa-mr          # hapus butir MR yang sudah merged/closed (glab/gh)"""
import base64, contextlib, fcntl, json, os, subprocess, sys, tempfile, time

P = os.path.expanduser("~/Library/Logs/clint/terakhir.json")
GRUP = ("gagal", "kerjakan", "cek", "tunggu")


def baca():
    try:
        d = json.load(open(P, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d


def simpan(d):
    if "_dibuat" not in d:
        d["_dibuat"] = os.path.getmtime(P) if os.path.exists(P) else time.time()
    fd, tmp = tempfile.mkstemp(prefix=".terakhir.", suffix=".tmp", dir=os.path.dirname(P))
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, P)


@contextlib.contextmanager
def kunci():
    os.makedirs(os.path.dirname(P), exist_ok=True)
    with open(P + ".lock", "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        yield


def norm(s):
    return str(s or "").strip().lower()


def pilih(d, k, proyek, grup):
    """Butir yang cocok tepat pada sumber/teks; substring hanya bila hasilnya tepat satu."""
    if k.startswith("b64:"):
        k = base64.urlsafe_b64decode(k[4:] + "=" * (-len(k[4:]) % 4)).decode("utf-8")
    n = norm(k)
    if not n:
        return []
    kand = [(g, x) for g in grup for x in d.get(g) or [] if not proyek or x.get("proyek") == proyek]
    tepat = [(g, x) for g, x in kand if n in (norm(x.get("sumber")), norm(x.get("teks")))]
    if tepat:
        return tepat
    sub = [(g, x) for g, x in kand if n in norm(x.get("teks"))]
    return sub if len(sub) == 1 else []


def gabung(lama, baru):
    """Ganti entri project yang ada di `baru` (cocok berdasarkan dir); project lain dipertahankan."""
    if not lama:
        return dict(baru)
    dirs = {p.get("dir") for p in baru.get("proyek") or [] if p.get("dir")}
    nama_baru = {p.get("nama") for p in baru.get("proyek") or []}
    dir_lama = {p.get("nama"): p.get("dir") for p in lama.get("proyek") or []}
    milik_lain = lambda x, nama: (x.get("dir") or dir_lama.get(x.get(nama))) not in dirs

    d = dict(lama)
    for k, v in baru.items():
        if k not in GRUP + ("proyek", "berikutnya", "rincian"):
            d[k] = v
    d["proyek"] = [p for p in lama.get("proyek") or [] if p.get("dir") not in dirs] + list(baru.get("proyek") or [])
    for g in GRUP:
        d[g] = [x for x in lama.get(g) or [] if milik_lain(x, "proyek")] + list(baru.get(g) or [])
    d["rincian"] = [r for r in lama.get("rincian") or [] if r.get("proyek") not in nama_baru] + \
        list(baru.get("rincian") or [])
    nl, nb = lama.get("berikutnya"), baru.get("berikutnya")
    if isinstance(nb, list):
        d["berikutnya"] = [b for b in (nl if isinstance(nl, list) else []) if milik_lain(b, "proyek")] + nb
    elif nb:
        d["berikutnya"] = nb
    return d


def argumen():
    a, proyek = sys.argv[2:], None
    if "--proyek" in a:
        i = a.index("--proyek")
        proyek = a[i + 1] if i + 1 < len(a) else None
        a = a[:i] + a[i + 2:]
    return a, proyek


aksi = sys.argv[1] if len(sys.argv) > 1 else ""
if aksi == "merge":
    baru = json.load(open(sys.argv[2], encoding="utf-8"))
    with kunci():
        d = gabung(baca(), baru)
        d["_dibuat"] = time.time()
        simpan(d)
    sys.exit(0)

if not os.path.exists(P):
    sys.exit(0)

if aksi == "selesai":
    a, proyek = argumen()
    with kunci():
        d = baca()
        kena = pilih(d, a[0], proyek, GRUP) if d and a else []
        if kena:
            ids = {id(x) for _, x in kena}
            for g in GRUP:
                d[g] = [x for x in d.get(g) or [] if id(x) not in ids]
            simpan(d)
elif aksi == "review":
    a, proyek = argumen()
    k, mr, url = a[0], a[1], a[2] if len(a) > 2 else ""
    with kunci():
        d = baca()
        kena = pilih(d, k, proyek, ("gagal", "kerjakan", "tunggu")) if d else []
        if kena:
            g, x = kena[0]
            d[g] = [y for y in d[g] if y is not x]
            d.setdefault("cek", []).append({"teks": x.get("teks"), "proyek": x.get("proyek"),
                                           "sumber": mr, "url": url})
            simpan(d)
elif aksi == "periksa-mr":
    import copy, re, datetime
    d0 = baca()
    if d0 is None:
        sys.exit(0)
    d = copy.deepcopy(d0)
    sidik = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False)
    ops = []   # diterapkan ulang ke isi terbaru saat menyimpan
    dibuat = datetime.datetime.fromtimestamp(d.get("_dibuat") or os.path.getmtime(P)).astimezone()
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
                ops.append((g, sidik(x), None)); continue
            buka = next((m for m in mrs if m["state"] == "opened" or m["state"] == "open"
                         for i, k in ids if cocok(m, i, k)), None)
            if buka:
                pindah = {"teks": x.get("teks"), "proyek": x.get("proyek"), "sumber": buka["ref"], "url": buka["url"]}
                ops.append((g, sidik(x), pindah))
                d.setdefault("cek", []).append(pindah)
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
                    ops.append((g, sidik(x), None))
                    continue
            sisa.append(x)
        d[g] = sisa

    with kunci():
        d = baca()
        if d is None:
            sys.exit(0)
        berubah = "_dibuat" not in d
        for g, k, pindah in ops:
            xs = d.get(g) or []
            i = next((i for i, x in enumerate(xs) if sidik(x) == k), None)
            if i is None:
                continue
            del xs[i]; berubah = True
            if pindah:
                d.setdefault("cek", []).append(pindah)
        if berubah:            # simpan hanya bila ada butir yang berubah (mtime tetap jujur)
            simpan(d)
