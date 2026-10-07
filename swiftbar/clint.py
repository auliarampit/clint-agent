#!/usr/bin/env -S PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin python3
# <swiftbar.title>clint</swiftbar.title>
# <swiftbar.type>streamable</swiftbar.type>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideSwiftBar>true</swiftbar.hideSwiftBar>
"""Menu bar clint (SwiftBar, streamable). Membaca file lokal saja, tanpa jaringan dan tanpa token:
~/Library/Logs/clint/terakhir.json (laporan), kerja.json (kemajuan jalankan), ~/.config/clint/sesi/
(sesi Claude Code). Saat agent bekerja, cincin avatar berputar."""
import base64, datetime, io, json, os, subprocess, sys, time

HOME = os.path.expanduser("~")
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG = os.path.join(HOME, "Library/Logs/clint")
CFG = os.path.join(HOME, ".config/clint")
AKSI = os.path.join(ROOT, "scripts/clint-aksi.sh")
ORANYE, HIJAU, MERAH, KUNING, ABU = "#F0954A", "#3DBB7E", "#E55B5B", "#D9A93A", "#8A94A3"


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


def bersih(t, n=70):
    t = str(t or "").replace("|", "/").replace("\n", " ").replace('"', "'")
    return t if len(t) <= n else t[: n - 1] + "…"


def aksi(nama, *args, refresh=False):
    s = f'bash="{AKSI}" param1={nama}'
    for i, a in enumerate(args, start=2):
        s += f' param{i}="{bersih(a, 300)}"'
    return s + " terminal=false" + (" refresh=true" if refresh else "")


def sapa():
    j = datetime.datetime.now().hour
    return "Selamat pagi" if j < 11 else "Selamat siang" if j < 15 else "Selamat sore" if j < 18 else "Selamat malam"


def durasi(dt):
    m = int(dt // 60)
    return "baru saja" if m < 1 else f"{m} mnt" if m < 60 else f"{m // 60} j {m % 60} mnt"


def nama_proyek(d):
    base, induk = os.path.basename(d), os.path.basename(os.path.dirname(d))
    return f"{induk} · {base}" if len(base) < 12 and induk not in ("Desktop", "Documents", HOME) else base


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
            waktu = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%H.%M")
        except Exception:
            lap = None
    kerja = None
    for fn in ("kerja.json", "kerja.txt"):
        k = os.path.join(LOG, fn)
        if os.path.exists(k) and time.time() - os.path.getmtime(k) < 3 * 3600:
            try:
                kerja = json.load(open(k, encoding="utf-8")) if fn.endswith(".json") else \
                    dict(zip(("label", "tahap", "catatan"), open(k, encoding="utf-8").read().splitlines()))
            except Exception:
                kerja = None
            break
    sesi, sd = [], os.path.join(CFG, "sesi")
    for fn in (os.listdir(sd) if os.path.isdir(sd) else []):
        try:
            f = os.path.join(sd, fn); x = json.load(open(f, encoding="utf-8")); umur = time.time() - os.path.getmtime(f)
        except Exception:
            continue
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
        if (st in ("bekerja", "latar") and umur < 3 * 3600) or (st == "menunggu" and umur < 3600) \
                or (st in ("selesai", "diam") and umur < 1800 if st == "diam" else st == "selesai" and umur < 600):
            x["umur"] = umur; sesi.append(x)
    sesi.sort(key=lambda x: x.get("mulai", 0))
    return lap, waktu, kerja, sesi


def render():
    """Kembalikan (bekerja?, teks menu tanpa baris judul, judul (label, warna))."""
    lap, waktu, kerja, sesi = baca()
    L = lambda key: (lap or {}).get(key) or []
    gagal, kerjakan, cek, tunggu = L("gagal"), L("kerjakan"), L("cek"), L("tunggu")
    menunggu = len(gagal) + len(kerjakan) + len(cek)
    aktif = [x for x in sesi if x["status"] in ("bekerja", "latar")]
    bekerja = bool(kerja or aktif)
    DIR = {p.get("nama"): p.get("dir") for p in L("proyek") if p.get("dir")}
    out = []; o = out.append
    ava = b64(os.path.join(CFG, "ikon.png"))
    ava_img = f"image={ava} width=34 height=34" if ava else "sfimage=person.crop.circle"
    sesi_utama = (aktif or sesi or [{}])[0].get("cwd", "")

    # ---- kepala ----
    if bekerja:
        judul = (kerja or {}).get("judul") or (aktif[0].get("tugas") if aktif else "") or "Agent bekerja"
        mulai = (kerja or {}).get("mulai") or (datetime.datetime.fromtimestamp(aktif[0]["mulai"]).strftime("%H.%M") if aktif and aktif[0].get("mulai") else "")
        o(f"Sedang bekerja | {ava_img} size=15 font=HelveticaNeue-Bold {aksi('vscode', sesi_utama)}")
        o(f"{bersih(judul, 48)}{' · mulai ' + mulai if mulai else ''} | size=12 color={ABU}")
        badge = ((kerja or {}).get("label") or (f"{len(aktif)} sesi" if len(aktif) > 1 else "bekerja"), ORANYE)
    elif gagal:
        o(f"Ada yang gagal | {ava_img} size=15 font=HelveticaNeue-Bold {aksi('laporan')}")
        o(f"{bersih(gagal[0].get('teks'), 50)} | size=12 color={ABU}")
        badge = ("!", MERAH)
    else:
        o(f"{sapa()} | {ava_img} size=15 font=HelveticaNeue-Bold {aksi('laporan')}")
        if lap is None:
            o(f"Belum ada laporan | size=12 color={ABU}"); badge = ("", None)
        else:
            ket = f"{menunggu} hal menunggu" if menunggu else "Semua aman"
            o(f"{ket} · cek terakhir {waktu} | size=12 color={ABU}")
            badge = (str(menunggu), ORANYE) if menunggu else ("✓", HIJAU)
    o("---")

    # ---- agent sedang bekerja ----
    if bekerja:
        o(f"Agent sedang bekerja | size=12 color={ABU}")
        if kerja:
            pr, total = kerja.get("pr"), kerja.get("total")
            utama = f"PR-{pr} dari {total}" if pr and total else (kerja.get("label") or "")
            o(f"{bersih(utama + (' · ' + kerja['tahap'] if kerja.get('tahap') else ''), 60)} | size=13 font=HelveticaNeue-Medium {aksi('vscode', sesi_utama)}")
            if pr and total:
                isi = round(26 * (int(pr) - 0.5) / int(total))
                o(f"{'━' * isi}{'─' * (26 - isi)} | size=12 font=Menlo {aksi('vscode', sesi_utama)}")
            if kerja.get("catatan"):
                o(f"{bersih(kerja['catatan'], 60)} | size=12 color={ABU}")
        for x in sesi:
            st = x["status"]
            warna, kata = {"bekerja": (ORANYE, "bekerja"), "latar": (ORANYE, "di latar"),
                           "menunggu": (KUNING, "menunggu Anda"), "selesai": (HIJAU, "selesai"),
                           "diam": (ABU, "tanpa aktivitas")}[st]
            lama = durasi(x["diam"]) if st == "diam" else durasi(time.time() - x.get("mulai", time.time())) \
                if st != "selesai" else durasi(x["umur"]) + " lalu"
            cwd = x.get("cwd", "")
            o(f"{nama_proyek(cwd)} — {kata} · {lama} | {titik(warna)} {aksi('vscode', cwd)}")
            ag = sorted(set(a.split(":")[-1] for a in (x.get("agents") or {}).values()))
            if ag:
                o(f"--Agent: {bersih(', '.join(ag), 80)}")
            if x.get("tugas"):
                o(f"--Tugas: {bersih(x['tugas'], 80)} | color={ABU}")
            o(f"--Buka di VS Code | {aksi('vscode', cwd)}")
        o(f"Lihat sesi di Claude Code | {aksi('vscode', sesi_utama)}")
        o("---")
    elif sesi:  # tidak bekerja, tapi ada sesi menunggu/baru selesai
        for x in sesi:
            warna, kata = {"menunggu": (KUNING, "menunggu Anda"), "selesai": (HIJAU, "baru selesai"),
                           "diam": (ABU, "tanpa aktivitas")}.get(x["status"], (ABU, x["status"]))
            o(f"{nama_proyek(x.get('cwd', ''))} — {kata} | {titik(warna)} {aksi('vscode', x.get('cwd', ''))}")
        o("---")

    # ---- hal yang menunggu ----
    def butir(x, warna, pre=""):
        o(f"{pre}{bersih(x.get('teks'), 58)} | {titik(warna)}")
        o(f"{pre}--{bersih(x.get('proyek'))} · {bersih(x.get('sumber'))} | color={ABU}")
        if x.get("perintah"):
            o(f"{pre}--Salin perintah | {aksi('salin', x['perintah'], x.get('proyek'))} sfimage=doc.on.doc")
        if x.get("url"):
            o(f"{pre}--Buka MR di browser | {aksi('buka', x['url'])} sfimage=safari")
        if DIR.get(x.get("proyek")):
            o(f"{pre}--Buka project di VS Code | {aksi('vscode', DIR[x['proyek']])} sfimage=chevron.left.forwardslash.chevron.right")
        o(f"{pre}--Tandai selesai | {aksi('selesai', x.get('teks'), refresh=True)} sfimage=checkmark")

    grup = (("Perlu perhatian", gagal, MERAH), ("Perlu dikerjakan", kerjakan, ORANYE), ("Menunggu review Anda", cek, KUNING))
    if bekerja and menunggu:   # saat bekerja menu fokus ke kemajuan; tugas diringkas
        o(f"Hal yang menunggu ({menunggu}) | sfimage=tray.full")
        for judul, xs, warna in grup:
            for x in xs[:6]:
                butir(x, warna, pre="--")
        o("---")
    elif not bekerja:
        for judul, xs, warna in grup:
            if xs:
                o(f"{judul} | size=12 color={ABU}")
                for x in xs[:6]:
                    butir(x, warna)
                o("---")
        if lap is not None and not menunggu:
            o(f"Tidak ada yang perlu ditindaklanjuti. | color={ABU}")
            o("---")

    # ---- tombol cepat ----
    o(f"Buka laporan terakhir | {aksi('laporan')} sfimage=doc.text")
    try:
        aktif_p = [x for x in subprocess.run(["bash", os.path.join(ROOT, "scripts/proyek-aktif.sh"), "3"],
                                             capture_output=True, text=True, timeout=10).stdout.split("\n") if x.strip()]
    except Exception:
        aktif_p = []
    o(f"Cek semua project ({len(aktif_p)} aktif) | {aksi('cek-semua', refresh=True)} sfimage=arrow.clockwise")
    o("Cek project | sfimage=folder")
    for d in aktif_p:
        o(f"--{nama_proyek(d)} | {aksi('cek', d, refresh=True)}")
    o(f"Halo Clint (perintah suara) | {aksi('halo')} sfimage=mic")
    o("---")
    diam, bisu = os.path.exists(os.path.join(CFG, "diam")), os.path.exists(os.path.join(CFG, "bisu-sampai"))
    o("Pengaturan | sfimage=gearshape")
    o(f"--Suara: {'mati' if diam else 'aktif ✓'} | {aksi('suara')}")
    o(f"--Sapaan pagi: 08.00, Sen–Jum | {aksi('sapaan')}")
    o(f"--{'Nyalakan kabar lagi' if bisu else 'Bisukan sampai besok'} | {aksi('bunyikan' if bisu else 'bisu')}")

    # Status MR dicek tiap 15 menit di latar (glab/gh, tanpa token).
    cap = os.path.join(CFG, "mr-dicek")
    if lap is not None and (not os.path.exists(cap) or time.time() - os.path.getmtime(cap) > 900):
        open(cap, "w").close()
        subprocess.Popen(["python3", os.path.join(ROOT, "scripts/laporan-ubah.py"), "periksa-mr"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return bekerja, "\n".join(out), badge


def judul(badge, frame=None):
    label, warna = badge
    img = frame or b64(os.path.join(CFG, "ikon.png"))
    gambar = f"image={img} width=18 height=18" if img else "sfimage=person.crop.circle"
    return f"{label} | {gambar}"   # warna teks mengikuti sistem (putih di menu bar gelap)


def tanda():
    """Sidik perubahan file sumber; menu dirender ulang hanya bila berubah (atau tiap 30 detik)."""
    fs = [os.path.join(LOG, f) for f in ("terakhir.json", "kerja.json", "kerja.txt")] + \
         [os.path.join(CFG, f) for f in ("diam", "bisu-sampai")]
    sd = os.path.join(CFG, "sesi")
    if os.path.isdir(sd):
        fs += [os.path.join(sd, f) for f in os.listdir(sd)]
    return tuple((f, os.path.getmtime(f)) for f in fs if os.path.exists(f))


frames = [b64(os.path.join(CFG, "putar", f"{i}.png")) for i in range(8)]
frames = frames if all(frames) else None
if "--sekali" in sys.argv:            # untuk uji: cetak satu kali lalu keluar
    b, teks, badge = render(); print(judul(badge)); print("---"); print(teks); sys.exit(0)

terakhir_tanda, terakhir_render, keluaran_lalu, i = None, 0, None, 0
while True:
    t = tanda()
    if t != terakhir_tanda or time.time() - terakhir_render > 30:
        bekerja, teks, badge = render(); terakhir_tanda, terakhir_render = t, time.time()
    if bekerja and frames:
        keluaran = judul(badge, frames[i % 8]) + "\n---\n" + teks; i += 1; jeda = 0.35
    else:
        keluaran = judul(badge) + "\n---\n" + teks; jeda = 1
    if keluaran != keluaran_lalu:
        sys.stdout.write("~~~\n" + keluaran + "\n"); sys.stdout.flush(); keluaran_lalu = keluaran
    time.sleep(jeda)
