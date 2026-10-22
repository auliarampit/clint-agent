#!/usr/bin/env -S PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin python3
# <swiftbar.title>clint</swiftbar.title>
# <swiftbar.type>streamable</swiftbar.type>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideSwiftBar>true</swiftbar.hideSwiftBar>
"""Menu bar clint (SwiftBar, streamable). Membaca file lokal saja, tanpa jaringan dan tanpa token:
~/Library/Logs/clint/terakhir.json (laporan), kerja/<sid>.json (kemajuan develop per sesi), ~/.config/clint/sesi/
(sesi Claude Code). Saat agent bekerja, bilah biru di bawah avatar mengalir."""
import base64, datetime, io, json, os, re, subprocess, sys, time

HOME = os.path.expanduser("~")
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG = os.path.join(HOME, "Library/Logs/clint")
CFG = os.path.join(HOME, ".config/clint")
AKSI = os.path.join(ROOT, "scripts/clint-action.sh")
ORANYE, HIJAU, MERAH, KUNING, ABU, BIRU = "#F0954A", "#3DBB7E", "#E55B5B", "#D9A93A", "#8A94A3", "#6AA8FF"


def b64(path):
    try:
        return base64.b64encode(open(path, "rb").read()).decode()
    except Exception:
        return None


_titik = {}
def titik(warna):
    """Gambar titik berwarna (menu Mac tidak mewarnai simbol secara andal)."""
    if warna not in _titik:
        try:
            from PIL import Image, ImageDraw
            im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse((5, 5, 19, 19), fill=warna)
            buf = io.BytesIO(); im.save(buf, "PNG")
            _titik[warna] = f"image={base64.b64encode(buf.getvalue()).decode()} width=12 height=12"
        except Exception:
            _titik[warna] = "sfimage=circle.fill"
    return _titik[warna]


TAHAP = ("worktree", "kode", "tinjau", "test", "MR")
_bilah = {}
def bilah(langkah):
    """Bilah lima tahap dengan nama tahap di bawahnya: biru = lewat, biru pudar = sedang, abu = belum.
    Nama tahap yang sedang berjalan ikut biru; teks abu terbaca di menu gelap maupun terang."""
    if langkah not in _bilah:
        try:
            from PIL import Image, ImageDraw, ImageFont
            im = Image.new("RGBA", (5 * 68 + 4 * 8, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
            except OSError:
                font = None
            for i in range(5):
                c = (106, 168, 255, 255) if i < langkah else (106, 168, 255, 115) if i == langkah else (138, 148, 163, 90)
                d.rounded_rectangle((i * 76, 0, i * 76 + 67, 7), radius=3, fill=c)
                if font:
                    d.text((i * 76, 16), TAHAP[i], font=font,
                           fill=(106, 168, 255, 255) if i == langkah else (138, 148, 163, 255))
            buf = io.BytesIO(); im.save(buf, "PNG")
            _bilah[langkah] = f"image={base64.b64encode(buf.getvalue()).decode()} width=186 height=20"
        except Exception:
            _bilah[langkah] = ""
    return _bilah[langkah]


def bersih(t, n=70):
    t = str(t or "").replace("|", "/").replace("\n", " ").replace('"', "'")
    return t if len(t) <= n else t[: n - 1] + "…"


def aksi(nama, *args, refresh=False):
    s = f'bash="{AKSI}" param1={nama}'
    for i, a in enumerate(args, start=2):
        s += f' param{i}="{bersih(a, 1000)}"'
    return s + " terminal=false" + (" refresh=true" if refresh else "")


def sapa():
    j = datetime.datetime.now().hour
    return "Selamat pagi" if j < 11 else "Selamat siang" if j < 15 else "Selamat sore" if j < 18 else "Selamat malam"


def durasi(dt):
    m = int(dt // 60)
    return "baru saja" if m < 1 else f"{m} mnt" if m < 60 else f"{m // 60} j {m % 60} mnt"


def nama_proyek(d):
    base, induk = os.path.basename(d), os.path.basename(os.path.dirname(d))
    return f"{induk} · {base}" if len(base) < 12 and induk not in ("Desktop", "Documents", os.path.basename(HOME)) else base


def giliran_selesai(path):
    """True bila baris bermakna terakhir transkrip menunjukkan jawaban sudah tuntas (end_turn atau
    ringkasan hook Stop). Pengaman bila hook status tidak tercatat dengan benar."""
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2); fh.seek(max(0, fh.tell() - 65536))
            baris = fh.read().decode("utf-8", "ignore").splitlines()[1:]
    except (OSError, TypeError):
        return False
    for b in reversed(baris):
        try:
            r = json.loads(b)
        except ValueError:
            continue
        t = r.get("type")
        if t == "system" and r.get("subtype") == "stop_hook_summary":
            return True
        if t == "assistant":
            return (r.get("message") or {}).get("stop_reason") == "end_turn"
        if t == "user":
            return False
    return False


def baca():
    lap, waktu = None, None
    p = os.path.join(LOG, "terakhir.json")
    if os.path.exists(p):
        try:
            lap = json.load(open(p, encoding="utf-8"))
            # Waktu laporan DIBUAT, bukan waktu file terakhir disentuh (pengecekan MR / tandai selesai).
            waktu = kapan(lap.get("_dibuat") or os.path.getmtime(p))
        except Exception:
            lap = None
    return lap, waktu, baca_kerja(), baca_sesi()


def kapan(ts):
    t = datetime.datetime.fromtimestamp(ts)
    selisih = (datetime.date.today() - t.date()).days
    return t.strftime("%H.%M") if selisih == 0 else t.strftime("kemarin %H.%M") if selisih == 1 else t.strftime("%d/%m %H.%M")


def hidup(path):
    """Klaim kerja/<sid>.json hidup bila < 3 jam dan sesinya masih ada; cek-<pid>.json bila prosesnya masih jalan."""
    if time.time() - os.path.getmtime(path) >= 3 * 3600:
        return False
    nama = os.path.basename(path)[:-5]
    if nama.startswith("cek-"):
        try:
            os.kill(int(nama[4:]), 0); return True
        except (ValueError, OSError):
            return False
    return os.path.exists(os.path.join(CFG, "sesi", nama + ".json"))


def baca_kerja():
    """Semua kemajuan kerja yang hidup: klaim per sesi (kerja/<sid>.json) dan cek-<pid>.json."""
    kerja, kd = [], os.path.join(LOG, "kerja")
    fs = [os.path.join(kd, f) for f in sorted(os.listdir(kd)) if f.endswith(".json")] if os.path.isdir(kd) else []
    for k in fs:
        try:
            if hidup(k):
                kerja.append(dict(json.load(open(k, encoding="utf-8")), _sid=os.path.basename(k)[:-5]))
        except Exception:
            pass
    return kerja


tugas_selesai = set()


def baca_sesi():
    sesi, sd = [], os.path.join(CFG, "sesi")
    tugas_selesai.clear()
    for fn in (os.listdir(sd) if os.path.isdir(sd) else []):
        try:
            f = os.path.join(sd, fn); x = json.load(open(f, encoding="utf-8")); umur = time.time() - os.path.getmtime(f)
        except Exception:
            continue
        x["_sid"] = fn[:-5]
        st = x.get("status")
        if st == "latar":               # format lama; kini Stop selalu menulis "selesai"
            st = x["status"] = "selesai"
        if st == "bekerja" and giliran_selesai(x.get("transkrip")):
            st = x["status"] = "selesai"
        if st == "selesai" and x.get("agents") and umur < 1800:
            st = x["status"] = "latar"   # turn selesai, tapi agent latar masih berjalan
        # Esc/interupsi tidak memicu hook Stop: status bisa tertahan "bekerja". Pakai aktivitas terakhir
        # (hook atau transkrip). > 10 mnt tanpa aktivitas dan tanpa agent jalan → dianggap diam.
        if st in ("bekerja", "latar"):
            akt = umur
            try:
                akt = min(akt, time.time() - os.path.getmtime(x.get("transkrip") or ""))
            except OSError:
                pass
            if akt > 600 and not x.get("agents"):
                x["status"], st, x["diam"] = "diam", "diam", akt
        if st == "selesai" and x.get("tugas") and umur < 12 * 3600:
            tugas_selesai.add(x["tugas"])
        if (st in ("bekerja", "latar") and umur < 3 * 3600) or (st == "menunggu" and umur < 3600) \
                or (st in ("selesai", "diam") and umur < 1800 if st == "diam" else st == "selesai" and umur < 600):
            x["umur"] = umur; sesi.append(x)
    sesi.sort(key=lambda x: x.get("mulai", 0))
    return sesi


def proyek_aktif():
    """Hasil active-projects.sh disimpan 5 menit: find di ~/.claude/projects lambat bila dipanggil tiap render."""
    cache = os.path.join(CFG, "proyek-aktif.txt")
    try:
        if time.time() - os.path.getmtime(cache) < 300:
            return [x for x in open(cache, encoding="utf-8").read().split("\n") if x.strip()]
    except OSError:
        pass
    try:
        out = subprocess.run(["bash", os.path.join(ROOT, "scripts/active-projects.sh"), "3"],
                             capture_output=True, text=True, timeout=10).stdout
        open(cache, "w", encoding="utf-8").write(out)
    except Exception:
        out = ""
    return [x for x in out.split("\n") if x.strip()]


def tugas_pendek(t):
    return re.sub(r"^/clint:\w+\s+", "", t or "").strip()


def render():
    """Kembalikan (bekerja?, teks menu tanpa baris judul, judul (label, warna))."""
    lap, waktu, semua_kerja, sesi = baca()
    L = lambda key: (lap or {}).get(key) or []
    gagal, kerjakan = L("gagal"), L("kerjakan")
    klaim = {k["_sid"]: k for k in semua_kerja}
    aktif = [x for x in sesi if x["status"] in ("bekerja", "latar")]
    cek_jalan = [k for k in semua_kerja if k["_sid"].startswith("cek-")]
    bekerja = bool(aktif or cek_jalan)
    # Perintah yang sedang dipegang sesi (tugas yang diketik, atau `perintah` di klaimnya): butir laporan yang sama
    # tampil di baris sesi itu, bukan di "Perlu dikerjakan". Butir yang tugasnya baru selesai diberi tanda ✓.
    dipegang = {p for x in sesi if x["status"] in ("bekerja", "latar", "menunggu")
                for p in (x.get("tugas"), (klaim.get(x["_sid"]) or {}).get("perintah")) if p}
    sama = lambda cmd, ps: bool(cmd) and any(cmd[:90] == p[:90] for p in ps)
    gagal, kerjakan = [[x for x in xs if not sama(x.get("perintah"), dipegang)] for xs in (gagal, kerjakan)]
    # Satu butir paling mendesak per project (yang gagal lebih dulu). Butir review dan rincian lain ada di
    # laporan HTML, jadi menu tidak memuat submenu per butir.
    urgen = {}
    for x in gagal + kerjakan:
        urgen.setdefault(x.get("proyek") or "", x)
    out = []; o = out.append
    sesi_utama = (aktif or sesi or [{}])[0].get("cwd", "")

    # ---- kepala ----
    if bekerja:
        n = len(aktif) + len(cek_jalan)
        o(f"clint · {n} berjalan | size=15 font=HelveticaNeue-Bold {aksi('vscode', sesi_utama)}")
        tahap = next((x["tahap"].split(" · ")[0] for x in aktif if x.get("tahap")), "" if aktif else "cek")
        badge = (f"{n} · {tahap or 'bekerja'}", BIRU)
    elif gagal:
        o(f"Ada yang gagal | size=15 font=HelveticaNeue-Bold {aksi('laporan')}")
        o(f"{bersih(gagal[0].get('teks'), 50)} | size=12 color={ABU}")
        badge = ("!", MERAH)
    else:
        o(f"{sapa()} | size=15 font=HelveticaNeue-Bold {aksi('laporan')}")
        if lap is None:
            o(f"Belum ada laporan | size=12 color={ABU}"); badge = ("", None)
        else:
            o(f"cek terakhir {waktu} | size=12 color={ABU}")
            badge = (str(len(urgen)), ORANYE) if urgen else ("✓", HIJAU)
    o("---")

    # ---- sesi: yang berjalan dengan bilah tahap, sisanya satu baris; klik membuka VS Code ----
    for k in cek_jalan:
        o(f"{bersih(k.get('judul'), 46)} — sejak {k.get('mulai', '')} | {titik(BIRU)} font=HelveticaNeue-Bold")
        if k.get("tahap"):
            o(f"{bersih(k['tahap'], 60)} | size=12 color={ABU}")
    for x in sesi:
        st, cwd, k = x["status"], x.get("cwd", ""), klaim.get(x["_sid"]) or {}
        klik = aksi("vscode", k.get("path") or cwd)
        nama = k.get("judul") or tugas_pendek(x.get("tugas")) or "sesi"
        if st in ("bekerja", "latar"):
            ekor = durasi(time.time() - x.get("mulai", time.time())) if st == "bekerja" else "di latar"
            if k.get("pr") and k.get("total") and k["total"] > 1:
                ekor = f"PR {k['pr']}/{k['total']} · {ekor}"
            o(f"{bersih(nama, 40)} — {ekor} | {titik(BIRU)} font=HelveticaNeue-Bold {klik}")
            if isinstance(x.get("langkah"), int) and bilah(x["langkah"]):
                o(f" | {bilah(x['langkah'])} {klik}")
            ag = ", ".join(sorted(set(a.split(":")[-1] for a in (x.get("agents") or {}).values())))
            o(f"{bersih(' · '.join(p for p in (nama_proyek(cwd), ag or x.get('tahap')) if p), 60)} | size=12 color={ABU} {klik}")
        else:
            warna, ekor = {"menunggu": (KUNING, "perlu jawaban Anda"),
                           "selesai": (HIJAU, f"selesai {durasi(x['umur'])} lalu"),
                           "diam": (ABU, f"diam {durasi(x.get('diam', 0))}")}[st]
            o(f"{'✓ ' if st == 'selesai' else ''}{bersih(f'{nama_proyek(cwd)} · {nama}', 46)} — {ekor} | {titik(warna)} {klik}")
    if sesi or cek_jalan:
        o("---")

    # ---- perlu dikerjakan: satu per project; klik membuka laporan HTML ----
    if urgen:
        o(f"Perlu dikerjakan | size=12 color={ABU}")
        for proyek, x in urgen.items():
            tadi = sama(x.get("perintah"), tugas_selesai)
            warna = HIJAU if tadi else MERAH if x in gagal else ORANYE
            o(f"{'✓ ' if tadi else ''}{bersih(x.get('teks'), 50)} | {titik(warna)} {aksi('laporan')}")
            if proyek:
                o(f"{bersih(proyek, 50)} | size=12 color={ABU} {aksi('laporan')}")
        o("---")
    elif lap is not None and not bekerja:
        o(f"Tidak ada yang perlu ditindaklanjuti. | color={ABU}")
        o("---")

    # ---- tombol cepat ----
    o(f"Buka laporan terakhir | {aksi('laporan')} sfimage=doc.text")
    aktif_p = proyek_aktif()
    o(f"Cek semua project ({len(aktif_p)} aktif) | {aksi('cek-semua', refresh=True)} sfimage=arrow.clockwise")
    o(f"Halo Clint (perintah suara) | {aksi('halo')} sfimage=mic")
    o("Cek project | sfimage=folder")
    for d in aktif_p:
        o(f"--{nama_proyek(d)} | {aksi('cek', d, refresh=True)}")
    o("---")
    diam, bisu = os.path.exists(os.path.join(CFG, "diam")), os.path.exists(os.path.join(CFG, "bisu-sampai"))
    o("Pengaturan | sfimage=gearshape")
    o(f"--Suara: {'mati' if diam else 'aktif ✓'} | {aksi('suara')}")
    sp = sapaan_cfg()
    o(f"--Sapaan pagi: {sp['jam']:02d}.{sp['menit']:02d} Sen–Jum {'✓' if sp['aktif'] else '(mati)'} | {aksi('sapaan-mati' if sp['aktif'] else 'sapaan-nyala')}")
    o(f"--{'Nyalakan kabar lagi' if bisu else 'Bisukan sampai besok'} | {aksi('bunyikan' if bisu else 'bisu')}")
    o(f"--Bersihkan menu (hal menunggu & klaim kerja) | {aksi('bersihkan', refresh=True)} sfimage=trash")

    # Status MR dicek tiap 5 menit di latar dan setiap giliran sesi selesai (hook Stop), lewat glab/gh tanpa token.
    cap = os.path.join(CFG, "mr-dicek")
    if lap is not None and (not os.path.exists(cap) or time.time() - os.path.getmtime(cap) > 300):
        open(cap, "w").close()
        subprocess.Popen(["python3", os.path.join(ROOT, "scripts/update-report.py"), "periksa-mr"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return bekerja, "\n".join(out), badge


def judul(badge, frame=None):
    label, warna = badge
    img = frame or b64(os.path.join(CFG, "ikon.png"))
    gambar = f"image={img} width=18 height=18" if img else "sfimage=person.crop.circle"
    return f"{label} | {gambar}"   # warna teks mengikuti sistem (putih di menu bar gelap)


def tanda():
    """Sidik perubahan file sumber; menu dirender ulang hanya bila berubah (atau tiap 30 detik)."""
    fs = [os.path.join(LOG, "terakhir.json")] + \
         [os.path.join(CFG, f) for f in ("diam", "bisu-sampai")]
    for sd in (os.path.join(CFG, "sesi"), os.path.join(LOG, "kerja")):
        if os.path.isdir(sd):
            fs += [os.path.join(sd, f) for f in os.listdir(sd)]
    return tuple((f, os.path.getmtime(f)) for f in fs if os.path.exists(f))


# Saat bekerja bilah biru di bawah avatar mengalir (bingkai alir/0..11, dibuat scripts/make-icon.py). Konsekuensi
# yang diterima: setiap bingkai mengirim ulang seluruh menu, jadi menu yang sedang dibuka berkedip selama agent bekerja.
bingkai = [f for f in (b64(os.path.join(CFG, "alir", f"{i}.png")) for i in range(12)) if f]


def sapaan_cfg():
    try:
        c = json.load(open(os.path.join(CFG, "sapaan.json"), encoding="utf-8"))
    except Exception:
        c = {}
    return {"aktif": c.get("aktif", True), "jam": int(c.get("jam", 8)), "menit": int(c.get("menit", 0)),
            "sampai": int(c.get("sampai", 13))}


def sapaan_pagi():
    """Jadwal sapaan pagi dijalankan dari sini (SwiftBar punya izin folder Desktop; launchd tidak).
    Senin–Jumat, mulai jam yang diatur sampai sebelum jam `sampai`, sekali per hari. Laptop tidur →
    jalan saat bangun selama masih di rentang itu."""
    c = sapaan_cfg(); now = datetime.datetime.now()
    if not c["aktif"] or now.weekday() > 4 or (now.hour, now.minute) < (c["jam"], c["menit"]) or now.hour >= c["sampai"]:
        return
    tanda_hari = os.path.join(CFG, f"sapaan-{now:%Y-%m-%d}")
    if os.path.exists(tanda_hari):
        return
    for f in os.listdir(CFG):            # bersihkan penanda hari lain
        if f.startswith("sapaan-20") and f != os.path.basename(tanda_hari):
            os.remove(os.path.join(CFG, f))
    open(tanda_hari, "w").close()
    subprocess.Popen(["bash", os.path.join(ROOT, "scripts/morning-greeting.sh")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


if "--sekali" in sys.argv:            # untuk uji: cetak satu kali lalu keluar
    b, teks, badge = render(); print(judul(badge, bingkai[0] if b and bingkai else None)); print("---"); print(teks); sys.exit(0)

terakhir_tanda, terakhir_render, keluaran_lalu, cek_sapaan, langkah = None, 0, None, 0, 0
while True:
    if time.time() - cek_sapaan > 60:
        cek_sapaan = time.time()
        try:
            sapaan_pagi()
        except Exception:
            pass
    t = tanda()
    if t != terakhir_tanda or time.time() - terakhir_render > 30:
        bekerja, teks, badge = render(); terakhir_tanda, terakhir_render = t, time.time()
    alir = bekerja and bingkai
    keluaran = judul(badge, bingkai[langkah % len(bingkai)] if alir else None) + "\n---\n" + teks
    if keluaran != keluaran_lalu:          # kirim hanya bila berubah: saat diam menu yang terbuka tidak berkedip
        sys.stdout.write("~~~\n" + keluaran + "\n"); sys.stdout.flush(); keluaran_lalu = keluaran
    langkah += 1
    time.sleep(0.15 if alir else 1)
