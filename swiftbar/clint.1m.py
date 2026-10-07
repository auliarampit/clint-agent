#!/usr/bin/env -S PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin python3
# <swiftbar.title>clint</swiftbar.title>
# <swiftbar.desc>Status clint: hal yang menunggu, agent yang bekerja, tombol cepat.</swiftbar.desc>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
"""Plugin SwiftBar untuk clint. Membaca file lokal saja (tanpa jaringan, tanpa token):
laporan terakhir ~/Library/Logs/clint/terakhir.json dan status kerja kerja.txt."""
import base64, datetime, json, os, subprocess, time

HOME = os.path.expanduser("~")
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG = os.path.join(HOME, "Library/Logs/clint")
CFG = os.path.join(HOME, ".config/clint")
AKSI = os.path.join(ROOT, "scripts/clint-aksi.sh")
ORANYE, HIJAU, MERAH, ABU = "#E07B2E", "#2F9E6B", "#D64545", "#8A94A3"


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


# ---- data ----
lap, waktu_lap = None, None
p = os.path.join(LOG, "terakhir.json")
if os.path.exists(p):
    try:
        lap = json.load(open(p, encoding="utf-8"))
        waktu_lap = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%H.%M")
    except Exception:
        lap = None

kerja = None
k = os.path.join(LOG, "kerja.txt")
if os.path.exists(k) and time.time() - os.path.getmtime(k) < 3 * 3600:
    kerja = [x for x in open(k, encoding="utf-8").read().splitlines() if x.strip()]

# Sesi Claude Code yang aktif (dicatat hooks/status-sesi.sh, tanpa token)
def nama_proyek(d):
    base, induk = os.path.basename(d), os.path.basename(os.path.dirname(d))
    return f"{induk} · {base}" if os.path.exists(os.path.join(d, ".claude/clint.json")) and \
        not os.path.exists(os.path.join(os.path.dirname(d), ".claude/clint.json")) and induk not in ("Desktop", "Documents") \
        and len(base) < 12 else base

sesi = []
sd = os.path.join(CFG, "sesi")
for fn in (os.listdir(sd) if os.path.isdir(sd) else []):
    try:
        f = os.path.join(sd, fn); x = json.load(open(f, encoding="utf-8")); umur = time.time() - os.path.getmtime(f)
    except Exception:
        continue
    st = x.get("status")
    if (st in ("bekerja", "latar") and umur < 3 * 3600) or (st == "menunggu" and umur < 3600) \
            or (st == "selesai" and umur < 600):
        x["umur"] = umur; sesi.append(x)
sesi.sort(key=lambda x: x.get("mulai", 0))
aktif_sesi = [x for x in sesi if x["status"] in ("bekerja", "latar")]

L = lambda key: (lap or {}).get(key) or []
gagal, kerjakan, cek, tunggu = L("gagal"), L("kerjakan"), L("cek"), L("tunggu")
menunggu = len(gagal) + len(kerjakan) + len(cek)

# ---- ikon + badge ----
ikon = os.path.join(CFG, "ikon.png")
img = f"image={base64.b64encode(open(ikon, 'rb').read()).decode()} width=18 height=18" if os.path.exists(ikon) \
    else "sfimage=person.crop.circle"
if kerja or aktif_sesi:
    label = bersih(kerja[0], 18) if kerja else (f"{len(aktif_sesi)} sesi" if len(aktif_sesi) > 1 else "bekerja")
    print(f"⟳ {label} | {img} color={ORANYE}")
elif gagal:
    print(f"! | {img} color={MERAH}")
elif lap is not None and menunggu == 0:
    print(f"✓ | {img} color={HIJAU}")
elif menunggu:
    print(f"{menunggu} | {img} color={ORANYE}")
else:
    print(f" | {img}")
print("---")

# ---- kepala ----
if kerja or aktif_sesi:
    print("Sedang bekerja | size=14")
    print(f"{bersih(kerja[0]) if kerja else str(len(aktif_sesi)) + ' sesi Claude Code aktif'} | size=11 color={ABU}")
elif gagal:
    print("Ada yang gagal | size=14")
    print(f"{bersih(gagal[0].get('teks'))} | size=11 color={ABU}")
elif lap is None:
    print(f"{sapa()} | size=14")
    print(f"Belum ada laporan | size=11 color={ABU}")
else:
    print(f"{sapa()} | size=14")
    ket = f"{menunggu} hal menunggu" if menunggu else "Tidak ada yang menunggu"
    print(f"{ket} · cek terakhir {waktu_lap} | size=11 color={ABU}")
print("---")


DIR = {p.get("nama"): p.get("dir") for p in L("proyek") if p.get("dir")}

def butir(x, warna):
    print(f"{bersih(x.get('teks'), 60)} | sfimage=circle.fill sfcolor={warna}")
    print(f"--{bersih(x.get('proyek'))} · {bersih(x.get('sumber'))} | size=11 color={ABU}")
    if x.get("perintah"):
        print(f"--Salin perintah | {aksi('salin', x['perintah'], x.get('proyek'))}")
        print(f"----{bersih(x['perintah'])} | size=11 color={ABU}")
    if x.get("url"):
        print(f"--Buka MR di browser | {aksi('buka', x['url'])}")
    if DIR.get(x.get("proyek")):
        print(f"--Buka project di VS Code | {aksi('vscode', DIR[x['proyek']])}")


def durasi(dt):
    m = int(dt // 60)
    return "baru saja" if m < 1 else f"{m} mnt" if m < 60 else f"{m // 60} j {m % 60} mnt"

if sesi or kerja:
    print(f"Agent & sesi | size=11 color={ABU}")
    for baris in (kerja or [])[1:3]:
        print(f"{bersih(baris)} | size=12")
    for x in sesi:
        st = x["status"]
        tanda = {"bekerja": ("circle.dotted", ORANYE, "bekerja"), "latar": ("circle.dotted", ORANYE, "di latar"),
                 "menunggu": ("hand.raised.fill", "#C79A2B", "menunggu Anda"), "selesai": ("checkmark.circle", HIJAU, "selesai")}[st]
        lama = durasi(time.time() - x.get("mulai", time.time())) if st != "selesai" else durasi(x["umur"]) + " lalu"
        cwd = x.get("cwd", "")
        print(f"{nama_proyek(cwd)} — {tanda[2]} · {lama} | sfimage={tanda[0]} sfcolor={tanda[1]} {aksi('vscode', cwd)}")
        ag = sorted(set(a.split(":")[-1] for a in (x.get("agents") or {}).values()))
        if ag:
            print(f"--Agent: {bersih(', '.join(ag), 80)} | size=12")
        if x.get("tugas"):
            print(f"--Tugas: {bersih(x['tugas'], 80)} | size=12 color={ABU}")
        print(f"--Buka di VS Code | {aksi('vscode', cwd)}")
    print("---")
for judul, xs, warna in (("Perlu perhatian", gagal, MERAH), ("Perlu dikerjakan", kerjakan, ORANYE),
                         ("Menunggu review Anda", cek, "#C79A2B")):
    if xs:
        print(f"{judul} | size=11 color={ABU}")
        for x in xs[:6]:
            butir(x, warna)
        print("---")
if lap is not None and not (gagal or kerjakan or cek) and not kerja:
    print(f"Tidak ada yang perlu ditindaklanjuti. | color={ABU}")
    print("---")

# ---- tombol cepat ----
print(f"Buka laporan terakhir | {aksi('laporan')} sfimage=doc.text")
print(f"Cek semua project | {aksi('cek-semua', refresh=True)} sfimage=arrow.clockwise")
print("Cek project | sfimage=folder")
try:
    aktif = subprocess.run(["bash", os.path.join(ROOT, "scripts/proyek-aktif.sh"), "3"],
                           capture_output=True, text=True, timeout=10).stdout.split("\n")
except Exception:
    aktif = []
for d in [x for x in aktif if x.strip()]:
    nama = f"{os.path.basename(os.path.dirname(d))} · {os.path.basename(d)}"
    print(f"--{nama} | {aksi('cek', d, refresh=True)}")
print(f"Halo Clint | {aksi('halo')} sfimage=mic")
print("---")
diam = os.path.exists(os.path.join(CFG, "diam"))
bisu = os.path.exists(os.path.join(CFG, "bisu-sampai"))
print("Pengaturan | sfimage=gearshape")
print(f"--Suara: {'mati' if diam else 'aktif ✓'} | {aksi('suara')}")
print(f"--Sapaan pagi: 08.00, Sen–Jum | {aksi('sapaan')}")
print(f"--{'Nyalakan kabar lagi' if bisu else 'Bisukan sampai besok'} | {aksi('bunyikan' if bisu else 'bisu')}")
