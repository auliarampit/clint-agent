---
name: cek
description: Satu perintah untuk tahu kondisi kerja di project ini, atau di semua project aktif ("cek semua project") dengan satu layar laporan gabungan — tarik docs/designs/base branch dan cocokkan perubahannya dengan kode, plus MR open, pipeline gagal, branch tertinggal, worktree, dan sisa disk. Pakai di awal hari, saat user bertanya "ada update apa?" atau "apa yang perlu saya urus?".
argument-hint: [semua] [sejak <periode>]
---

## Mode project ini (default)

1. Jalankan bersamaan agent `pelacak-perubahan` (teruskan periode bila disebut) dan `penjaga`.
2. Susun laporan sesuai **Gaya laporan** di bawah. Isinya mencakup: update docs/design dan
   dampaknya ke kode, feedback/bug QA yang masih open untuk project ini (walau file-nya tidak
   berubah belakangan ini), MR (pipeline gagal, komentar baru, menunggu review), dan
   bersih-bersih/disk bila ada yang perlu.
3. Langkah berikutnya berupa perintah `/clint:jalankan ...`. Jangan menyuruh user memanggil agent.

## Mode `semua` ("cek semua project")

1. Daftar project aktif:
   `R=$(ls -d ~/.claude/plugins/cache/clint/clint/*/ | sort -V | tail -1); bash "$R/scripts/proyek-aktif.sh" 3`
   (user boleh menyebut project tambahan atau jumlah hari lain).
2. Untuk **setiap** project, jalankan `pelacak-perubahan` dan `penjaga` — semuanya dalam **satu
   pesan** (paralel). Beri tiap agent path project-nya; agent bekerja dengan `git -C <path>` dan
   membaca `<path>/.claude/clint.json`.
3. Gabungkan menjadi satu laporan dan tulis sebagai JSON ke
   `~/Library/Logs/clint/<YYYY-MM-DD>.json` dengan tool **Write**, bentuknya:
   ```json
   {"tanggal":"Rabu, 7 Oktober 2026 · 08.00",
    "judul":"Selamat pagi. 4 hal menunggu hari ini.",
    "kalimat":"<kalimat inti untuk dibacakan>", "lead":"<1 kalimat pendukung>",
    "proyek":[{"nama":"<nama pendek>","aktif":"kemarin"}],
    "kerjakan":[{"teks":"<1 kalimat>","proyek":"<nama>","sumber":"<ID/MR>","perintah":"/clint:jalankan ..."}],
    "cek":[...], "tunggu":[...],
    "aman":["Pipeline aman di 2 project"], "peringatan":["Disk tinggal 18 GB"],
    "rincian":[{"proyek":"<nama>","butir":["<1 baris>"]}]}
   ```
   Butir mengikuti gaya laporan di bawah; kelompok kosong ditulis `[]`.
4. Bila dijalankan di sesi interaktif: render dan buka layarnya,
   `python3 "$R/scripts/render-laporan.py" <json> "${json%.json}.html" && open "${json%.json}.html"`,
   lalu di chat cukup kalimat inti + "laporan sudah terbuka". (Saat dijalankan sapaan pagi, skrip
   yang merender dan membuka.)
5. Sesi interaktif: tulis kabar suara seperti di bawah. (Sapaan pagi membacakan `kalimat` dari JSON.)

## Gaya laporan ke user (wajib)

**Singkat dan manusiawi.** Seperti rekan kerja mengabari lewat chat:

- Buka dengan sapaan sesuai waktu lalu kalimat inti, mis. "Selamat pagi. Ada 3 hal untuk mobile
  hari ini, 2 bisa langsung dikerjakan."
- Lalu daftar pendek, satu baris per hal, bahasa sehari-hari, sebut nama layar/fitur:
  "Daftar produk belum bisa ditarik untuk dimuat ulang (feedback #8)."
- Yang tidak perlu tindakan cukup satu baris penutup, mis. "Selain itu aman: MR dan pipeline bersih."
- Akhiri dengan satu perintah siap ketik.
- Tanpa judul besar, tanpa tabel, tanpa hash commit/path kecuali benar-benar diperlukan.
  Maksimal ±10 baris.

## Kabar suara (wajib, di akhir)

Tulis **satu kalimat inti** (maks ±20 kata, bahasa lisan, tanpa simbol/kode/path) ke file kabar;
hook akan menampilkannya sebagai notifikasi dan membacakannya:

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar.txt"
```
Contoh: "Selamat pagi. Ada dua hal untuk mobile hari ini, pipeline aman."
