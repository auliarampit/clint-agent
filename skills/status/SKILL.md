---
name: status
description: Satu perintah untuk tahu kondisi kerja di project ini, atau di semua project aktif ("status all", "cek semua project") dengan satu layar laporan gabungan — tarik docs/designs/base branch dan cocokkan perubahannya dengan kode, plus MR open/Draft, pipeline gagal, branch tertinggal, worktree, dan sisa disk. Mode plan menjawab sisa PR di rencana (selesai, setengah jalan, siap, dikerjakan sesi lain) dan modul yang belum direncanakan; mode sprint menjawab sisa tugas sprint dari sprint tracker. Pakai di awal hari, saat user bertanya "ada update apa?", "apa yang perlu saya urus?", "sisa tugas di rencana apa?", "modul mana yang belum direncanakan?", "sprint saat ini yang belum selesai apa?", atau "sisa tugas sprint 3".
argument-hint: [all | nama project | plan [rencana|modul] | sprint [N ...|aktif] [saya|<nama>]] [since <periode>] [--json <path>] [--no-screen]
---

## Mode project ini (default)

Argumen berupa **nama project lain** (mis. `/clint:status toko-online`) → cari path-nya dengan
`bash "$R/scripts/find-project.sh" "<nama>"` (R seperti di mode `all`), lalu jalankan mode
`all` untuk path itu saja.


`R` = path plugin dan `<sid>` = id sesi, dari baris *Sesi clint* di konteks sesi (cadangan
`R=$(cat ~/.config/clint/root)`). Teruskan `R` di prompt agent.

1. **Tarik semua repo dulu** (tanpa token): `bash "$R/scripts/sync-repos.sh" .` menarik repo kerja dan semua
   `relatedRepos` (docs, design, api) paralel. Repo `fetch-saja`/`gagal-tarik` disebut di laporan apa adanya.
2. Lalu jalankan bersamaan agent `change-tracker` (teruskan periode bila disebut) dan `status-reporter`, dan di
   sesi ini (tanpa token) `python3 "$R/scripts/plan-status.py" --session <sid>` bila `docs.plans` diatur.
   Pengumpul kedua agent memakai hasil tarikan langkah 1 (tidak menarik ulang).
3. Susun laporan sesuai **Gaya laporan** di bawah. Isinya mencakup: update docs/design dan
   dampaknya ke kode, feedback/bug QA yang masih open untuk project ini (walau file-nya tidak
   berubah belakangan ini), MR (pipeline gagal, komentar baru, menunggu review dengan tanda ⚠ > 3 jam / 🔴 > 5 jam sesuai
   eskalasi standar Badr, **Draft** yang menunggu E2E),
   rencana yang masih punya PR tersisa (satu baris per rencana: n/total selesai + yang siap), dan
   bersih-bersih/disk bila ada yang perlu.
4. Simpan laporan project ini untuk menu bar tanpa menyentuh project lain: tulis JSON (bentuk di mode `all`,
   satu project) ke `~/Library/Logs/clint/<YYYY-MM-DD-HHMM>-<nama>.json` dengan tool Write, lalu
   `python3 "$R/scripts/update-report.py" merge <file>`.
5. Tutup dengan blok **Berikutnya** (lihat Gaya laporan). Jangan menyuruh user memanggil agent.

## Mode `plan` ("sisa tugas di rencana", "PR mana yang belum", "modul apa yang belum direncanakan")

Dijawab langsung di sesi ini, **tanpa agent**.

1. `bash "$R/scripts/sync-repos.sh" .` dulu (rencana dan PRD bisa ada di repo docs), lalu
   `python3 "$R/scripts/plan-status.py" [<rencana> ...] --session <sid>`. Tanpa argumen: semua rencana di
   `docs.plans`; ID/nama modul disebut → rencana yang cocok (`grep -il <ID> <docs.plans>/*.md`).
2. **Belum direncanakan**: daftar modul di `docs.requirements` (nama file PRD/modul, mis.
   `ls <requirements>/prd*/ <requirements>/2-modules/ 2>/dev/null`, atau judul modul ber-ID di PRD), lalu
   cocokkan ID-nya dengan `grep -ril <ID> <docs.plans>`. Modul tanpa rencana masuk kelompok ini. Butir
   feedback/bug yang masih open dan belum disebut di rencana mana pun disebut sebagai jumlah per modul, bukan
   satu per satu.
3. Laporan singkat: satu kalimat inti (mis. "3 rencana masih berjalan, 2 modul belum direncanakan"), lalu per
   rencana: `n/total selesai`, PR yang 🔄 dikerjakan sesi lain, ⏸️ setengah jalan/tertahan, 🧪 Draft, siap; lalu
   modul yang belum direncanakan. Rencana yang semuanya ✅ cukup satu baris "Selesai semua: …".
4. **Berikutnya**: dari keluaran skrip (sudah bertanda paralel/urutan); modul belum direncanakan →
   `[siap] /clint:develop <ID-modul>` (develop memanggil planner). Status `❔ belum tercatat` →
   `/clint:docs perbarui Status PR di <rencana> dari git log`, kecuali skrip menandainya sedang dikerjakan sesi lain.

Mode ini hanya membaca. Status di file rencana ditulis oleh `develop` saat commit, atau lewat `/clint:docs`.

## Mode `sprint` ("sprint saat ini yang belum selesai apa", "sisa tugas sprint 3")

Dijawab langsung di sesi ini, **tanpa agent** (hanya membaca dokumen, murah).

1. Lokasi: `docs.pic` di `.claude/clint.json`. Kosong/`TIDAK ADA` → tanya user letak sprint tracker-nya dan
   tawarkan menyimpannya lewat `/clint:setup sync`. Tarik semua repo dulu: `bash "$R/scripts/sync-repos.sh" .`
   (tracker sering ada di repo docs).
2. Pilih file: nomor disebut (`sprint 3`, `S09`, `sprint 1 2 3 4`) → file sprint bernomor itu (mis. `s03.md`,
   `sprint-3*.md`); tidak disebut atau `aktif` → sprint yang `window`/tanggalnya mencakup hari ini; tidak ada → di antara
   yang bertanda `status: Active`/`Aktif`, nomor terbesar (tanda Active di sprint lama sering lupa diubah);
   tidak ada juga → nomor terbesar. Sebut file yang dipakai di laporan. Beberapa nomor → jawab per sprint.
3. `clint.json` punya `"tugas"` → jalankan `python3 "$R/scripts/tugas-saya.py" .` dan pakai keluarannya sebagai
   daftar (filter `saya` sudah diterapkan skrip; sprint bernomor lain → baca file itu seperti langkah berikut).
   Selain itu baca hemat: frontmatter + judul + baris tabel/checklist saja (`grep -nE '^(#|\||- \[)' <file>`), bukan file
   utuh. Butir di luar file sprint (mis. `backlog.md` yang ditandai sprint itu) dibaca hanya bila user memintanya.
4. **Belum selesai** = baris/butir yang punya kolom status selain selesai: emoji ⬜ 🔄 🧪 🐞 🚫, kata
   Open/To Do/In Progress/Belum/Blocked/On QA, atau checklist `- [ ]`. **Selesai** = ✅, Done, Selesai, Merged,
   `- [x]`; `—` berarti tidak berlaku. Ikuti legenda di file itu bila ada.
5. Filter PIC: default semua butir dengan kolom PIC; `saya` → hanya nama di `~/.config/clint/user.json`
   (`name`); nama lain → butir orang itu.
6. Laporan singkat (gaya laporan di bawah): satu kalimat inti (jumlah sisa + sisa hari bila ada `window`), lalu
   dikelompokkan **Terblokir/ada bug** → **Sedang dikerjakan/QA** → **Belum mulai**, satu baris per butir: ID/modul,
   PIC, kolom yang belum selesai. Butir Anda ditandai. Lebih dari ±15 butir → ringkas per epic/PIC dan tawarkan
   rinciannya.
7. **Berikutnya** (aturan skill `develop` bagian 6): butir milik user yang paling mendesak, tanpa yang diklaim sesi lain
   (`~/Library/Logs/clint/kerja/`), sebagai langkah bertanda, mis.
   `/clint:develop MOD-AD-04 sisa QA (docs/sprints/s09.md)` atau `/clint:test e2e !<n>`.

Mode ini hanya membaca. Memperbarui tracker (centang, status, PIC) dikerjakan lewat `/clint:docs`.

## Mode `all` ("cek semua project")

1. Daftar project: bila argumen menyebut path project, pakai **hanya** itu. Bila tidak, project aktif:
   `bash "$R/scripts/active-projects.sh" 3`
   (user boleh menyebut project tambahan atau jumlah hari lain).
2. **Tarik semua repo semua project dulu** dalam satu panggilan Bash (tanpa token):
   `for p in <path ...>; do bash "$R/scripts/sync-repos.sh" "$p" & done; wait`.
   Lalu untuk **setiap** project, jalankan `change-tracker` dan `status-reporter` — semuanya dalam **satu
   pesan** (paralel). Beri tiap agent path project-nya dan `R`; agent bekerja dengan `git -C <path>` dan
   membaca `<path>/.claude/clint.json`. Bersamaan, di sesi ini: `python3 "$R/scripts/plan-status.py" --repo <path>`
   per project yang punya `docs.plans` (tanpa token).
3. Gabungkan menjadi satu laporan dan tulis sebagai JSON ke
   path dari `--json` bila diberikan, selain itu `~/Library/Logs/clint/<YYYY-MM-DD-HHMM>.json`, dengan tool **Write**, bentuknya:
   ```json
   {"tanggal":"Rabu, 7 Oktober 2026 · 08.00",
    "judul":"Selamat pagi. 4 hal menunggu hari ini.",
    "kalimat":"<kalimat inti untuk dibacakan>", "lead":"<1 kalimat pendukung>",
    "proyek":[{"nama":"<nama pendek>","dir":"<path absolut project>","aktif":"kemarin"}],
    "gagal":[{"teks":"Pipeline !123 gagal di lint","proyek":"<nama>","sumber":"MR !123","perintah":"/clint:develop perbaiki pipeline !123","url":"<tautan MR>"}],
    "kerjakan":[{"teks":"<1 kalimat>","proyek":"<nama>","sumber":"<ID/MR>","perintah":"/clint:develop ..."}],
    "cek":[{"teks":"...","proyek":"...","sumber":"MR !123","url":"<tautan MR>"}], "tunggu":[...],
    "aman":["Pipeline aman di 2 project"], "peringatan":["Disk tinggal 18 GB"],
    "rincian":[{"proyek":"<nama>","butir":["<1 baris>"]}],
    "rencana":[{"proyek":"<nama>","nama":"<judul pendek rencana>","selesai":6,"total":7}],
    "berikutnya":[{"proyek":"<nama>","dir":"<path absolut>","langkah":["[paralel] /clint:develop …","[urutan, setelah PR-2] …"]}]}
   ```
   Butir mengikuti gaya laporan di bawah; kelompok kosong ditulis `[]`. `gagal` = pipeline/pekerjaan
   gagal (memberi ikon merah di menu bar); `url` diisi untuk butir MR. Setiap butir wajib punya `proyek`, dan
   `berikutnya` dipisah per project (langkah dari plan-status + butir project itu, aturan *Berikutnya*). `rencana` diisi dari keluaran
   `plan-status.py` (n/total per rencana yang masih berjalan atau baru selesai hari ini); sesi yang sedang berjalan
   dibaca sendiri oleh `render-report.py` dari klaim, tidak ditulis ke JSON. Salinan
   terakhir juga ditulis ke `~/Library/Logs/clint/terakhir.json` (dibaca menu bar); mode ini memang menggantikan
   seluruh isinya karena mencakup semua project aktif.
4. Saring dulu (wajib, tanpa token): `python3 "$R/scripts/update-report.py" saring <json>` membuang butir tanpa
   bukti atau yang menurut sumber tugas sudah diserahkan/selesai (dicatat di `~/Library/Logs/clint/ditolak.log`).
   `merge` sudah menyaring sendiri. Kecuali ada `--no-screen` (dipakai sapaan pagi, yang merender sendiri): render
   dan buka layarnya,
   `python3 "$R/scripts/render-report.py" <json> "${json%.json}.html" && open "${json%.json}.html"`,
   lalu di chat cukup kalimat inti + "laporan sudah terbuka".
5. Kecuali ada `--no-screen`: tulis kabar suara seperti di bawah. (Sapaan pagi membacakan `kalimat` dari JSON.)

## Gaya laporan ke user (wajib)

Semua teks untuk user (chat, `judul`, `kalimat`, `lead`, butir JSON, kabar suara) memakai bahasa user
(baris *Bahasa clint* di konteks sesi; default English). Contoh di bawah berbahasa Indonesia; terjemahkan
bila bahasa user English. Nama kunci JSON tetap seperti di atas.

**Hanya yang valid dan milik user** (berlaku untuk chat dan semua kelompok JSON):
- Butir tugas hanya dari `KERJAKAN` di `tugas-saya.py` (sumber tugas `"tugas"` di `clint.json`); project tanpa
  adapter tidak punya butir tugas. Butir lain masuk laporan hanya bila tindakan berikutnya ada di tangan user dan
  ada buktinya yang bisa diperiksa mesin (MR, hash commit, path file), ditulis persis. Butir agent tanpa bukti, atau yang bertentangan dengan status tracker (mis. "belum ada
  commit" padahal butir 🧪), dibuang, tidak diteruskan.
- `tunggu` hanya untuk hal yang menahan pekerjaan user sendiri (keputusan PM atas pertanyaan user, materi klien).
  Pekerjaan user yang sudah diserahkan ke QA bukan butir `tunggu`; cukup angka di `aman`.
- `cek` hanya untuk selisih konkret yang sudah ditemukan, bukan pertanyaan spekulatif.
- Tidak ada butir tersisa untuk sebuah project → `judul`/kalimat chat: **"Tidak ada tugas lagi."**, dan blok
  *Berikutnya* project itu juga kosong.

**Singkat dan manusiawi.** Seperti rekan kerja mengabari lewat chat:

- Buka dengan sapaan sesuai waktu lalu kalimat inti, mis. "Selamat pagi. Ada 3 hal untuk mobile
  hari ini, 2 bisa langsung dikerjakan."
- Lalu daftar pendek, satu baris per hal, bahasa sehari-hari, sebut nama layar/fitur:
  "Daftar produk belum bisa ditarik untuk dimuat ulang (feedback #8)."
- Yang tidak perlu tindakan cukup satu baris penutup, mis. "Selain itu aman: MR dan pipeline bersih."
- **Blok terakhir wajib: "Berikutnya"**, aturannya di skill `develop` bagian 6 (*Berikutnya*): beberapa
  langkah bertanda `[paralel]`/`[siap]`/`[urutan, setelah X]`/`[lanjutkan]`/`[E2E]`/`[terblokir]`, hanya untuk
  project sesi ini, PR yang dikerjakan sesi lain tidak disarankan. Mode `all`: satu blok per project, maks 3
  langkah per project. Contoh langkah dari feedback:
  `[siap] /clint:develop perbaiki BUG-092 tombol Verifikasi Customer (docs/qa/feedback/feedback-ui.md)`.
  MR Draft milik user: `[E2E] /clint:test e2e !<n>`, atau `[E2E] /clint:test e2e draft` bila lebih dari satu.
- Tanpa judul besar, tanpa tabel, tanpa hash commit/path kecuali benar-benar diperlukan.
  Maksimal ±10 baris.

## Kabar suara (wajib, di akhir)

Tulis **satu kalimat inti** (maks ±20 kata, bahasa lisan, tanpa simbol/kode/path) ke file kabar;
hook akan menampilkannya sebagai notifikasi dan membacakannya:

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar-<sid>.txt"
```
Contoh: "Selamat pagi. Ada dua hal untuk mobile hari ini, pipeline aman."
