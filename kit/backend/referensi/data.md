# Data, migrasi, dan query

Dibaca bila task menyentuh skema, migrasi, query, transaksi, atau indeks.

## Migrasi aman (deploy bertahap tanpa downtime)

Kode lama dan baru bisa berjalan bersamaan selama deploy. Karena itu perubahan skema dipecah:

| Mau | Langkah aman |
|---|---|
| Tambah kolom wajib | tambah sebagai nullable/berdefault → isi data → jadikan wajib di rilis berikutnya |
| Ganti nama kolom | tambah kolom baru → tulis ke keduanya → pindahkan data → baca dari baru → hapus lama nanti |
| Hapus kolom | hentikan semua pemakaian di kode dulu → hapus di rilis berikutnya |
| Ubah tipe | kolom baru + backfill, bukan `ALTER TYPE` langsung pada tabel besar |
| Indeks pada tabel besar | buat dengan cara yang tidak mengunci tulis bila database mendukung |

- Satu migrasi = satu perubahan logis; tidak mengedit migrasi yang sudah dijalankan di lingkungan bersama.
- Backfill data besar dilakukan bertahap (batch), bukan satu pernyataan raksasa.
- Seed/data contoh terpisah dari migrasi skema.

## Integritas

Batasan di database, bukan hanya di kode: `NOT NULL`, unik, foreign key, check. Penghapusan mengikuti
kebijakan project (soft delete atau hard delete) secara konsisten; data pribadi mengikuti aturan
penghapusan/anonimisasi yang tertulis.

## Transaksi

- Penulisan yang harus konsisten → satu transaksi, sesingkat mungkin.
- Tidak ada panggilan jaringan keluar di dalam transaksi.
- Pembaruan bersamaan pada data yang sama → kunci optimistis (versi) atau `SELECT … FOR UPDATE`
  sesuai pola project; hindari "baca lalu tulis" tanpa perlindungan.

## Query

- Tidak ada N+1: ambil relasi sekaligus (join/batch), bukan query per baris.
- Pilih kolom yang dibutuhkan saja. Daftar selalu dibatasi (paginasi).
- Kolom pada `WHERE`/`JOIN`/`ORDER BY` query yang sering dipanggil diberi indeks; periksa rencana query
  untuk query baru pada tabel besar.
- Hitungan total pada tabel besar dipertimbangkan biayanya.
