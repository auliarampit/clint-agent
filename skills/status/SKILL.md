---
name: status
description: Satu perintah untuk tahu kondisi kerja di project ini, atau di semua project aktif ("status all", "cek semua project") dengan satu layar laporan gabungan — tarik docs/designs/base branch dan cocokkan perubahannya dengan kode, plus MR open, pipeline gagal, branch tertinggal, worktree, dan sisa disk. Mode sprint menjawab sisa tugas sprint dari sprint tracker. Pakai di awal hari, saat user bertanya "ada update apa?", "apa yang perlu saya urus?", "sprint saat ini yang belum selesai apa?", atau "sisa tugas sprint 3".
argument-hint: [all | nama project | sprint [N ...|aktif] [saya|<nama>]] [since <periode>] [--json <path>] [--no-screen]
---

## Mode project ini (default)

Argumen berupa **nama project lain** (mis. `/clint:status toko-online`) → cari path-nya dengan
`bash "$R/scripts/find-project.sh" "<nama>"` (R seperti di mode `all`), lalu jalankan mode
`all` untuk path itu saja.


1. Jalankan bersamaan agent `change-tracker` (teruskan periode bila disebut) dan `status-reporter`.
2. Susun laporan sesuai **Gaya laporan** di bawah. Isinya mencakup: update docs/design dan
   dampaknya ke kode, feedback/bug QA yang masih open untuk project ini (walau file-nya tidak
   berubah belakangan ini), MR (pipeline gagal, komentar baru, menunggu review), dan
   bersih-bersih/disk bila ada yang perlu.
3. Tutup dengan baris **Berikutnya** (lihat Gaya laporan). Jangan menyuruh user memanggil agent.

## Mode `sprint` ("sprint saat ini yang belum selesai apa", "sisa tugas sprint 3")

Dijawab langsung di sesi ini, **tanpa agent** (hanya membaca dokumen, murah).

1. Lokasi: `docs.pic` di `.claude/clint.json`. Kosong/`TIDAK ADA` → tanya user letak sprint tracker-nya dan
   tawarkan menyimpannya lewat `/clint:setup sync`. Bila path berada di repo terkait (`relatedRepos`), tarik
   dulu (`git -C <repo> pull --ff-only` bila bersih).
2. Pilih file: nomor disebut (`sprint 3`, `S09`, `sprint 1 2 3 4`) → file sprint bernomor itu (mis. `s03.md`,
   `sprint-3*.md`); tidak disebut atau `aktif` → sprint yang `window`/tanggalnya mencakup hari ini; tidak ada → di antara
   yang bertanda `status: Active`/`Aktif`, nomor terbesar (tanda Active di sprint lama sering lupa diubah);
   tidak ada juga → nomor terbesar. Sebut file yang dipakai di laporan. Beberapa nomor → jawab per sprint.
3. Baca hemat: frontmatter + judul + baris tabel/checklist saja (`grep -nE '^(#|\||- \[)' <file>`), bukan file
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
7. **Berikutnya**: butir milik user yang paling mendesak sebagai perintah siap ketik, mis.
   `/clint:develop MOD-AD-04 sisa QA (docs/sprints/s09.md)` atau `/clint:test e2e !<n>`.

Mode ini hanya membaca. Memperbarui tracker (centang, status, PIC) dikerjakan lewat `/clint:docs`.

## Mode `all` ("cek semua project")

1. Daftar project: bila argumen menyebut path project, pakai **hanya** itu. Bila tidak, project aktif:
   `R=$(ls -d ~/.claude/plugins/cache/clint/clint/*/ | sort -V | tail -1); bash "$R/scripts/active-projects.sh" 3`
   (user boleh menyebut project tambahan atau jumlah hari lain).
2. Untuk **setiap** project, jalankan `change-tracker` dan `status-reporter` — semuanya dalam **satu
   pesan** (paralel). Beri tiap agent path project-nya; agent bekerja dengan `git -C <path>` dan
   membaca `<path>/.claude/clint.json`.
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
    "berikutnya":"/clint:develop … (atau \"Selesai semua pekerjaan.\")"}
   ```
   Butir mengikuti gaya laporan di bawah; kelompok kosong ditulis `[]`. `gagal` = pipeline/pekerjaan
   gagal (memberi ikon merah di menu bar); `url` diisi untuk butir MR. Salinan terakhir juga ditulis ke
   `~/Library/Logs/clint/terakhir.json` (dibaca menu bar).
4. Kecuali ada `--no-screen` (dipakai sapaan pagi, yang merender sendiri): render dan buka layarnya,
   `python3 "$R/scripts/render-report.py" <json> "${json%.json}.html" && open "${json%.json}.html"`,
   lalu di chat cukup kalimat inti + "laporan sudah terbuka".
5. Kecuali ada `--no-screen`: tulis kabar suara seperti di bawah. (Sapaan pagi membacakan `kalimat` dari JSON.)

## Gaya laporan ke user (wajib)

Semua teks untuk user (chat, `judul`, `kalimat`, `lead`, butir JSON, kabar suara) memakai bahasa user
(baris *Bahasa clint* di konteks sesi; default English). Contoh di bawah berbahasa Indonesia; terjemahkan
bila bahasa user English. Nama kunci JSON tetap seperti di atas.

**Singkat dan manusiawi.** Seperti rekan kerja mengabari lewat chat:

- Buka dengan sapaan sesuai waktu lalu kalimat inti, mis. "Selamat pagi. Ada 3 hal untuk mobile
  hari ini, 2 bisa langsung dikerjakan."
- Lalu daftar pendek, satu baris per hal, bahasa sehari-hari, sebut nama layar/fitur:
  "Daftar produk belum bisa ditarik untuk dimuat ulang (feedback #8)."
- Yang tidak perlu tindakan cukup satu baris penutup, mis. "Selain itu aman: MR dan pipeline bersih."
- **Baris terakhir wajib: "Berikutnya"** — satu perintah siap ketik untuk pekerjaan berikutnya yang paling
  penting, lengkap dengan sumbernya, mis.:
  `Berikutnya: /clint:develop perbaiki BUG-092 tombol Verifikasi Customer (docs/qa/feedback/feedback-ui.md)`
  `Berikutnya: /clint:develop docs/plans/mob-10.md PR-2`
  Urutan memilih: PR berikutnya dari rencana yang sedang dikerjakan → butir *Perlu perhatian* → butir
  *Perlu dikerjakan* teratas di laporan terakhir (`~/Library/Logs/clint/terakhir.json`) → MR yang menunggu
  review (sebut "review dan merge !n" tanpa perintah). Tidak ada sama sekali → tulis **"Selesai semua
  pekerjaan."**
- Tanpa judul besar, tanpa tabel, tanpa hash commit/path kecuali benar-benar diperlukan.
  Maksimal ±10 baris.

## Kabar suara (wajib, di akhir)

Tulis **satu kalimat inti** (maks ±20 kata, bahasa lisan, tanpa simbol/kode/path) ke file kabar;
hook akan menampilkannya sebagai notifikasi dan membacakannya:

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar.txt"
```
Contoh: "Selamat pagi. Ada dua hal untuk mobile hari ini, pipeline aman."
