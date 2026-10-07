---
paths:
  - "**/e2e/**/*.{ts,js}"
  - "**/tests/**/*.spec.{ts,js}"
  - "**/*.e2e.{ts,js}"
  - "**/cypress/**/*.{ts,js}"
---

# Web E2E — aturan penulisan test

> Portable. Tool dan lokasi test project ini ada di `.claude/web-stack.md` §11. Bila adapter menulis
> `TIDAK ADA`, jangan memasang tool E2E sendiri; angkat ke user.

## Sebelum menulis: cari yang sudah ada

Ikuti pengelompokan, fixture login, dan helper yang sudah ada. Jangan menduplikasi langkah login di
setiap test bila project punya fixture/state tersimpan.

## Locator: peran dan penanda test, bukan struktur

Urutan pilihan: **peran + nama aksesibel** (tombol "Simpan", field berlabel "Email") → **penanda test**
(format adapter §11) → teks hanya untuk konten yang memang sedang diuji. Tidak memakai selektor CSS
berbasis kelas styling, urutan `nth-child`, atau XPath. Locator berbasis peran sekaligus menguji
aksesibilitas.

## Cakupan per fitur

Minimal dua: **happy path** sampai tuntas dengan assertion pada hasil akhir yang terlihat pengguna, dan
**satu error path utama** (validasi gagal, server menolak, atau jaringan gagal). Test yang hanya membuka
halaman tanpa assertion tidak dihitung.

## Menunggu: kondisi, bukan durasi

Tunggu elemen/teks/URL/respons jaringan yang diharapkan. Tidak ada jeda waktu tetap. Assertion yang
otomatis mencoba ulang lebih disukai daripada pengecekan sekali.

## Data dan isolasi

- Setiap test menyiapkan datanya sendiri (lewat API/seed bila tersedia) dan tidak bergantung pada urutan.
- Data unik per run (mis. akhiran waktu) supaya bisa jalan paralel.
- Respons jaringan di-mock hanya bila test memang menguji keadaan yang sulit dibuat (error 500,
  lambat); alur utama diuji terhadap backend sungguhan bila adapter menyediakannya.

## Ketertelusuran

Bila project punya dokumen test case (adapter §12), awali nama test dengan ID test case-nya.

## Artefak

Trace, video, dan screenshot disimpan di folder output tool yang di-ignore git; jangan di-commit.

## Saat test gagal

Urutan diagnosis: locator berubah? → perilaku memang berubah (perbarui test + dokumen test case)? →
bug produk (laporkan). Jangan melonggarkan assertion atau menambah retry supaya hijau.
