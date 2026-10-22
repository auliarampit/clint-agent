#!/usr/bin/env python3
"""Ubah laporan terakhir (~/Library/Logs/clint/terakhir.json) tanpa memeriksa ulang. Tanpa token.
  update-report.py merge   <laporan.json>                     # saring, lalu ganti entri project yang ada di file baru saja
  update-report.py saring  <laporan.json>                     # buang butir tanpa bukti / sudah diserahkan (file diubah di tempat)
  update-report.py selesai "<sumber|teks|b64:...>" [--proyek <nama>]
  update-report.py review  "<sumber|teks|b64:...>" "<MR !N>" "<url MR>" [--proyek <nama>]
  update-report.py periksa-mr          # hapus butir MR yang sudah merged/closed (glab/gh)
  update-report.py langkah --dir <repo> [--session <sid>]   # butir siap ketik project ini, tanpa yang diklaim sesi lain"""
import base64, contextlib, fcntl, glob, json, os, re, subprocess, sys, tempfile, time

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


def penanda(sumber):
    """ID dari sumber butir: kode seperti ABC-1/BUG-M-02, dan nomor seperti 'UI-mobile #12' (disertai kata
    di depannya supaya '#12' milik dokumen lain tidak ikut cocok)."""
    ids = [(i, []) for i in re.findall(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+[a-z]?\b", sumber)]
    for kata, no in re.findall(r"([A-Za-z][\w-]*)\s*#(\d+)", sumber):
        ids.append((f"#{no}", [w for w in re.split(r"[-_ ]", kata.lower()) if len(w) >= 2]))
    return ids


def klaim_lain(repo, own):
    """Teks klaim sesi lain yang masih hidup di repo ini (~/Library/Logs/clint/kerja/<sid>.json)."""
    out = []
    for f in glob.glob(os.path.expanduser("~/Library/Logs/clint/kerja/*.json")):
        sid = os.path.basename(f)[:-5]
        if sid == own or time.time() - os.path.getmtime(f) > 3 * 3600 or \
                not os.path.exists(os.path.expanduser(f"~/.config/clint/sesi/{sid}.json")):
            continue
        try:
            k = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if os.path.realpath(k.get("dir") or "") == os.path.realpath(repo):
            out.append(k)
    return out


def diklaim(x, klaim):
    """Butir laporan dipegang sesi lain: perintahnya sama, atau ID sumbernya disebut di klaim (judul, path, ...)."""
    for k in klaim:
        if x.get("perintah") and norm(x["perintah"]) == norm(k.get("perintah")):
            return k
        t = json.dumps(k, ensure_ascii=False).lower()
        for i, konteks in penanda(x.get("sumber") or ""):
            if re.search(rf"(?<![a-z0-9]){re.escape(i.lower())}(?!\d)", t) and all(w in t for w in konteks[:1]):
                return k
    return None


def _tugas_saya():
    import importlib.util
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(
        "tugas_saya", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tugas-saya.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _git(d, *a):
    try:
        return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, timeout=10)
    except Exception:
        return None


def _cocok(sumber, daftar):
    """ID di sumber butir yang ada di daftar ID tugas (termasuk '<file> #n' dari tabel bernomor)."""
    for i, konteks in penanda(sumber):
        for t in daftar:
            tl = t.lower()
            if i.startswith("#"):
                if tl.endswith(" " + i) and (not konteks or any(w in tl for w in konteks)):
                    return t
            elif re.search(rf"(?<![a-z0-9]){re.escape(i.lower())}(?![0-9a-z])", tl):
                return t
    return None


def _bukti(sumber, dirs):
    """Bukti yang bisa diperiksa mesin: MR, commit yang ada, atau file yang ada di salah satu repo."""
    if re.search(r"(^|\s)!\d+\b|https?://", sumber):
        return "MR/tautan"
    for h in re.findall(r"\b[0-9a-f]{7,40}\b", sumber):
        if any((r := _git(d, "cat-file", "-e", f"{h}^{{commit}}")) and r.returncode == 0 for d in dirs):
            return f"commit {h}"
    for p in re.findall(r"[\w./-]+\.[A-Za-z]{1,5}(?=[:\s·,)]|$)", sumber):
        base = os.path.basename(p)
        if any((r := _git(d, "ls-files", f"*{base}")) and r.stdout.strip() for d in dirs):
            return f"file {base}"
    return None


def _disebut(sumber, dirs):
    """Untuk butir tunggu: ID-nya benar-benar tertulis di dokumen repo."""
    kata = [i for i, _ in penanda(sumber) if not i.startswith("#")] or re.findall(r"[A-Z][\w-]{3,}", sumber)[:1]
    return any((r := _git(d, "grep", "-l", "-F", k)) and r.stdout.strip() for k in kata for d in dirs)


def saring(d):
    """Buang butir tanpa bukti atau yang menurut sumber tugas sudah diserahkan/selesai. Dicatat di ditolak.log."""
    ts = _tugas_saya()
    ditolak, info, tugas = [], {}, {}
    for p in d.get("proyek") or []:
        dirp = p.get("dir")
        if not dirp or not os.path.isdir(dirp):
            continue
        dirs = [dirp]
        try:
            cfg = json.load(open(os.path.join(dirp, ".claude/clint.json"), encoding="utf-8"))
            dirs += [os.path.normpath(os.path.join(dirp, r["path"])) for r in cfg.get("relatedRepos") or []
                     if r.get("path")]
        except (OSError, ValueError):
            pass
        t = ts.kumpulkan(dirp)
        info[p.get("nama")] = (dirs, [x["id"] for x in t.get("kerjakan", [])],
                               [x["id"] for k in ("diserahkan", "selesai") for x in t.get(k, [])])
        if t.get("adapter"):
            tugas[p.get("nama")] = t.get("kerjakan", [])

    def alasan_tolak(x, g):
        if x.get("proyek") not in info:
            return None
        dirs, kerja, beres = info[x["proyek"]]
        s = f"{x.get('sumber') or ''} {x.get('perintah') or ''}"
        if (i := _cocok(s, beres)) and not _cocok(s, kerja):
            return f"{i} sudah diserahkan/selesai menurut sumber tugas"
        if _cocok(s, kerja) or _bukti(s, dirs) or (g == "tunggu" and _disebut(s, dirs)):
            return None
        return "tanpa bukti yang bisa diperiksa"

    for g in GRUP:
        tetap = []
        for x in d.get(g) or []:
            a = alasan_tolak(x, g)
            (ditolak.append((g, x, a)) if a else tetap.append(x))
        d[g] = tetap
    lengkapi(d, tugas)
    for b in d.get("berikutnya") or [] if isinstance(d.get("berikutnya"), list) else []:
        if b.get("proyek") in info:
            beres, kerja = info[b["proyek"]][2], info[b["proyek"]][1]
            b["langkah"] = [l for l in b.get("langkah") or [] if not (_cocok(l, beres) and not _cocok(l, kerja))]
    if ditolak:
        with open(os.path.expanduser("~/Library/Logs/clint/ditolak.log"), "a", encoding="utf-8") as fh:
            for g, x, a in ditolak:
                fh.write(f"{time.strftime('%F %T')}\t{x.get('proyek')}\t{g}\t{x.get('sumber')}\t{a}\t{x.get('teks')}\n")
    return d, ditolak


def lengkapi(d, tugas, maks=5):
    """Butir KERJAKAN dari sumber tugas yang tidak ditulis agent dimasukkan, supaya tugas nyata tidak hilang.
    Judul dihitung ulang dari isi akhir, bukan dipercaya dari agent."""
    for proyek, xs in tugas.items():
        ada = " ".join(f"{x.get('sumber') or ''} {x.get('perintah') or ''} {x.get('teks') or ''}"
                       for g in GRUP for x in d.get(g) or []
                       if x.get("proyek") == proyek)
        kurang = [x for x in xs if not _cocok(ada, [x["id"]]) and x["id"].lower() not in ada.lower()]
        boleh = max(0, maks - (len(xs) - len(kurang)))
        for x in kurang[:boleh]:
            d.setdefault("kerjakan", []).append({
                "teks": f"{x['id']}: {x.get('judul') or ''} ({x['status']})".replace(":  (", " (").strip(),
                "proyek": proyek, "sumber": x["id"], "perintah": x.get("perintah", "")})
        r = next((r for r in d.setdefault("rincian", []) if r.get("proyek") == proyek), None)
        if r:
            r["butir"] = [b for b in r.get("butir") or [] if "tugas lain dari sumber tugas" not in b]
        if len(kurang) > boleh:
            if r is None:
                r = {"proyek": proyek, "butir": []}
                d["rincian"].append(r)
            r["butir"].append(f"{len(kurang) - boleh} tugas lain dari sumber tugas: " +
                              ", ".join(x["id"] for x in kurang[boleh:]))
    if tugas and d.get("kerjakan"):
        n = len(d["kerjakan"])
        d["judul"] = d["kalimat"] = f"{n} tugas siap dikerjakan."
        d["lead"] = ", ".join(f"{p}: {sum(x.get('proyek') == p for x in d['kerjakan'])}"
                              for p in dict.fromkeys(x.get("proyek") for x in d["kerjakan"]))


def judul_kosong(d):
    if not any(d.get(g) for g in GRUP):
        d["judul"] = d["kalimat"] = "Tidak ada tugas lagi."
        d["lead"] = ""
    return d


def argumen():
    a, proyek = sys.argv[2:], None
    if "--proyek" in a:
        i = a.index("--proyek")
        proyek = a[i + 1] if i + 1 < len(a) else None
        a = a[:i] + a[i + 2:]
    return a, proyek


aksi = sys.argv[1] if len(sys.argv) > 1 else ""
if aksi == "saring":
    f = sys.argv[2]
    d, ditolak = saring(json.load(open(f, encoding="utf-8")))
    judul_kosong(d)
    json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for g, x, a in ditolak:
        print(f"ditolak\t{x.get('proyek')}\t{g}\t{x.get('sumber')}\t{a}")
    sys.exit(0)

if aksi == "merge":
    baru, _ = saring(json.load(open(sys.argv[2], encoding="utf-8")))
    with kunci():
        d = judul_kosong(gabung(baca(), baru))
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
    import copy, datetime
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
        """MR/PR yang masih open, atau dibuat/di-merge setelah laporan dibuat, sekali ambil per project (tanpa token)."""
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
        _mr[dirp] = [x for x in xs if x["state"] in ("opened", "open")
                     or (waktu(x["merged_at"]) or waktu(x["created_at"]) or dibuat) > dibuat]
        return _mr[dirp]

    def cocok(mr, ident, konteks):
        t = mr["teks"].upper()
        if ident.startswith("#"):
            no = ident[1:]
            kata = [re.escape(k.upper()) for k in konteks[:1]]
            ada = re.search(rf"(?<![\w-])(?:#|(?:UI|BUTIR|NO|NOMOR|FEEDBACK|{'|'.join(kata) or 'UI'})[- ]#?){no}\b", t)
            return bool(ada) and all(re.search(rf"\b{k}\b", t) for k in kata)
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
elif aksi == "langkah":
    a = sys.argv[2:]
    opsi = lambda n: a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else ""
    repo, own = opsi("--dir") or os.getcwd(), opsi("--session")
    d = baca() or {}
    nama = {p.get("nama") for p in d.get("proyek") or [] if os.path.realpath(p.get("dir") or "") == os.path.realpath(repo)}
    klaim = klaim_lain(repo, own)
    for g in ("gagal", "kerjakan"):
        for x in d.get(g) or []:
            if x.get("proyek") not in nama or not x.get("perintah"):
                continue
            k = diklaim(x, klaim)
            print(f"Sedang dikerjakan sesi lain: {x.get('teks')} ({k.get('tahap') or 'berjalan'})" if k
                  else f"[siap] {x['perintah']}")
