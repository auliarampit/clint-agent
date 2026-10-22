#!/usr/bin/env python3
"""Usulkan adapter "tugas" untuk .claude/clint.json dari dokumen yang ada. Tanpa token.
  deteksi-tugas.py <dir-project>                         # usulan + uji coba, tidak menulis apa pun
  deteksi-tugas.py <dir-project> --status "Info=selesai" "Blocked=diserahkan" --tulis
      --status  koreksi pemetaan dari user (nilai=kerjakan|diserahkan|selesai), boleh berulang
      --tulis   tulis usulan (plus koreksi) ke "tugas" di clint.json

Urutan sumber: tabel berkolom PIC yang memuat nama user (sprint tracker/backlog) > tabel tanpa PIC di
docs.feedback (pemilik semua, disaring nama surface pada nama file bila ada) > checklist di docs.plans."""
import collections, glob, importlib.util, json, os, re, sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("ts", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tugas-saya.py"))
ts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ts)

KOL_ID = ["ID", "#", "No", "Kode"]
KOL_PIC = ["PIC", "Owner", "Assignee", "Dev", "Penanggung jawab"]
KOL_JUDUL = ["Title", "Judul", "Bagian", "Kasus", "Feedback", "Nama", "Item"]
KELAS = ("kerjakan", "diserahkan", "selesai")


def tabel(f):
    """(header, baris[]) untuk setiap tabel markdown di file."""
    out, header, isi, prev = [], None, [], ""
    for b in open(f, encoding="utf-8", errors="replace").read().splitlines() + [""]:
        if b.startswith("|") and re.match(r"^\|[\s:|-]+\|?\s*$", b):
            header, isi = (ts.sel(prev), []) if prev.startswith("|") else (None, [])
        elif b.startswith("|") and header:
            isi.append(ts.sel(b))
        elif not b.startswith("|") and header:
            out.append((header, isi))
            header = None
        prev = b
    return out


def kunci_status(v):
    v = ts.norm(v)
    return re.split(r"\s*[(,;:.]|\s+[—–-]\s+", v)[0][:40] if v else ""


def dari_file(files, user, perlu_pic):
    """Kolom yang dipakai + hitungan nilai status, dari tabel ber-ID dan ber-Status."""
    nilai, kolom, cocok = collections.Counter(), {}, set()
    for f in files:
        for header, isi in tabel(f):
            i_id, i_st = ts.cari_kolom(header, KOL_ID), [i for i, h in enumerate(header) if "status" in ts.norm(h)]
            i_pic = ts.cari_kolom(header, KOL_PIC)
            if not i_id or not i_st or (perlu_pic and not i_pic):
                continue
            for c in isi:
                if perlu_pic and not any(n in (c[i_pic[0]] if i_pic[0] < len(c) else "").lower() for n in user):
                    continue
                cocok.add(f)
                for i in i_st:
                    if i < len(c) and kunci_status(c[i]):
                        nilai[kunci_status(c[i])] += 1
            kolom.setdefault("id", []).extend(h for h in (header[i] for i in i_id) if h not in kolom.get("id", []))
            kolom.setdefault("status", []).extend(h for h in (header[i] for i in i_st) if h not in kolom.get("status", []))
            if i_pic:
                kolom["pic"] = header[i_pic[0]]
            j = ts.cari_kolom(header, KOL_JUDUL)
            if j and header[j[0]] not in kolom.setdefault("judul", []):
                kolom["judul"].append(header[j[0]])
    return kolom, nilai, sorted(cocok)


def pola_glob(dirp, files):
    """Glob relatif untuk sekumpulan file: angka di nama file jadi *, dan 'aktif' bila file bertanda status."""
    rel = sorted({os.path.relpath(f, dirp) for f in files})
    seri = [r for r in rel if re.search(r"\d", os.path.basename(r))]
    if len(seri) > 1:
        rel = seri
    pola = sorted({re.sub(r"\d+", "*", r) for r in rel})
    aktif = len(rel) > 1 and any(
        re.search(r"^status:\s*\w+", open(os.path.join(dirp, r), encoding="utf-8", errors="replace").read(3000), re.M)
        for r in rel)
    return (pola[0] if len(pola) == 1 else pola), aktif, [os.path.join(dirp, r) for r in rel]


def petakan(nilai, koreksi):
    """Pemetaan status berisi kata kunci saja (mis. 'fixed', bukan 'fixed 20 okt 2026')."""
    peta, tak = {k: [] for k in KELAS}, []
    for v, n in nilai.most_common():
        if v in koreksi:
            k, kw = koreksi[v], v
        else:
            k, kw = ts.kelas(v, ts.PEMETAAN_BAWAAN), ts.kata_kunci(v, ts.PEMETAAN_BAWAAN)
        if not k:
            tak.append((v, n))
        elif kw not in peta[k]:
            peta[k].append(kw)
    return peta, tak


def usul(dirp, koreksi):
    cfg = json.load(open(os.path.join(dirp, ".claude/clint.json"), encoding="utf-8"))
    docs, user = cfg.get("docs", {}), ts.nama_user()
    path = lambda k: os.path.normpath(os.path.join(dirp, docs[k])) if docs.get(k) not in (None, "", "TIDAK ADA") else None
    md = lambda p: sorted(glob.glob(os.path.join(p, "**/*.md"), recursive=True)) if p and os.path.isdir(p) else \
        ([p] if p and p.endswith(".md") and os.path.exists(p) else [])

    pic = md(path("pic"))
    if pic and user:
        kolom, nilai, files = dari_file(pic, user, True)
        if files:
            pola, aktif, dipakai = pola_glob(dirp, files)
            if aktif:
                dipakai = ts.pilih_file(dirp, {"file": pola, "pilih": "aktif"})
            kolom, nilai, _ = dari_file(dipakai, user, True)
            peta, tak = petakan(nilai, koreksi)
            src = {"jenis": "tabel", "file": pola, "kolom": kolom, "status": peta}
            if aktif:
                src["pilih"] = "aktif"
            return [src], tak, "tabel berkolom PIC dengan nama Anda"

    fb = md(path("feedback"))
    if fb:
        nama_sf = [s.get("name", "").lower() for s in cfg.get("surfaces", []) if s.get("name")]
        per_sf = [f for f in fb if any(n and n in os.path.basename(f).lower() for n in nama_sf)]
        kolom, nilai, files = dari_file(per_sf or fb, user, False)
        if files:
            base = os.path.relpath(path("feedback"), dirp)
            pola = [f"{base}/**/*{n}*.md" for n in nama_sf if any(n in os.path.basename(f).lower() for f in files)] \
                if per_sf else f"{base}/**/*.md"
            peta, tak = petakan(nilai, koreksi)
            return [{"jenis": "tabel", "file": pola[0] if isinstance(pola, list) and len(pola) == 1 else pola,
                     "pemilik": "semua", "kolom": kolom, "status": peta}], tak, \
                "tabel feedback tanpa PIC" + (", disaring nama surface" if per_sf else "")

    plans = path("plans")
    ck = [f for f in md(plans) if re.search(r"^\s*- \[[ xX]\]", open(f, encoding="utf-8", errors="replace").read(), re.M)]
    if ck:
        rel = sorted({os.path.relpath(f, dirp) for f in ck})
        awal = os.path.commonprefix([os.path.basename(r) for r in rel])
        m = re.match(r"[A-Za-z]+-", awal)
        src = {"jenis": "checklist", "file": f"{os.path.relpath(plans, dirp)}/{m.group(0) if m else ''}*.md",
               "pemilik": "semua"}
        if m:
            src["idPola"] = re.escape(m.group(0)) + "[A-Z0-9]+"
        return [src], [], "checklist di rencana"
    return [], [], "tidak ditemukan tabel ber-ID+Status atau checklist"


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    dirp = os.path.abspath(a[0])
    koreksi = {}
    if "--status" in a:
        for x in a[a.index("--status") + 1:]:
            if x.startswith("--"):
                break
            v, _, k = x.rpartition("=")
            if k not in KELAS:
                sys.exit(f"kelas tidak dikenal: {x} (pakai kerjakan|diserahkan|selesai)")
            koreksi[kunci_status(v)] = k
    tugas, tak, alasan = usul(dirp, koreksi)
    if not tugas:
        print(f"usulan=tidak ada ({alasan}). Project ini tidak punya sumber tugas yang bisa dibaca; biarkan tanpa \"tugas\".")
        return
    print(f"dasar: {alasan}")
    print(json.dumps({"tugas": tugas}, ensure_ascii=False, indent=2))
    if tak:
        print("STATUS BELUM DIPETAKAN (tanyakan ke user, lalu ulangi dengan --status \"nilai=kelas\"):")
        for v, n in tak:
            print(f"  {v!r} ({n} baris)")
    r = ts.kumpulkan(dirp, tugas)
    print(f"uji coba: kerjakan {len(r['kerjakan'])}, diserahkan {len(r['diserahkan'])}, selesai {len(r['selesai'])}, "
          f"tidak dikenal {len(r['tidak_dikenal'])}")
    for x in r["kerjakan"][:5]:
        print(f"  contoh kerjakan: {x['id']} | {x.get('judul', '')[:60]} | {x['status']}")
    if "--tulis" in a:
        p = os.path.join(dirp, ".claude/clint.json")
        cfg = json.load(open(p, encoding="utf-8"))
        cfg["tugas"] = tugas
        json.dump(cfg, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(p, "a").write("\n")
        print(f"ditulis ke {p}")


main()
