#!/usr/bin/env python3
"""Render laporan pagi gabungan (JSON dari /clint:cek semua) menjadi halaman HTML lokal.
Pakai: render-laporan.py <laporan.json> <laporan.html>"""
import json, sys, html, datetime, base64, os

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
e = lambda s: html.escape(str(s or ""))

proyek = d.get("proyek", [])
warna = {p.get("nama"): "ab"[i % 2] for i, p in enumerate(proyek)}
def chip(nama, extra=""):
    k = warna.get(nama, "a")
    return f'<span class="chip {k}">{e(nama)}{extra}</span>'

def butir(x):
    cmd = ""
    if x.get("perintah"):
        cmd = (f'<div class="cmd"><code>{e(x["perintah"])}</code>'
               f'<button class="copy" type="button">Salin</button>'
               f'<span class="hint">jalankan di {e(x.get("proyek"))}</span></div>')
    return (f'<li class="item"><div class="body"><p>{e(x.get("teks"))}</p>'
            f'<div class="meta">{chip(x.get("proyek"))}<span>{e(x.get("sumber"))}</span>'
            f'{f"<a href=\"{e(x["url"])}\">buka</a>" if x.get("url") else ""}</div>{cmd}</div></li>')

def grup(kunci, judul, kelas):
    xs = d.get(kunci) or []
    if not xs: return ""
    return (f'<section class="group {kelas}"><h2>{judul} <span class="count">{len(xs)}</span></h2>'
            f'<ul class="items">{"".join(butir(x) for x in xs)}</ul></section>')

av_path = os.path.expanduser("~/.config/clint/avatar.jpg")  # opsional, milik pribadi, tidak di repo
avatar = ""
if os.path.exists(av_path):
    b64 = base64.b64encode(open(av_path, "rb").read()).decode()
    avatar = f'<img class="avatar" alt="clint" src="data:image/jpeg;base64,{b64}">'
waktu = d.get("tanggal") or datetime.datetime.now().strftime("%Y-%m-%d %H.%M")
pills = "".join(f'<span class="pill ok">{e(s)}</span>' for s in d.get("aman", [])) + \
        "".join(f'<span class="pill warn">{e(s)}</span>' for s in d.get("peringatan", []))
rincian = "".join(
    f'<section><h3>{e(r.get("proyek"))}</h3><ul>{"".join(f"<li>{e(b)}</li>" for b in r.get("butir", []))}</ul></section>'
    for r in d.get("rincian", []))
kosong = "" if any(d.get(k) for k in ("gagal", "kerjakan", "cek", "tunggu")) else \
    '<p class="lead">Tidak ada yang perlu ditindaklanjuti hari ini.</p>'

CSS = """
:root{--bg:#EDF1F6;--surface:#FFF;--ink:#18212D;--muted:#5A6676;--line:#D6DDE7;--dawn:#C9671E;--dawn-soft:#FBEBDD;
--ok:#2F7D5B;--ok-soft:#E1F1E9;--warn:#A86A0B;--warn-soft:#FBF0D9;--chip-a:#2D5DA8;--chip-a-soft:#E2EAF7;--chip-b:#7A4AA8;--chip-b-soft:#EEE5F7;
--f-display:"Bricolage Grotesque","Avenir Next",system-ui,sans-serif;--f-body:"IBM Plex Sans",-apple-system,system-ui,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#10161F;--surface:#18212D;--ink:#E7ECF3;--muted:#9AA6B6;--line:#2A3544;--dawn:#F0954A;--dawn-soft:#3A2817;
--ok:#6CC59B;--ok-soft:#17312A;--warn:#E7B04F;--warn-soft:#352A12;--chip-a:#8DB2F0;--chip-a-soft:#1D2B44;--chip-b:#C6A2EC;--chip-b-soft:#2D2140;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--f-body);padding:28px 16px 64px}
.screen{max-width:780px;margin:0 auto;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:28px clamp(18px,4vw,40px) 32px;display:grid;gap:26px}
h1,h2,h3{margin:0;text-wrap:balance}h1{font:700 clamp(30px,5vw,42px)/1.15 var(--f-display)}h1 em{font-style:normal;color:var(--dawn)}
.eyebrow{font:500 11.5px var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.lead{font-size:17px;margin:0;max-width:60ch}code{font-family:var(--f-mono);font-size:.88em}
.hello{display:grid;gap:10px}.top{display:flex;align-items:center;gap:12px}.avatar{width:52px;height:52px;border-radius:50%;object-fit:cover;border:2px solid var(--dawn)}.projects,.calm{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;gap:6px;font:500 12px var(--f-mono);padding:4px 10px;border-radius:999px}.chip small{opacity:.75}
.chip.a{color:var(--chip-a);background:var(--chip-a-soft)}.chip.b{color:var(--chip-b);background:var(--chip-b-soft)}
.speak{font:500 13px var(--f-body);color:var(--dawn);background:var(--dawn-soft);border:0;border-radius:999px;padding:6px 12px;cursor:pointer}
.group{display:grid;gap:10px}.group h2{font:600 15px var(--f-body);display:flex;gap:10px;align-items:center}.count{font:500 12px var(--f-mono);color:var(--muted)}
.items{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.item{display:grid;grid-template-columns:4px 1fr;gap:14px;background:var(--bg);border-radius:10px;padding:12px 14px 12px 0}
.item:before{content:"";border-radius:0 3px 3px 0}.do .item:before{background:var(--dawn)}.fail .item:before{background:#C23B3B}.check .item:before{background:var(--warn)}.wait .item:before{background:var(--line)}
.body{min-width:0;display:grid;gap:6px}.body p{margin:0}.meta{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;color:var(--muted);font-size:13px}
.cmd{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.cmd code{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:3px 8px;overflow-wrap:anywhere}
.copy{font:500 12px var(--f-body);background:none;border:1px solid var(--line);color:var(--ink);border-radius:6px;padding:3px 9px;cursor:pointer}.copy:hover{border-color:var(--dawn);color:var(--dawn)}
.hint{font-size:12px;color:var(--muted)}.pill{font-size:13px;padding:5px 11px;border-radius:999px}
.pill.ok{background:var(--ok-soft);color:var(--ok)}.pill.warn{background:var(--warn-soft);color:var(--warn)}
details{border-top:1px solid var(--line);padding-top:14px}summary{cursor:pointer;font-weight:600;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:12px}
.grid section{min-width:0;font-size:13.5px;color:var(--muted)}.grid h3{font:600 13px var(--f-body);color:var(--ink);margin-bottom:6px}.grid ul{margin:0;padding-left:18px}
.foot{font-size:12.5px;color:var(--muted)}
button:focus-visible,summary:focus-visible{outline:2px solid var(--dawn);outline-offset:2px}
"""
JS = """
document.querySelectorAll('.copy').forEach(b=>b.onclick=()=>{const t=b.parentElement.querySelector('code').textContent;
navigator.clipboard.writeText(t).then(()=>{b.textContent='Tersalin';setTimeout(()=>b.textContent='Salin',1600)})});
const sp=document.getElementById('speak');if(sp)sp.onclick=()=>{const u=new SpeechSynthesisUtterance(sp.dataset.t);u.lang='id-ID';speechSynthesis.cancel();speechSynthesis.speak(u)};
"""
judul = d.get("judul") or d.get("kalimat") or "Selamat pagi."
out = f"""<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sapaan pagi · {e(waktu)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@500&display=swap">
<style>{CSS}</style></head><body><main class="screen">
<header class="hello"><div class="top">{avatar}<span class="eyebrow">clint · {e(waktu)}</span></div><h1>{e(judul)}</h1>
<p class="lead">{e(d.get("lead"))}</p>
<div class="projects">{"".join(chip(p.get("nama"), f' <small>{e(p.get("aktif"))}</small>' if p.get("aktif") else "") for p in proyek)}
<button class="speak" id="speak" type="button" data-t="{e(d.get("kalimat"))}">▶ Bacakan</button></div></header>
{kosong}{grup("gagal","Perlu perhatian","fail")}{grup("kerjakan","Perlu dikerjakan","do")}{grup("cek","Perlu Anda cek","check")}{grup("tunggu","Menunggu pihak lain","wait")}
<div class="calm">{pills}</div>
{f'<details><summary>Rincian per project</summary><div class="grid">{rincian}</div></details>' if rincian else ""}
<div class="foot">Dibuat oleh clint</div></main><script>{JS}</script></body></html>"""
open(dst, "w", encoding="utf-8").write(out)
