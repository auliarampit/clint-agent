---
name: cek
description: Satu perintah untuk tahu kondisi kerja — tarik docs/designs/base branch dan cocokkan perubahannya dengan kode, plus MR open, pipeline gagal, branch tertinggal, worktree, dan sisa disk. Pakai di awal hari, saat user bertanya "ada update apa?" atau "apa yang perlu saya urus?".
argument-hint: [sejak <periode>]
---

1. Jalankan bersamaan agent `pelacak-perubahan` (teruskan periode bila disebut) dan `penjaga`.
2. Susun laporan sesuai **Gaya laporan** di bawah. Isinya mencakup: update docs/design dan
   dampaknya ke kode, feedback/bug QA yang masih open untuk project ini (walau file-nya tidak
   berubah belakangan ini), MR (pipeline gagal, komentar baru, menunggu review), dan
   bersih-bersih/disk bila ada yang perlu.
3. Langkah berikutnya berupa perintah `/clint:jalankan ...`. Jangan menyuruh user memanggil agent.

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
