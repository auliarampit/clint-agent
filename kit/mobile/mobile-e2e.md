---
paths:
  - "**/maestro/**/*.{yaml,yml}"
  - "**/e2e/**/*.{ts,js}"
  - "**/.maestro/**/*.{yaml,yml}"
---

# Mobile E2E — aturan penulisan flow

> **Portable.** Tidak menyebut tool, path, atau nama project. Tool E2E dan lokasi flow
> project ini ada di `.claude/mobile-stack.md` §11. Baca itu dulu.
>
> Kalau adapter bilang `TIDAK ADA` untuk E2E, **jangan memasang tool E2E sendiri** — itu
> keputusan tooling; angkat ke user.

## Sebelum menulis flow: cari yang sudah ada

```bash
# tool + lokasi ada di adapter §11
ls {e2ePath}
```

Ikuti pengelompokan yang sudah ada (biasanya per epic/feature). Buat folder baru hanya kalau
epic-nya memang baru, dan pakai slug yang sama dengan yang dipakai dokumen project.

**Jangan menambah file ke folder yang ditandai legacy/deprecated.**

## Locator: id, bukan teks

**Selalu** pakai testID / accessibility id. **Tidak pernah** teks yang terlihat user.

Alasannya bukan gaya: teks berubah saat copy diperbarui atau locale berganti, dan flow akan
gagal karena alasan yang tidak ada hubungannya dengan bug. Id adalah kontrak; teks adalah
konten.

Kalau elemen yang perlu di-assert belum punya id → tambahkan id-nya di kode produk (mengikuti
format testID di skill Step 7), jangan menyiasatinya dengan XPath atau pencarian teks.

## Cakupan tiap flow

Satu feature minimal dua flow:

1. **Happy path** — jalur utama sampai tuntas, dengan assertion pada state akhir.
2. **Satu error path utama** — yang paling mungkin terjadi di produksi: input tidak valid,
   kredensial salah, atau kegagalan jaringan.

Jangan menulis flow yang hanya membuka screen lalu berhenti; flow tanpa assertion tidak
membuktikan apa pun dan hanya menambah waktu CI.

## Menunggu: kondisi, bukan durasi

Tunggu sampai elemen benar-benar terlihat/siap. **Jangan** memakai jeda dengan durasi tetap
untuk menunggu jaringan atau navigasi — itu flaky saat CI lambat dan boros saat CI cepat.

Jeda tetap hanya boleh untuk mensimulasikan perilaku user yang memang disengaja (mis. menahan
tombol), dan harus diberi komentar.

## Ketertelusuran

Kalau project punya dokumen test case (adapter §12), awali tiap flow/blok test dengan ID test
case-nya, supaya hasil run bisa dipetakan balik ke dokumen tanpa menebak.

## Independensi

Tiap flow berdiri sendiri: menyiapkan state yang dibutuhkannya dan tidak bergantung pada flow
lain yang berjalan lebih dulu. Flow yang hanya lulus jika dijalankan berurutan akan gagal saat
dijalankan paralel atau saat satu flow di-skip.

## Saat flow gagal

Urutan diagnosis — **jangan langsung mengubah flow supaya hijau**:

1. Apakah id-nya berubah? → cari commit yang me-rename; kalau rename itu tidak disengaja,
   perbaiki kode produk, bukan flow-nya.
2. Apakah perilakunya berubah dan memang disengaja? → update flow **dan** dokumen test case.
3. Apakah ini bug produk sungguhan? → laporkan lewat alur bug project; jangan melonggarkan
   assertion untuk menutupinya.

Melonggarkan assertion supaya CI hijau adalah cara paling cepat membuat seluruh suite tidak
berarti.
