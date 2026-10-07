---
paths:
  - "**/test/**"
  - "**/tests/**"
  - "**/__tests__/**"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*_test.*"
---

# Test backend — aturan penulisan

> Portable. Runner, database test, dan lokasi test project ini ada di `.claude/backend-stack.md` §11.

## Lapisan test

| Lapisan | Menguji | Database |
|---|---|---|
| Unit | aturan bisnis/domain murni | tidak |
| Integrasi | endpoint + validasi + otorisasi + repository | **sungguhan** (database test/container sesuai adapter), bukan mock |
| Kontrak | bentuk respons dan error sesuai API contract | sesuai adapter |

Mock hanya untuk layanan luar (pembayaran, email, pihak ketiga) dan untuk keadaan yang sulit dibuat.

## Setiap endpoint minimal

1. Happy path dengan assertion pada status, bentuk respons, dan efek di database.
2. Validasi gagal (400/422) dengan kode error yang benar.
3. Tanpa autentikasi (401) bila endpoint terproteksi.
4. Otorisasi: pengguna lain/tanpa izin tidak bisa mengakses objek milik orang lain (403/404).

## Isolasi dan data

- Setiap test menyiapkan datanya sendiri lewat factory/fixture project; tidak bergantung urutan.
- Database dibersihkan/di-rollback antar test sesuai pola project; test bisa jalan paralel.
- Waktu, ID acak, dan layanan luar dikendalikan (clock/fake) supaya hasil deterministik.
- Tidak ada `sleep`; tunggu kondisi atau panggil job secara sinkron di test.

## Bug fix

Tulis test yang mereproduksi bug dan gagal dulu, baru perbaiki.

## Saat test gagal

Jangan melonggarkan assertion, menambah retry, atau men-skip test supaya hijau. Cari penyebabnya:
data test, perubahan perilaku yang disengaja (perbarui test + kontrak), atau bug.
