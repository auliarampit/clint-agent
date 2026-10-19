---
name: release
description: Build, distribusi, dan rilis — build APK/IPA untuk UAT, update over-the-air, naik versi, changelog dan catatan rilis, checklist store; untuk web/backend: kesiapan deploy, migrasi, variabel lingkungan, dan rencana mundur. Pakai saat user bilang "build APK untuk UAT", "rilis ke kanal preview", "siap deploy?". Tidak mengubah kode produk.
argument-hint: <apa yang dibuild/dirilis, ke mana>
---

# Release

## 1. Prasyarat

- Baca `.claude/clint.json`. Tidak ada → berhenti, tawarkan `/clint:setup`.
- **Bahasa**: laporan dan kabar suara memakai bahasa user (baris *Bahasa clint* di konteks sesi; default
  English). Catatan rilis dan changelog di repo memakai `docs.language` (tidak ada → ikuti bahasa file yang
  sudah ada).
- Tentukan surface dan target dari permintaan (profil build, kanal, lingkungan). Tidak jelas → tanya user
  sekali, jangan menebak.

## 2. Kerjakan

Panggil agent `release-engineer` dengan: permintaan user apa adanya, surface + path adapter-nya, target,
dan bahasa. Operasi yang berdampak ke pihak lain (kanal yang dipakai QA, store, produksi) hanya dijalankan
bila user menyebutnya secara eksplisit di permintaan ini. Selain itu `release-engineer` menyiapkan dan
melaporkan perintahnya, lalu kamu meminta konfirmasi user.

Perubahan file yang dihasilkan (versi, changelog, catatan rilis): stage eksplisit, commit mengikuti gaya
repo, lalu push/MR mengikuti `mr.mode` (aturan skill `develop` langkah 5.5).

## 3. Laporan

Maksimal ±8 baris: apa yang dirilis (versi, branch, commit), tautan/ID hasil, yang belum dilakukan beserta
alasannya, dan cara membatalkan. Baris terakhir wajib **Berikutnya** (aturannya sama dengan skill `develop`
bagian 6).

Tutup dengan kabar suara: satu kalimat inti (maks ±20 kata, tanpa simbol/kode/path):

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar.txt"
```
