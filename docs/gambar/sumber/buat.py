#!/usr/bin/env python3
"""Buat gambar presentasi clint (docs/gambar/*.png) dari HTML, dipotret Microsoft Edge/Chrome headless.
Pakai: python3 docs/gambar/sumber/buat.py
Data di gambar adalah CONTOH (project fiktif); jangan memakai nama/data project sungguhan."""
import os, shutil, subprocess, tempfile, time

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(DIR)
BROWSER = next((p for p in [
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("chromium") or "", shutil.which("google-chrome") or ""] if p and os.path.exists(p)), None)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{--bg:#0E1420;--bg2:#141C2B;--card:#1A2333;--line:#2A3548;--ink:#EEF2F7;--muted:#97A3B6;--dim:#6B778B;
--dawn:#F0954A;--dawn2:#FFB37A;--dawn-soft:rgba(240,149,74,.14);--ok:#4CC38A;--warn:#E8B84A;--crit:#EF6B6B;--blue:#7AA7F5;--violet:#B79AF0;
--fd:"Bricolage Grotesque","Avenir Next",system-ui,sans-serif;--fb:"IBM Plex Sans",-apple-system,system-ui,sans-serif;--fm:"IBM Plex Mono",Menlo,monospace}
*{box-sizing:border-box;margin:0}
html,body{width:100%;height:100%}
body{background:radial-gradient(90% 120% at 100% 0%,#2A1E1A 0%,transparent 55%),radial-gradient(70% 90% at 0% 100%,#122238 0%,transparent 60%),var(--bg);
color:var(--ink);font:16px/1.5 var(--fb);padding:56px 64px;overflow:hidden}
.eyebrow{font:500 13px var(--fm);letter-spacing:.14em;text-transform:uppercase;color:var(--dawn)}
h1,h2{font-family:var(--fd);letter-spacing:-.01em;text-wrap:balance}
h2{font-size:40px;font-weight:800;margin:8px 0 6px;line-height:1.12}
.sub{color:var(--muted);font-size:18px;max-width:60ch}
.logo{width:64px;height:64px;border-radius:50%;display:grid;place-items:center;font:800 34px/1 var(--fd);color:var(--bg);
background:radial-gradient(circle at 35% 30%,var(--dawn2),var(--dawn));box-shadow:0 0 0 4px var(--bg),0 0 0 6px var(--dawn);flex:none}
.logo.s{width:22px;height:22px;font-size:13px;box-shadow:0 0 0 2px #000,0 0 0 3.5px var(--dawn)}
.logo.m{width:40px;height:40px;font-size:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px}
.mono{font-family:var(--fm)}
.pill{display:inline-block;font:500 12px var(--fm);padding:3px 9px;border-radius:999px}
.opus{background:rgba(240,149,74,.16);color:var(--dawn2)}.sonnet{background:rgba(122,167,245,.16);color:var(--blue)}.haiku{background:rgba(183,154,240,.16);color:var(--violet)}
.foot{position:absolute;left:64px;right:64px;bottom:36px;display:flex;justify-content:space-between;color:var(--dim);font:13px var(--fm)}
"""

def halaman(nama, body, w=1280, h=720, css=""):
    return nama, f"<!doctype html><html lang='id'><head><meta charset='utf-8'><style>{CSS}{css}</style></head><body>{body}</body></html>", w, h

GAMBAR = []

# 1. Sampul ------------------------------------------------------------------------------------
GAMBAR.append(halaman("sampul", """
<div style="display:grid;grid-template-columns:1.05fr .95fr;gap:56px;align-items:center;height:100%">
 <div style="display:grid;gap:26px">
  <div style="display:flex;align-items:center;gap:18px"><div class="logo">c</div>
   <h1 style="font-size:84px;font-weight:800;line-height:1">clint</h1></div>
  <p style="font-size:27px;line-height:1.35;font-family:var(--fd);font-weight:600;max-width:20ch">Tim agent Claude Code yang mengerjakan tiket sampai jadi MR.</p>
  <p class="sub">Satu perintah: rencana, kode, tinjauan berlapis, E2E, dan MR. Anda tinggal review dan merge.</p>
  <div style="display:flex;flex-wrap:wrap;gap:10px">
   <span class="cmd">/clint:cek</span><span class="cmd hl">/clint:jalankan</span><span class="cmd">/clint:tinjau</span><span class="cmd">/clint:siapkan-project</span></div>
 </div>
 <div class="card term">
  <div class="bar"><i></i><i></i><i></i><span>Claude Code · toko-online</span></div>
  <div class="lines">
   <p><b>›</b> /clint:jalankan MOB-10</p>
   <p class="ok">✓ rencana 4 PR dibuat dari PRD, SAD, dan API contract</p>
   <p class="ok">✓ PR-1 → MR !127 · tinjauan berlapis lulus</p>
   <p class="ok">✓ PR-2 → MR !128 · 2 temuan reviewer-senior diperbaiki</p>
   <p class="ok">✓ PR-3 → MR !129 · E2E 4/4 lulus</p>
   <p class="run">! PR-4 tertahan · test gagal, perubahan disimpan sebagai wip</p>
   <div class="done">Beres: 3 MR siap Anda review, 1 perlu keputusan Anda. Merge berurutan !127 → !128.</div>
  </div>
 </div>
</div>
<div class="foot"><span>14 agent senior · mobile, web & backend · menu bar & suara tanpa token</span><span>github.com/auliarampit/clint-agent</span></div>
""", css="""
.cmd{font:500 15px var(--fm);padding:8px 14px;border-radius:10px;border:1px solid var(--line);background:var(--bg2);color:var(--muted)}
.cmd.hl{border-color:var(--dawn);color:var(--dawn2);background:var(--dawn-soft)}
.term{overflow:hidden;box-shadow:0 30px 60px -30px #000}
.term .bar{display:flex;align-items:center;gap:7px;padding:12px 16px;border-bottom:1px solid var(--line);font:13px var(--fm);color:var(--dim)}
.term .bar i{width:11px;height:11px;border-radius:50%;background:#3A465A}.term .bar span{margin-left:8px}
.lines{padding:22px 24px;display:grid;gap:11px;font:15px/1.4 var(--fm)}
.lines b{color:var(--dawn)}.lines .run{color:var(--warn)}.ok{color:var(--ok)}.run{color:var(--dawn2)}.run span{color:var(--dim);margin-left:8px}.dim{color:var(--dim)}
.done{margin-top:10px;padding:14px 16px;border-radius:10px;background:var(--dawn-soft);color:var(--ink);font:500 15px var(--fb)}
"""))

# 2. Alur jalankan -----------------------------------------------------------------------------
GAMBAR.append(halaman("alur-jalankan", """
<div class="eyebrow">/clint:jalankan</div>
<h2>Satu perintah, satu rantai kerja</h2>
<p class="sub">Tugas kecil langsung jadi 1 PR. Modul besar dibuatkan rencana, PR yang tidak saling bergantung dikerjakan paralel.</p>
<div class="flow">
 <div class="st"><span class="n">1</span><b>Tarik terbaru</b><small>dev, docs, design</small></div><div class="ar">→</div>
 <div class="st"><span class="n">2</span><b>Rencana</b><small>perencana</small><span class="pill sonnet">Sonnet</span></div><div class="ar">→</div>
 <div class="st"><span class="n">3</span><b>Kode</b><small>pengembang</small><span class="pill opus">Opus</span></div><div class="ar">→</div>
 <div class="st wide"><span class="n">4</span><b>Tinjauan paralel</b>
   <ul><li>peninjau <em>sesuai rencana &amp; aturan?</em></li><li>reviewer-senior <em>clean code &amp; arsitektur?</em></li>
   <li>auditor-keamanan <em>OWASP, bila relevan</em></li><li>penyelaras-desain <em>sama dengan prototype?</em></li><li>aksesibilitas &amp; performa <em>WCAG 2.2, Core Web Vitals</em></li><li>database &amp; kontrak API <em>migrasi aman, sesuai kontrak</em></li></ul></div><div class="ar">→</div>
 <div class="st"><span class="n">5</span><b>E2E</b><small>penguji</small><span class="pill sonnet">Sonnet</span></div><div class="ar">→</div>
 <div class="st hl"><span class="n">6</span><b>MR</b><small>stage eksplisit, push, verifikasi</small></div>
</div>
<div class="loop">↺ temuan wajib dikirim balik ke pengembang · maksimal 2 putaran · masih gagal → berhenti, tanpa MR</div>
<div class="row">
 <div class="mini"><b>Paralel bila aman</b><span>PR tanpa dependensi jalan bersamaan (maks 3), masing-masing di worktree sendiri.</span></div>
 <div class="mini"><b>Bertumpuk bila perlu</b><span>PR yang bergantung dibangun di atas branch dependensinya; deskripsi MR menyebut urutan merge.</span></div>
 <div class="mini"><b>Satu laporan di akhir</b><span>Tautan MR, apa yang berubah bagi pengguna, dan yang perlu Anda putuskan.</span></div>
</div>
""", w=1280, h=870, css="""
.flow{display:flex;align-items:stretch;gap:10px;margin-top:34px}
.st{flex:1;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 14px;display:flex;flex-direction:column;gap:6px;position:relative}
.st.wide{flex:2.3}.st.hl{border-color:var(--dawn);background:linear-gradient(180deg,var(--dawn-soft),var(--card))}
.st .n{font:500 12px var(--fm);color:var(--dawn)}.st b{font:700 18px var(--fd)}.st small{color:var(--muted);font-size:13.5px}
.st .pill{align-self:flex-start;margin-top:auto}
.st ul{list-style:none;padding:0;display:grid;gap:6px;font-size:14px}.st li{padding:6px 9px;border-radius:8px;background:var(--bg2)}
.st em{display:block;font-style:normal;color:var(--muted);font-size:12.5px}
.ar{align-self:center;color:var(--dawn);font:600 22px var(--fb)}
.loop{margin:16px 0 0 34%;width:46%;text-align:center;padding:10px;border:1.5px dashed var(--dawn);border-radius:12px;color:var(--dawn2);font:500 14px var(--fm)}
.row{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:26px}
.mini{display:grid;gap:4px;padding:14px 16px;border-left:3px solid var(--line)}.mini b{font-weight:600}.mini span{color:var(--muted);font-size:14.5px}
"""))

# 3. Tim agent ---------------------------------------------------------------------------------
agen = [("perencana", "Memecah modul jadi rencana per PR dari PRD, SAD, STD, API contract, prototype", "sonnet"),
        ("pengembang", "Menulis kode satu PR, lint, typecheck, test", "opus"),
        ("peninjau", "Sesuai rencana, dokumen, dan aturan project?", "sonnet"),
        ("reviewer-senior", "Clean code dan clean architecture", "opus"),
        ("auditor-keamanan", "OWASP Mobile Top 10, MASVS, API Security", "opus"),
        ("penyelaras-desain", "Selisih tampilan dengan prototype", "sonnet"),
        ("penguji", "E2E happy path + error path", "sonnet"),
        ("pemulih-pipeline", "Memperbaiki CI yang gagal dari penyebabnya", "opus"),
        ("pelacak-perubahan", "Apa yang berubah di docs, design, dev", "sonnet"),
        ("auditor-aksesibilitas", "WCAG 2.2 AA: keyboard, fokus, label, kontras", "sonnet"),
        ("auditor-performa", "Core Web Vitals, bundle, render", "sonnet"),
        ("auditor-database", "Migrasi aman, integritas, indeks, N+1", "opus"),
        ("auditor-kontrak-api", "Implementasi vs API contract", "sonnet"),
        ("penjaga", "MR, pipeline, branch, worktree, disk", "haiku")]
kartu = "".join(f'<div class="ag card"><div class="t"><b>{n}</b><span class="pill {m}">{m.capitalize()}</span></div><p>{d}</p></div>' for n, d, m in agen)
GAMBAR.append(halaman("tim-agent", f"""
<div class="eyebrow">Tim di balik layar</div>
<h2>14 agent senior, dipanggil otomatis</h2>
<p class="sub">Anda tidak memanggil agent. Perintah clint yang menugaskan mereka, dengan model yang sesuai bebannya.</p>
<div class="grid">{kartu}</div>
<div class="legend"><span><span class="pill opus">Opus</span> menulis dan menilai kode</span><span><span class="pill sonnet">Sonnet</span> membaca, meninjau, menguji</span><span><span class="pill haiku">Haiku</span> mengumpulkan status</span></div>
""", css=""".legend{display:flex;gap:28px;margin-top:26px;color:var(--muted);font-size:15px}.legend .pill{margin-right:8px}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;margin-top:30px}
.ag{padding:14px;display:grid;gap:8px;align-content:start;min-height:150px}
.ag .t{display:flex;flex-direction:column;gap:7px;align-items:flex-start}.ag b{font:700 14px var(--fd);overflow-wrap:anywhere}
.ag p{color:var(--muted);font-size:13px;line-height:1.4}
"""))

# 4. Menu bar ----------------------------------------------------------------------------------
GAMBAR.append(halaman("menu-bar", """
<div style="display:grid;grid-template-columns:.8fr 1.2fr;gap:44px;height:100%">
 <div style="display:grid;gap:18px;align-content:center">
  <div class="eyebrow">Menu bar Mac</div>
  <h2>Lihat agent bekerja tanpa membuka apa pun</h2>
  <p class="sub" style="font-size:17px">Cincin oranye menyala selama agent bekerja, termasuk sesi di VS Code. Klik untuk melihat kemajuan, sesi, dan hal yang menunggu.</p>
  <div class="states">
   <div><span class="ic"><span class="logo s">c</span></span><b>3</b><small>hal menunggu</small></div>
   <div><span class="ic spin"><span class="logo s">c</span></span><b>PR-2/4</b><small>agent bekerja</small></div>
   <div><span class="ic"><span class="logo s">c</span></span><b>✓</b><small>semua aman</small></div>
   <div><span class="ic"><span class="logo s">c</span></span><b>!</b><small>ada yang gagal</small></div>
  </div>
  <p style="color:var(--dim);font:13px var(--fm)">Membaca file lokal · tanpa token</p>
 </div>
 <div class="desk">
  <div class="mb"><span class="apps"><b>Code</b> File Edit View</span><span class="r"><span class="me"><span class="ring"><span class="logo s">c</span></span>PR-2/4</span><span>Wi-Fi</span><span>Rab 7 Okt 11.40</span></span></div>
  <div class="menu">
   <div class="hd"><span class="logo m">c</span><div><b>Sedang bekerja</b><small>jalankan MOB-10 · mulai 11.21</small></div></div>
   <hr><small class="sec">Agent sedang bekerja</small>
   <p class="it"><b>PR-2 dari 4</b> · ditinjau reviewer-senior</p>
   <div class="pb"><i></i></div>
   <small class="it dim">PR-1 → MR !127 · PR-3 dan PR-4 menunggu</small>
   <p class="it"><span class="dot o"></span>toko-online · mobile — bekerja · 12 mnt <span class="chev">›</span></p>
   <p class="it">Lihat sesi di Claude Code</p>
   <hr><p class="it">Hal yang menunggu (3) <span class="chev">›</span></p>
   <hr><p class="it">Buka laporan terakhir</p><p class="it">Cek semua project (2 aktif)</p>
   <p class="it">Cek project <span class="chev">›</span></p><p class="it">Halo Clint (perintah suara)</p>
   <hr><p class="it">Pengaturan <span class="chev">›</span></p>
  </div>
 </div>
</div>
""", css="""
.states{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.states div{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;background:var(--card);border:1px solid var(--line)}
.states b{font:600 15px var(--fb)}.states small{color:var(--muted);font-size:13px;margin-left:auto}
.ic{display:grid;place-items:center}.spin .logo{box-shadow:0 0 0 2px #000,0 0 0 3.5px rgba(240,149,74,.3)}
.spin{position:relative}.spin:after{content:"";position:absolute;inset:-3.5px;border-radius:50%;border:2px solid transparent;border-top-color:var(--dawn);border-right-color:var(--dawn)}
.desk{border-radius:18px;overflow:hidden;position:relative;background:radial-gradient(120% 90% at 85% 10%,#C97A4A 0%,transparent 55%),linear-gradient(160deg,#3B5B8C,#1E2A44);border:1px solid var(--line)}
.mb{height:34px;display:flex;align-items:center;padding:0 14px;background:rgba(20,24,30,.5);backdrop-filter:blur(20px);font:500 14px var(--fb)}
.mb .apps b{margin-right:10px}.mb .r{margin-left:auto;display:flex;gap:16px;align-items:center}
.me{display:flex;align-items:center;gap:8px;padding:2px 8px;border-radius:6px;background:rgba(255,255,255,.18)}
.ring{position:relative;display:grid;place-items:center}.ring:after{content:"";position:absolute;inset:-3.5px;border-radius:50%;border:2px solid transparent;border-top-color:var(--dawn);border-right-color:var(--dawn)}
.menu{position:absolute;top:44px;right:120px;width:360px;padding:8px;border-radius:12px;background:rgba(36,40,48,.9);backdrop-filter:blur(30px);border:1px solid rgba(255,255,255,.12);box-shadow:0 20px 50px rgba(0,0,0,.45);font-size:14px}
.hd{display:flex;gap:12px;align-items:center;padding:8px 10px 10px}.hd b{font-size:16px;display:block}.hd small{color:var(--muted)}
.menu hr{border:0;border-top:1px solid rgba(255,255,255,.1);margin:5px 8px}
.sec{display:block;color:var(--muted);font-size:12px;padding:4px 10px}
.it{padding:5px 10px;display:flex;align-items:center;gap:8px}.it.dim{color:var(--muted);font-size:12.5px}
.chev{margin-left:auto;color:var(--muted)}
.pb{height:6px;margin:4px 10px 6px;border-radius:3px;background:rgba(255,255,255,.15)}.pb i{display:block;height:100%;width:38%;border-radius:3px;background:#fff}
.dot{width:9px;height:9px;border-radius:50%}.dot.o{background:var(--dawn)}
"""))

# 5. Laporan pagi ------------------------------------------------------------------------------
GAMBAR.append(halaman("laporan-pagi", """
<div style="display:grid;grid-template-columns:.75fr 1.25fr;gap:44px;height:100%">
 <div style="display:grid;gap:16px;align-content:center">
  <div class="eyebrow">/clint:cek semua · 08.00</div>
  <h2>Satu laporan pagi untuk semua project aktif</h2>
  <p class="sub" style="font-size:17px">Docs, design, feedback QA, MR, dan pipeline dicek bersamaan. Hanya butir yang PIC-nya Anda. Dikelompokkan per tindakan.</p>
  <ul class="pts"><li>Feedback QA yang masih open, sampai rinciannya</li><li>Tombol Salin untuk perintah lanjutan</li><li>Kalimat inti dibacakan, notifikasi muncul</li></ul>
 </div>
 <div class="rep card">
  <div class="top"><span class="logo m terang">c</span><span class="eb">clint · Rabu, 7 Oktober 2026 · 08.02</span></div>
  <h1>Selamat pagi. <em>3 hal</em> menunggu hari ini.</h1>
  <p class="lead">Dua bisa langsung dikerjakan, satu MR menunggu review Anda. Pipeline aman di 2 project.</p>
  <div class="chips"><span class="ch a">toko-online · mobile</span><span class="ch b">portal-admin</span></div>
  <h3>Perlu dikerjakan <span>2</span></h3>
  <div class="it do"><p>Daftar produk belum bisa ditarik untuk dimuat ulang.</p><div class="m"><span class="ch a">mobile</span>Feedback UI #8</div><div class="c"><code>/clint:jalankan feedback UI #8</code><button>Salin</button></div></div>
  <div class="it do"><p>Field harga di API contract berganti nama, layar admin belum menyesuaikan.</p><div class="m"><span class="ch b">portal-admin</span>API-PRICE-3</div></div>
  <h3>Perlu Anda cek <span>1</span></h3>
  <div class="it ck"><p>Ganti email dengan OTP siap direview.</p><div class="m"><span class="ch a">mobile</span>MR !128 · tinjauan otomatis lulus</div></div>
  <div class="pl"><span class="g">Pipeline aman</span><span class="g">4 butir milik rekan dilewati</span><span class="w">Disk tinggal 18 GB</span></div>
 </div>
</div>
""", w=1280, h=720, css="""
.pts{display:grid;gap:8px;padding-left:18px;color:var(--muted)}
.rep{padding:24px 28px;display:grid;gap:10px;align-content:start;align-self:center;background:#F6F8FB;color:#18212D;border:0}
.rep .top{display:flex;gap:12px;align-items:center}.logo.terang{box-shadow:0 0 0 3px #F6F8FB,0 0 0 5px var(--dawn);color:#fff}.rep .eb{font:500 12px var(--fm);letter-spacing:.06em;text-transform:uppercase;color:#5A6676}
.rep h1{font:800 32px/1.15 var(--fd)}.rep h1 em{font-style:normal;color:#C9671E}.lead{color:#3A4656;font-size:15.5px}
.chips{display:flex;gap:8px}.ch{font:500 12px var(--fm);padding:3px 9px;border-radius:999px}.ch.a{background:#E2EAF7;color:#2D5DA8}.ch.b{background:#EEE5F7;color:#7A4AA8}
.rep h3{font:600 14.5px var(--fb);margin-top:4px}.rep h3 span{font:500 12px var(--fm);color:#5A6676;margin-left:6px}
.it{background:#E9EEF4;border-radius:10px;padding:10px 14px;display:grid;gap:5px;border-left:4px solid #C9671E}.it.ck{border-left-color:#A86A0B}
.it p{font-size:14.5px}.m{display:flex;gap:8px;align-items:center;color:#5A6676;font-size:12.5px}
.c{display:flex;gap:8px;align-items:center}.c code{font:12.5px var(--fm);background:#fff;border:1px solid #D6DDE7;border-radius:6px;padding:2px 8px}
.c button{font:500 12px var(--fb);border:1px solid #D6DDE7;background:none;border-radius:6px;padding:2px 9px}
.pl{display:flex;gap:8px;flex-wrap:wrap}.pl span{font-size:12.5px;padding:4px 10px;border-radius:999px}.g{background:#E1F1E9;color:#2F7D5B}.w{background:#FBF0D9;color:#A86A0B}
"""))

# 6. Mode JARVIS -------------------------------------------------------------------------------
GAMBAR.append(halaman("mode-jarvis", """
<div class="eyebrow">Mode JARVIS</div>
<h2>Menyapa, bersuara, dan bisa dipanggil</h2>
<p class="sub">Semua jalan di Mac Anda. Suara dan menu bar tidak memakai token. Agent tidak bergerak tanpa perintah.</p>
<div class="cols">
 <div class="col card"><span class="big">08.00</span><b>Sapaan pagi</b>
  <p>Senin–Jumat, semua project aktif dicek dalam satu sesi, mode baca saja.</p>
  <div class="toast"><span class="logo s">c</span><div><b>clint</b><small>Selamat pagi. 3 hal menunggu hari ini, pipeline aman.</small></div></div>
  <small class="ft">Layar laporan terbuka · kalimat inti dibacakan</small></div>
 <div class="col card"><span class="big">“Hey Siri”</span><b>Perintah suara</b>
  <div class="chat"><p class="u">Hey Siri, Halo Clint</p><p class="c">Halo, ada yang bisa saya bantu?</p><p class="u">Cek project toko online</p><p class="c">Siap, saya periksa. Laporannya menyusul.</p></div>
  <small class="ft">Dikte bahasa Indonesia · suara Damayanti</small></div>
 <div class="col card"><span class="big">Tetap</span><b>Aturan aman</b>
  <ul><li>Merge selalu oleh manusia</li><li>Tanpa <code>git add -A</code>, screenshot tidak ikut commit</li><li>Sapaan pagi tidak bisa edit, commit, atau push</li><li>Hanya tugas milik Anda yang dilaporkan</li><li>Bisukan sampai besok dari menu bar</li></ul></div>
</div>
""", css="""
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:28px}
.col{padding:22px;display:flex;flex-direction:column;gap:10px;min-height:380px}
.big{font:800 34px/1 var(--fd);color:var(--dawn)}.col b{font:700 19px var(--fd)}.col p{color:var(--muted);font-size:15px}
.toast{margin-top:8px;display:flex;gap:10px;align-items:flex-start;padding:12px;border-radius:12px;background:rgba(255,255,255,.07);border:1px solid var(--line)}
.toast small{display:block;color:var(--muted);font-size:13.5px}
.ft{margin-top:auto;color:var(--dim);font:12.5px var(--fm)}
.chat{display:grid;gap:8px;margin-top:4px}.chat p{padding:8px 12px;border-radius:12px;font-size:14px;max-width:85%}
.chat .u{justify-self:end;background:#2D5DA8;color:#fff}.chat .c{background:var(--dawn-soft);color:var(--dawn2)}
.col ul{padding-left:18px;display:grid;gap:8px;color:var(--muted);font-size:14.5px}.col code{font:13px var(--fm);color:var(--ink)}
"""))


def main():
    if not BROWSER:
        raise SystemExit("Butuh Microsoft Edge atau Google Chrome untuk memotret.")
    tmp = tempfile.mkdtemp()
    for nama, html, w, h in GAMBAR:
        src = os.path.join(DIR, f"{nama}.html")
        open(src, "w", encoding="utf-8").write(html)
        out = os.path.join(OUT, f"{nama}.png")
        if os.path.exists(out):
            os.remove(out)
        # Edge/Chrome headless di macOS kadang tidak keluar sendiri: tunggu file jadi, lalu hentikan.
        pr = subprocess.Popen([BROWSER, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                               "--disable-extensions", "--hide-scrollbars", f"--user-data-dir={tmp}",
                               "--force-device-scale-factor=2", f"--window-size={w},{h}", "--virtual-time-budget=4000",
                               f"--screenshot={out}", "file://" + src], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            if os.path.exists(out) and os.path.getsize(out) > 0:
                time.sleep(1); break
            time.sleep(1)
        pr.kill(); pr.wait()
        print("✓" if os.path.exists(out) else "✗", out)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
