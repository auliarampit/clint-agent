#!/usr/bin/env python3
"""Tugas user yang terbukti, dari sumber tugas yang dideklarasikan di .claude/clint.json ("tugas"). Tanpa token.
  tugas-saya.py <dir-project> [--json]

Jenis sumber:
  tabel      tabel markdown; kolom dicari dari nama header, status dipetakan lewat "status"; "idPola" (opsional)
             hanya membaca baris ber-ID cocok, untuk file bersama lintas surface (mis. M-1, W-1, A-1 dalam satu file)
  checklist  baris "- [ ]" / "- [x]"; diringkas per file (jumlah terbuka + butir terbuka pertama)
  jadwal     tabel jadwal sprint (rentang tanggal + daftar modul); modul surface ini di sprint yang sedang
             berjalan dicocokkan dengan rencana di "rencana": belum ada rencana = kerjakan, sisa PR = kerjakan
Tanpa "tugas" di clint.json: tidak ada butir tugas (bukan ditebak dari isi dokumen)."""
import datetime, glob, json, os, re, subprocess, sys

PEMETAAN_BAWAAN = {
    "kerjakan": ["⬜", "🔄", "🐞", "open", "belum", "sebagian", "reopen", "reopened", "in progress", "to do", "todo"],
    "diserahkan": ["🧪", "on qa", "fixed", "diperbaiki"],
    "selesai": ["✅", "done", "closed", "selesai", "merged", "passed", "diverifikasi", "—", "-", "n/a",
                "invalid", "rejected", "ditolak", "cancelled", "dibatalkan"],
}


def norm(s):
    s = re.sub(r"[*_`]", "", s or "").strip().lower()
    return re.sub(r"\s+", " ", s)


def nama_user():
    try:
        n = json.load(open(os.path.expanduser("~/.config/clint/user.json"), encoding="utf-8")).get("name")
    except (OSError, ValueError):
        return []
    return [x.lower() for x in (n if isinstance(n, list) else [n]) if x]


def pilih_file(dirp, src):
    pola = src["file"] if isinstance(src["file"], list) else [src["file"]]
    fs = sorted({f for p in pola for f in glob.glob(os.path.join(dirp, p), recursive=True) if f.endswith(".md")})
    kunci_v = lambda f: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", os.path.basename(f))]
    if src.get("pilih") == "aktif" and fs:
        aktif = [f for f in fs if re.search(r"^status:\s*(active|aktif)\b", open(f, encoding="utf-8").read(3000),
                                             re.I | re.M)]
        return [max(aktif or fs, key=kunci_v)]
    return fs


def kelas(nilai, peta):
    v = norm(nilai)
    kata = sorted(((norm(x), k) for k in ("kerjakan", "diserahkan", "selesai") for x in peta.get(k, [])),
                  key=lambda t: -len(t[0]))
    for kw, k in kata:
        if v == kw or re.match(rf"{re.escape(kw)}(?=[\s(,;:.])", v):
            return k
    return None


def kata_kunci(nilai, peta):
    """Kata kunci status yang cocok dengan nilai (yang terpanjang), atau None."""
    v = norm(nilai)
    for kw in sorted({norm(x) for k in peta for x in peta[k]}, key=len, reverse=True):
        if v == kw or re.match(rf"{re.escape(kw)}(?=[\s(,;:.])", v):
            return kw
    return None


def sel(baris):
    return [c.strip() for c in baris.strip().strip("|").split("|")]


def cari_kolom(header, nama):
    nama = [norm(n) for n in (nama if isinstance(nama, list) else [nama])]
    return [i for i, h in enumerate(header) if norm(h) in nama]


def baca_tabel(f, src, user, peta):
    kol, hasil, header = src.get("kolom", {}), [], None
    stem = os.path.splitext(os.path.basename(f))[0]
    baris = open(f, encoding="utf-8").read().splitlines()
    for no, b in enumerate(baris):
        if not b.startswith("|"):
            header = None
            continue
        if re.match(r"^\|[\s:|-]+\|?\s*$", b):
            header = sel(baris[no - 1]) if no else None
            continue
        if header is None:
            continue
        c = sel(b)
        i_id, i_st = cari_kolom(header, kol.get("id", ["ID"])), cari_kolom(header, kol.get("status", ["Status"]))
        if not i_id or not i_st:
            continue
        i_pic, i_jd = cari_kolom(header, kol.get("pic", ["PIC"])), cari_kolom(header, kol.get("judul", ["Title", "Judul"]))
        get = lambda i: c[i] if i < len(c) else ""
        id_ = get(i_id[0])
        if not id_ or norm(id_) == norm(header[i_id[0]]):
            continue
        if src.get("idPola") and not re.fullmatch(src["idPola"], id_):
            continue
        if re.fullmatch(r"\d+", id_):
            id_ = f"{stem} #{id_}"
        if src.get("pemilik", "pic") == "pic":
            if not i_pic or not any(n in get(i_pic[0]).lower() for n in user):
                continue
        status = {header[i]: get(i) for i in i_st if get(i)}
        kls = [kelas(v, peta) for v in status.values()]
        if "kerjakan" in kls:
            k = "kerjakan"
        elif "diserahkan" in kls:
            k = "diserahkan"
        elif kls and all(x == "selesai" for x in kls):
            k = "selesai"
        else:
            k = "tidak_dikenal"
        hasil.append({"id": id_, "judul": get(i_jd[0])[:90] if i_jd else "", "kelas": k,
                      "status": " ".join(f"{h}:{v}" for h, v in status.items()), "file": f, "baris": no + 1})
    return hasil


def baca_checklist(f, src):
    terbuka, selesai, pertama, judul = 0, 0, None, ""
    for no, b in enumerate(open(f, encoding="utf-8").read().splitlines()):
        if b.startswith("#"):
            judul = b.lstrip("#").strip()
        m = re.match(r"^\s*- \[( |x|X)\]\s*(.*)", b)
        if not m:
            continue
        if m.group(1) == " ":
            terbuka += 1
            pertama = pertama or (no + 1, judul, m.group(2))
        else:
            selesai += 1
    if not terbuka and not selesai:
        return []
    m = re.search(src.get("idPola") or r"^[^.]+", os.path.basename(f))
    id_ = m.group(0) if m else os.path.basename(f)
    if not terbuka:
        return [{"id": id_, "kelas": "selesai", "file": f}]
    return [{"id": id_, "judul": f"{pertama[1]}: {pertama[2]}"[:120], "kelas": "kerjakan",
             "status": f"{terbuka} terbuka / {terbuka + selesai}", "file": f, "baris": pertama[0]}]


BULAN = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "may": 5, "jun": 6, "jul": 7, "agu": 8, "agt": 8,
         "aug": 8, "sep": 9, "okt": 10, "oct": 10, "nov": 11, "des": 12, "dec": 12}


def rentang(teks):
    """'22 Okt–3 Nov 2026', '8–22 Sep 2026', '4 Nov 2026', '2026-10-06 → 2026-10-19' → (awal, akhir)."""
    iso = re.findall(r"\d{4}-\d{2}-\d{2}", teks)
    if iso:
        d = [datetime.date.fromisoformat(x) for x in iso]
        return d[0], d[-1]
    m = re.search(r"(\d{1,2})(?:\s+([A-Za-z]{3,}))?(?:\s+(\d{4}))?\s*[–-]\s*(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})", teks)
    try:
        if m:
            b2, t2 = BULAN[m.group(5)[:3].lower()], int(m.group(6))
            b1 = BULAN[m.group(2)[:3].lower()] if m.group(2) else b2
            return (datetime.date(int(m.group(3) or t2), b1, int(m.group(1))),
                    datetime.date(t2, b2, int(m.group(4))))
        m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})", teks)
        if m:
            d = datetime.date(int(m.group(3)), BULAN[m.group(2)[:3].lower()], int(m.group(1)))
            return d, d
    except (KeyError, ValueError):
        pass
    return None


def status_rencana(dirp, plan):
    try:
        out = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan-status.py"),
                              plan, "--json"], cwd=dirp, capture_output=True, text=True, timeout=60).stdout
        return [x.get("state") for x in json.loads(out)["plans"][0]["prs"]]
    except (OSError, ValueError, KeyError, IndexError, subprocess.TimeoutExpired):
        return []


def baca_jadwal(f, src, dirp, hari=None):
    hari = hari or datetime.date.today()
    kol, awalan = src.get("kolom", {}), src.get("idAwalan", "")
    pola = re.compile(src["modulPola"])
    rencana = os.path.join(dirp, src.get("rencana", "docs/plans"))
    hasil, header, baris = [], None, open(f, encoding="utf-8").read().splitlines()
    for no, b in enumerate(baris):
        if not b.startswith("|"):
            header = None
            continue
        if re.match(r"^\|[\s:|-]+\|?\s*$", b):
            header = sel(baris[no - 1]) if no else None
            continue
        if header is None:
            continue
        c = sel(b)
        i_tg = cari_kolom(header, kol.get("tanggal", ["Target", "Tanggal", "Date", "Window"]))
        i_md = cari_kolom(header, kol.get("modul", ["Scope summary", "Scope", "Isi", "Modul"]))
        if not i_tg or not i_md or i_tg[0] >= len(c) or i_md[0] >= len(c):
            continue
        r = rentang(c[i_tg[0]])
        if not r or not r[0] <= hari <= r[1]:
            continue
        for m in pola.findall(c[i_md[0]]):
            id_ = m if m.startswith(awalan) else awalan + m
            if any(x["id"] == id_ for x in hasil):
                continue
            plan = sorted(p for p in glob.glob(os.path.join(rencana, "*.md"))
                          if os.path.basename(p).lower().startswith(id_.lower() + "-"))
            x = {"id": id_, "judul": c[0], "file": f, "baris": no + 1}
            if not plan:
                x.update(kelas="kerjakan", status="belum direncanakan", perintah=f"/clint:develop {id_}")
            else:
                st, rel = status_rencana(dirp, plan[0]), os.path.relpath(plan[0], dirp)
                sisa = [s for s in st if s != "done"]
                x.update(file=plan[0], baris=1, status=f"rencana {len(st) - len(sisa)}/{len(st)} PR selesai",
                         perintah=f"/clint:develop {rel}")
                x["kelas"] = ("tidak_dikenal" if not st else "selesai" if not sisa
                              else "diserahkan" if all(s in ("review", "draft") for s in sisa) else "kerjakan")
            hasil.append(x)
    return hasil


def commit_kode(dirp, base, id_):
    if " #" in id_:
        return ""
    out = subprocess.run(["git", "-C", dirp, "log", f"origin/{base}", "-E",
                          f"--grep={re.escape(id_)}([^0-9A-Za-z]|$)", "--format=%h %ad %s",
                          "--date=format:%d/%m"], capture_output=True, text=True).stdout
    kode = [l for l in out.splitlines() if not re.match(r"^\S+ \S+ (docs|Merge)\b", l)]
    return kode[0][:90] if kode else ""


def kumpulkan(dirp, sumber=None):
    try:
        cfg = json.load(open(os.path.join(dirp, ".claude/clint.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {"adapter": False, "alasan": "tidak ada .claude/clint.json"}
    sumber = sumber if sumber is not None else cfg.get("tugas")
    if not sumber:
        return {"adapter": False, "alasan": 'clint.json belum punya "tugas"'}
    user, base = nama_user(), cfg.get("baseBranch", "dev")
    out = {"adapter": True, "kerjakan": [], "diserahkan": [], "selesai": [], "tidak_dikenal": [], "file": []}
    for src in sumber:
        ubah = {k: [norm(x) for x in v] for k, v in src.get("status", {}).items()}
        dipakai = {x for v in ubah.values() for x in v}
        peta = {k: ubah.get(k, []) + [x for x in v if norm(x) not in dipakai] for k, v in PEMETAAN_BAWAAN.items()}
        for f in pilih_file(dirp, src):
            out["file"].append(os.path.relpath(f, dirp))
            jenis = src.get("jenis")
            items = baca_tabel(f, src, user, peta) if jenis == "tabel" else \
                baca_jadwal(f, src, dirp) if jenis == "jadwal" else baca_checklist(f, src)
            for x in items:
                x["file"] = os.path.relpath(x["file"], dirp)
                if x["kelas"] == "kerjakan" and jenis == "tabel":
                    x["commit"] = commit_kode(dirp, base, x["id"])
                x.setdefault("perintah", f"/clint:develop {x['id']} {x.get('judul', '')} ({x['file']})".strip()
                             if jenis == "tabel" else f"/clint:develop {x['file']}")
                out[x["kelas"]].append(x)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    r = kumpulkan(sys.argv[1])
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False))
        sys.exit(0)
    if not r["adapter"]:
        print(f"sumber_tugas=tidak ada ({r['alasan']}): tidak ada butir tugas yang boleh dilaporkan")
        sys.exit(0)
    print(f"sumber_tugas: {', '.join(r['file']) or '(tidak ada file cocok)'}")
    print(f"KERJAKAN {len(r['kerjakan'])} (hanya ini yang boleh dilaporkan sebagai tugas):")
    for x in r["kerjakan"]:
        print(f"  {x['id']} | {x.get('judul', '')} | {x['status']} | {x['file']}:{x['baris']}"
              + (f" | commit kode: {x['commit'] or '-'}" if "commit" in x else ""))
    print(f"DISERAHKAN {len(r['diserahkan'])} (sudah di QA/fixed, jangan dilaporkan): "
          + ", ".join(x["id"] for x in r["diserahkan"]))
    print(f"SELESAI {len(r['selesai'])}")
    if r["tidak_dikenal"]:
        print("STATUS TIDAK DIKENAL (tambahkan ke \"status\" di adapter, jangan ditebak): "
              + ", ".join(f"{x['id']} ({x['status'] or 'kosong'})" for x in r["tidak_dikenal"]))
