#!/usr/bin/env python3
"""Render laporan (JSON dari /clint:status) menjadi halaman HTML lokal: satu tugas paling mendesak di atas,
papan tiga kolom, dan panel sesi berjalan, rencana, serta peringatan. Tanpa token.
Pakai: render-report.py <laporan.json> <laporan.html>"""
import json, sys, html, datetime, base64, os, re, glob, subprocess, time

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
e = lambda s: html.escape(str(s or ""))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")

proyek = d.get("proyek") or []
nama_dir = {os.path.realpath(p["dir"]): p.get("nama") for p in proyek if p.get("dir")}
warna = {p.get("nama"): "ab"[i % 2] for i, p in enumerate(proyek)}


def diklaim_lain():
    """Teks butir yang sedang dipegang sesi lain, dari `update-report.py langkah` per project."""
    out = set()
    for p in proyek:
        if not p.get("dir"):
            continue
        try:
            r = subprocess.run(["python3", os.path.join(ROOT, "scripts/update-report.py"), "langkah", "--dir", p["dir"]],
                               capture_output=True, text=True, timeout=10).stdout
        except (OSError, subprocess.TimeoutExpired):
            continue
        for l in r.splitlines():
            if l.startswith("Sedang dikerjakan sesi lain: "):
                out.add(l.split(": ", 1)[1].rsplit(" (", 1)[0])
    return out


def sesi_berjalan():
    out = []
    for f in glob.glob(os.path.join(HOME, "Library/Logs/clint/kerja/*.json")):
        sid = os.path.basename(f)[:-5]
        if time.time() - os.path.getmtime(f) > 3 * 3600 or not os.path.exists(os.path.join(HOME, f".config/clint/sesi/{sid}.json")):
            continue
        try:
            k = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        k["proyek"] = nama_dir.get(os.path.realpath(k.get("dir") or "")) or os.path.basename(k.get("dir") or "")
        out.append(k)
    return out


TAHAP = ["worktree", "implementasi", "tinjau", "test", "MR"]
KATA = [(4, r"\bMR\b|push|commit"), (3, r"test|e2e"), (2, r"tinjau|review|auditor"),
        (1, r"implementasi|developer"), (0, r"worktree|siapkan")]


def tahap_ke(t):
    return next((i for i, pola in KATA if re.search(pola, t or "", re.I)), None)


klaim_teks = diklaim_lain()
sesi = sesi_berjalan()
gagal, cek, tunggu = d.get("gagal") or [], d.get("cek") or [], d.get("tunggu") or []
kerjakan = [x for x in d.get("kerjakan") or [] if x.get("teks") not in klaim_teks]
dipegang = len(d.get("kerjakan") or []) - len(kerjakan) + sum(x.get("teks") in klaim_teks for x in gagal)
gagal = [x for x in gagal if x.get("teks") not in klaim_teks]

perintah_ada = {x.get("perintah") for x in (d.get("gagal") or []) + (d.get("kerjakan") or [])}
klaim_pr = [(os.path.splitext(os.path.basename(k.get("rencana") or ""))[0], set(k.get("prs") or [])) for k in sesi]


def langkah_diklaim(b):
    """Langkah Berikutnya yang sedang dipegang sesi lain (rencana maupun butir feedback), dicek skrip yang sama
    dengan hook Stop."""
    dirp = b.get("dir") or next((p.get("dir") for p in proyek if p.get("nama") == b.get("proyek")), None)
    if not dirp:
        return set()
    try:
        r = subprocess.run(["python3", os.path.join(ROOT, "scripts/update-report.py"), "cek-berikutnya", "--dir", dirp],
                           input="\n".join(b.get("langkah") or []), capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return set()
    return {l.split("\t")[0] for l in r.splitlines()}


langkah_rencana = []
nx = d.get("berikutnya") or []
for b in nx if isinstance(nx, list) else [{"proyek": "", "langkah": [nx]}]:
    lain = langkah_diklaim(b)
    for t in b.get("langkah") or []:
        m = re.match(r"^\[([^\]]*)\]\s*(/\S.*?)(?:\s+·\s+(.*))?$", t.strip())
        if not m or m.group(2) in perintah_ada or m.group(1).startswith("terblokir"):
            continue
        cmd = m.group(2)
        if cmd.strip() in lain or \
                any(slug and slug in cmd and prs & set(re.findall(r"PR-\d+", cmd)) for slug, prs in klaim_pr):
            dipegang += 1
            continue
        langkah_rencana.append({"teks": re.sub(r"^/clint:\w+\s+", "", cmd), "proyek": b.get("proyek"),
                                "sumber": m.group(1), "perintah": cmd, "ket": m.group(3)})

fokus = (gagal or kerjakan or [None])[0]
siap = [x for x in gagal + kerjakan if x is not fokus] + langkah_rencana


def proyek_tag(nama):
    return f'<span class="pj {warna.get(nama, "a")}"><i></i>{e(nama)}</span>'


def salin(cmd, besar=False):
    if besar:
        return (f'<div class="hero-cmd"><code>{e(cmd)}</code>'
                f'<button class="copy big" type="button" data-cmd="{e(cmd)}">Salin perintah</button></div>')
    return (f'<button class="copy line" type="button" data-cmd="{e(cmd)}"><code>{e(cmd)}</code>'
            f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/>'
            f'<path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg><span>Salin</span></button>')


def kartu(x):
    ket = x.get("ket") or ""
    aksi = salin(x["perintah"]) if x.get("perintah") else \
        (f'<a class="open" href="{e(x["url"])}">Buka MR</a>' if x.get("url") else "")
    return (f'<article class="card" data-p="{e(x.get("proyek"))}"><div class="meta">{proyek_tag(x.get("proyek"))}'
            f'<span>·</span><span class="mono">{e(x.get("sumber"))}</span></div>'
            f'<p class="t">{e(x.get("teks"))}</p>{f"<p class=k>{e(ket)}</p>" if ket else ""}{aksi}</article>')


def kolom(judul, kelas, xs, ket=""):
    isi = "".join(kartu(x) for x in xs) or '<p class="empty">Kosong</p>'
    return (f'<section class="col"><div class="col-h"><span class="dot {kelas}"></span><h2>{judul}</h2>'
            f'<span class="mono n">{len(xs)}</span>{f"<span class=ch>{e(ket)}</span>" if ket else ""}</div>{isi}</section>')


if fokus:
    label = "Kerjakan dulu" if fokus in gagal else "Mulai dari sini"
    hero_isi = (f'<div class="eyebrow {"bad" if fokus in gagal else ""}"><span></span>{label}</div>'
                f'<p class="hero-t">{e(fokus.get("teks"))}</p>'
                f'<p class="hero-k">{proyek_tag(fokus.get("proyek"))} · {e(fokus.get("sumber"))}</p>'
                + (salin(fokus["perintah"], True) if fokus.get("perintah") else ""))
else:
    hero_isi = ('<div class="eyebrow calm"><span></span>Aman</div>'
                '<p class="hero-t">Tidak ada yang perlu dikerjakan sekarang. Tugas hari ini sudah selesai semua.</p>')
angka = [(len(siap), "siap dikerjakan", "c1"), (len(cek), "menunggu review Anda", "c2"),
         (len(tunggu), "menunggu pihak lain", "c3"), (len(sesi), "sesi berjalan", "c4")]
ringkas = "".join(f'<div class="stat"><b class="{c}">{n}</b><span>{l}</span></div>' for n, l, c in angka)


def baris_sesi(k):
    i = tahap_ke(k.get("tahap"))
    bar = "" if i is None else '<div class="steps" aria-hidden="true">' + "".join(
        f'<span class="{"done" if j < i else "now" if j == i else ""}"></span>' for j in range(len(TAHAP))) + "</div>"
    mulai = f'<span class="muted">sejak {e(k["mulai"])}</span>' if k.get("mulai") else ""
    return (f'<div class="sesi" data-p="{e(k["proyek"])}"><div class="row"><b>{e(k.get("label") or k.get("judul"))} · {e(k["proyek"])}</b>'
            f'{mulai}</div>{bar}<div class="small">{e(k.get("tahap"))}</div></div>')


panel_sesi = "".join(baris_sesi(k) for k in sesi) or '<p class="empty">Tidak ada sesi yang berjalan.</p>'
rencana = d.get("rencana") or []
panel_rencana = "".join(
    f'<div class="plan" data-p="{e(r.get("proyek"))}"><div class="row"><span>{e(r.get("nama"))}</span>'
    f'<span class="mono">{r.get("selesai", 0)}/{r.get("total", 0)}</span></div><div class="bar"><span class="{"full" if r.get("selesai") == r.get("total") else ""}" '
    f'style="width:{round(100 * (r.get("selesai") or 0) / max(r.get("total") or 1, 1))}%"></span></div></div>'
    for r in rencana)
peringatan = "".join(f'<div class="warn">{e(s)}</div>' for s in d.get("peringatan") or [])
aman = "".join(f'<span class="pill">{e(s)}</span>' for s in d.get("aman") or [])
rincian = "".join(
    f'<section><h3>{e(r.get("proyek"))}</h3><ul>{"".join(f"<li>{e(b)}</li>" for b in r.get("butir", []))}</ul></section>'
    for r in d.get("rincian") or [])
filter_btn = "".join(f'<button type="button" data-f="{e(p.get("nama"))}">{e(p.get("nama"))}</button>' for p in proyek) \
    if len(proyek) > 1 else ""

av_path = os.path.join(HOME, ".config/clint/avatar.jpg")  # opsional, milik pribadi, tidak di repo
avatar = '<div class="logo">c</div>'
if os.path.exists(av_path):
    avatar = f'<img class="logo" alt="clint" src="data:image/jpeg;base64,{base64.b64encode(open(av_path, "rb").read()).decode()}">'
waktu = d.get("tanggal") or datetime.datetime.now().strftime("%Y-%m-%d %H.%M")
judul = d.get("judul") or d.get("kalimat") or "Selamat pagi."

CSS = """
:root{--bg:#F5F6F8;--surface:#FFF;--ink:#14171C;--muted:#596170;--soft:#3C4350;--line:#E3E6EB;--line2:#EEF0F3;--chipbg:#E8EAEE;
--hero:#14171C;--hero-2:#1D2128;--hero-3:#23272F;--hero-ink:#F3F5F8;--hero-mut:#A8B0BD;
--a:#2457D6;--b:#7A3FC4;--ok:#1F7A3D;--ok2:#7FC796;--bad:#FF8F87;--warn-bg:#FFF7E6;--warn-line:#F1DFB4;--warn-ink:#6B4600;
--c1:#9DB8FF;--c2:#8FD6A6;--c3:#C9A8F5;--c4:#F3F5F8;--f:"Geist",-apple-system,system-ui,sans-serif;--m:"Geist Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#0E1116;--surface:#161A20;--ink:#E8EBF0;--muted:#9AA3B0;--soft:#C3C9D2;--line:#262B33;--line2:#20242B;
--chipbg:#1E232A;--hero:#1C2129;--hero-2:#252B34;--hero-3:#2C333D;--a:#8DB0FF;--b:#C6A2EC;--ok:#6CC59B;--ok2:#3E8A5E;
--warn-bg:#2E2513;--warn-line:#4A3B1A;--warn-ink:#F0C66B;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 var(--f);padding:28px 16px 56px}
.wrap{max-width:1392px;margin:0 auto;display:flex;flex-direction:column;gap:24px}
h1,h2,h3,p{margin:0}.mono{font-family:var(--m)}.muted{color:var(--muted);font-size:12px}.small{font-size:12px;color:var(--soft)}
code{font-family:var(--m)}
header{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px}
.who{display:flex;align-items:center;gap:14px;min-width:0}.who>div{min-width:0}.logo{width:44px;height:44px;border-radius:12px;background:var(--ink);color:var(--bg);
display:flex;align-items:center;justify-content:center;font-weight:700;font-size:18px;object-fit:cover;flex:none}
h1{font-size:20px;font-weight:600;letter-spacing:-.01em;text-wrap:balance}.sub{color:var(--muted);font-size:13px}
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.seg{display:flex;padding:4px;border-radius:12px;background:var(--chipbg);gap:2px}
.seg button,.speak{min-height:40px;padding:0 14px;border-radius:9px;border:0;background:transparent;color:var(--soft);font:inherit;cursor:pointer}
.seg button[aria-pressed=true]{background:var(--surface);color:var(--ink);font-weight:500;box-shadow:0 1px 2px rgba(20,23,28,.1)}
.speak{border:1px solid var(--line);background:var(--surface);color:var(--ink);min-height:48px;border-radius:12px;font-weight:500}
.hero{background:var(--hero);color:var(--hero-ink);border-radius:20px;padding:24px;display:flex;flex-wrap:wrap;gap:24px;align-items:center}
.hero-main{flex:999 1 520px;min-width:0;display:flex;flex-direction:column;gap:12px}
.eyebrow{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--c1)}
.eyebrow span{width:8px;height:8px;border-radius:4px;background:currentColor}.eyebrow.bad{color:var(--bad)}.eyebrow.calm{color:var(--c2)}
.hero-t{font-size:26px;font-weight:600;letter-spacing:-.015em;line-height:1.2;text-wrap:balance}.hero-k{color:var(--hero-mut);font-size:13px}
.hero .pj{color:var(--hero-ink)}.hero .pj i{background:var(--hero-mut)}
.hero-cmd{display:flex;flex-wrap:wrap;gap:8px;padding-top:4px}.hero-cmd code{flex:1 1 360px;min-width:0;font-size:13px;background:var(--hero-3);
border-radius:10px;padding:13px 14px;overflow-wrap:anywhere}
.copy{cursor:pointer;font:inherit}.copy.big{min-height:48px;padding:0 18px;border-radius:10px;border:0;background:var(--hero-ink);color:var(--hero);font-weight:600}
.stats{flex:1 1 260px;min-width:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.stat{background:var(--hero-2);border-radius:14px;padding:14px;display:flex;flex-direction:column;gap:4px}
.stat b{font-size:28px;font-weight:600;letter-spacing:-.02em}.stat span{font-size:12px;color:var(--hero-mut)}
.c1{color:var(--c1)}.c2{color:var(--c2)}.c3{color:var(--c3)}.c4{color:var(--c4)}
.body{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start}
.board{flex:999 1 680px;min-width:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:16px;align-items:start}
.col{min-width:0;display:flex;flex-direction:column;gap:10px}.col-h{display:flex;align-items:center;gap:8px;padding:0 4px}
.col-h h2{font-size:14px;font-weight:600}.n{font-size:12px;color:var(--muted)}.ch{margin-left:auto;font-size:12px;color:var(--muted)}
.dot{width:8px;height:8px;border-radius:4px}.dot.siap{background:var(--a)}.dot.rev{background:var(--ok)}.dot.wait{background:var(--b)}
.card{min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px;display:flex;flex-direction:column;gap:10px}
.meta{display:flex;flex-wrap:wrap;align-items:center;gap:8px;font-size:12px;color:var(--muted)}
.pj{display:inline-flex;align-items:center;gap:6px;font-weight:500}.pj i{width:6px;height:6px;border-radius:3px}
.pj.a{color:var(--a)}.pj.a i{background:var(--a)}.pj.b{color:var(--b)}.pj.b i{background:var(--b)}
.t{font-size:15px;font-weight:500;line-height:1.4}.k{font-size:13px;color:var(--muted)}
.copy.line{min-width:0;width:100%;min-height:44px;display:flex;align-items:center;gap:10px;text-align:left;padding:0 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--soft)}
.copy.line code{flex:1;min-width:0;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.copy.line span{font-size:12px;font-weight:500}
.open{min-height:44px;display:flex;align-items:center;justify-content:center;border-radius:10px;border:1px solid var(--line);text-decoration:none;font-size:13px;font-weight:500;color:var(--a)}
.empty{color:var(--muted);font-size:13px;padding:8px 4px}
aside{flex:1 1 320px;min-width:0;display:flex;flex-direction:column;gap:16px}
.box{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:18px;display:flex;flex-direction:column;gap:14px}
.box h2{font-size:14px;font-weight:600}.row{display:flex;justify-content:space-between;gap:8px}
.sesi{display:flex;flex-direction:column;gap:8px;padding-top:12px;border-top:1px solid var(--line2)}
.steps{display:flex;gap:4px}.steps span{flex:1;height:4px;border-radius:2px;background:var(--line)}.steps .done{background:var(--ok)}.steps .now{background:var(--ok2)}
.plan{display:flex;flex-direction:column;gap:6px;font-size:13px}.bar{height:4px;border-radius:2px;background:var(--line2)}
.bar span{display:block;height:4px;border-radius:2px;background:var(--a)}.bar .full{background:var(--ok)}
.warn{background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-ink);border-radius:16px;padding:14px 18px;font-size:13px}
.pills{display:flex;flex-wrap:wrap;gap:8px}.pill{font-size:12px;padding:5px 11px;border-radius:999px;background:var(--chipbg);color:var(--soft)}
details{border-top:1px solid var(--line);padding-top:14px}summary{cursor:pointer;font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:12px}
.grid section{font-size:13px;color:var(--muted)}.grid h3{font-size:13px;color:var(--ink);margin-bottom:6px}.grid ul{margin:0;padding-left:18px}
[hidden]{display:none!important}
button:focus-visible,a:focus-visible,summary:focus-visible{outline:2px solid var(--a);outline-offset:2px}
"""
JS = """
document.querySelectorAll('.copy').forEach(b=>b.onclick=()=>navigator.clipboard.writeText(b.dataset.cmd).then(()=>{
const s=b.querySelector('span')||b,t=s.textContent;s.textContent='Tersalin';setTimeout(()=>s.textContent=t,1600)}));
const fb=[...document.querySelectorAll('.seg button')];fb.forEach(b=>b.onclick=()=>{fb.forEach(x=>x.setAttribute('aria-pressed',x===b));
const f=b.dataset.f;document.querySelectorAll('[data-p]').forEach(el=>el.hidden=!!f&&el.dataset.p!==f)});
const sp=document.getElementById('speak');if(sp)sp.onclick=()=>{const u=new SpeechSynthesisUtterance(sp.dataset.t);u.lang='id-ID';speechSynthesis.cancel();speechSynthesis.speak(u)};
"""

out = f"""<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>clint · {e(waktu)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap">
<style>{CSS}</style></head><body><div class="wrap">
<header><div class="who">{avatar}<div><h1>{e(judul)}</h1><div class="sub">{e(waktu)}{" · " + e(d.get("lead")) if d.get("lead") else ""}</div></div></div>
<div class="tools">{f'<div class="seg" role="group" aria-label="Saring project"><button type="button" aria-pressed="true" data-f="">Semua</button>{filter_btn}</div>' if filter_btn else ""}
{f'<button class="speak" id="speak" type="button" data-t="{e(d.get("kalimat"))}">Bacakan</button>' if d.get("kalimat") else ""}</div></header>
<section class="hero"><div class="hero-main">{hero_isi}</div><div class="stats">{ringkas}</div></section>
<div class="body"><main class="board">
{kolom("Siap dikerjakan", "siap", siap, f"+{dipegang} dipegang sesi lain" if dipegang else "")}
{kolom("Review Anda", "rev", cek)}
{kolom("Menunggu pihak lain", "wait", tunggu)}
</main><aside>
<section class="box"><div class="row"><h2>Sedang berjalan</h2><span class="muted">{len(sesi)} sesi</span></div>{panel_sesi}</section>
{f'<section class="box"><h2>Rencana</h2>{panel_rencana}</section>' if panel_rencana else ""}
{peringatan}{f'<div class="pills">{aman}</div>' if aman else ""}
</aside></div>
{f'<details><summary>Rincian per project</summary><div class="grid">{rincian}</div></details>' if rincian else ""}
</div><script>{JS}</script></body></html>"""
open(dst, "w", encoding="utf-8").write(out)
