---
name: tinjau
description: Meninjau perubahan kode lalu langsung memperbaikinya sampai bersih — kesesuaian dokumen/aturan, clean code & arsitektur, keamanan, dan desain. Terpicu otomatis oleh hook setelah sesi selesai mengubah kode; bisa juga dipanggil manual ("cek dulu sebelum MR"). Untuk MR orang lain hanya meninjau tanpa mengubah.
argument-hint: [branch | !nomor-MR] [--saja]
---

# Tinjau dan perbaiki

## 1. Tentukan yang ditinjau

- Tanpa argumen: perubahan di working tree (belum di-commit) **ditambah** commit branch saat ini
  yang belum ada di `origin/<baseBranch>` (`.claude/clint.json`).
- Branch/MR disebut: `git fetch`, tinjau diff branch itu terhadap base.
- **Mode hanya-tinjau** bila argumen `--saja`, atau MR milik orang lain
  (`glab mr view` / `gh pr view` → author bukan user). Mode ini tidak mengubah apa pun.

## 2. Tinjauan paralel

Jalankan bersamaan, dalam satu pesan:

- `peninjau` dan `reviewer-senior`: selalu;
- `auditor-keamanan`: bila diff menyentuh auth, API/HTTP, storage, konfigurasi, dependensi,
  WebView/deep link;
- `penyelaras-desain`: bila diff menyentuh UI dan `docs.design` bukan `TIDAK ADA`;
- `auditor-aksesibilitas`: bila diff menyentuh komponen tampilan, form, dialog, navigasi, atau warna;
- `auditor-performa`: bila diff menambah dependensi, menyentuh daftar besar, gambar, pengambilan data,
  atau komponen yang sering dirender;
- `auditor-database`: bila diff menyentuh migrasi, skema, repository/akses data, atau query;
- `auditor-kontrak-api`: bila diff menyentuh endpoint, DTO/skema validasi, atau file kontrak.

Input dari kamu ke setiap peninjau (hemat token):
- simpan diff sekali ke file sementara (`git -C <path kerja> diff <base> > <tmp>/pr.diff`) dan
  beri **path**-nya, bukan isi diff;
- beri hanya potongan rencana untuk PR ini, plus hasil lint/typecheck/test dari laporan
  pengembang (supaya tidak dijalankan ulang);
- putaran ulang: kirim **hanya** daftar temuan sebelumnya + diff baru, minta peninjau
  memverifikasi temuan itu saja, bukan meninjau dari awal.

## 3. Perbaiki otomatis (kecuali mode hanya-tinjau)

- Kumpulkan temuan **wajib**: PERLU PERBAIKAN (termasuk dari `reviewer-senior`), ADA CELAH
  tingkat Sedang ke atas, dan selisih desain.
- Kirim semuanya dalam satu daftar ke agent `pengembang` untuk diperbaiki di tempat yang sama
  (repo utama; worktree hanya bila working tree user sedang dipakai untuk hal lain). Jangan commit.
- Tinjau ulang **hanya** dengan peninjau yang tadi memberi temuan. Maksimal 2 putaran.

## 4. Tandai sudah ditinjau

Setelah selesai (lulus maupun berhenti di batas putaran), jalankan perintah penanda yang
diberikan hook (`... stop-review.sh --tandai`) bila tinjauan ini dipicu hook. Ini mencegah
tinjauan berulang untuk perubahan yang sama.

## 5. Laporan singkat

Putusan per peninjau, apa saja yang sudah diperbaiki, temuan wajib yang masih tersisa (bila
batas putaran tercapai), dan saran yang tidak diterapkan.
