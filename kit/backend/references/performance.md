# Performa backend — target ketat, diukur, bukan dirasa

Dibaca **selalu** untuk endpoint baru, dan untuk task apa pun yang menyentuh query, endpoint di jalur yang
sering dipanggil, job, cache, ekspor/impor data, atau dependensi baru. Notasi `§N` = bagian adapter
(`.claude/backend-stack.md`). Aturan query dan indeks yang lebih rinci ada di `data.md`; timeout, retry,
dan cache di `reliability.md`. Dokumen ini menetapkan **target dan disiplin performanya**.

Standar Badr: **performa terbaik, bukan "cukup"**. Pelanggaran aturan di dokumen ini adalah temuan
**Wajib** saat review, bukan saran.

## 1. Target

Diukur di lingkungan yang mendekati produksi (build produksi, data bervolume realistis), bukan di database
kosong. Adapter §11 boleh menetapkan angka lebih ketat, tidak boleh lebih longgar tanpa persetujuan user.

| Metrik | Target |
|---|---|
| Latensi endpoint baca | p95 ≤ 200 ms, p99 ≤ 500 ms |
| Latensi endpoint tulis | p95 ≤ 300 ms, p99 ≤ 800 ms |
| Endpoint yang memanggil layanan luar | waktu milik sendiri (di luar layanan luar) tetap dalam target di atas; layanan luar dibatasi timeout |
| Query tunggal | ≤ 50 ms pada volume data realistis |
| Jumlah query per permintaan | konstan terhadap jumlah data (tanpa N+1); idealnya ≤ 10 |
| Ukuran respons | ≤ 1 MB; daftar selalu berpaginasi, ukuran halaman maksimum ditetapkan (mis. 100) |
| Blok event loop / thread request (runtime satu thread) | tidak ada yang > 50 ms |
| Memori per permintaan | tidak memuat seluruh tabel/berkas besar ke memori |
| Error rate di bawah beban target | < 0,1% |

## 2. Database

- **Tanpa N+1**: relasi diambil sekaligus (join/batch/eager load). Test integrasi untuk endpoint daftar
  sebaiknya memastikan jumlah query tidak tumbuh mengikuti jumlah baris.
- Query baru pada tabel yang bisa besar (> 10 ribu baris) diperiksa rencana eksekusinya (`EXPLAIN`/setara):
  tidak ada full scan pada jalur yang sering dipanggil; kolom `WHERE`/`JOIN`/`ORDER BY` berindeks.
- Ambil kolom yang dibutuhkan saja, bukan `SELECT *`. Hitung di database (agregasi, filter), bukan di
  aplikasi setelah mengambil semua baris.
- Paginasi berbasis cursor/keyset untuk data besar atau yang terus bertambah; offset hanya untuk data kecil.
- Tulis massal memakai batch/bulk, bukan insert per baris di loop.
- Transaksi sependek mungkin; tidak ada panggilan jaringan keluar di dalam transaksi.
- Connection pool dikonfigurasi (adapter §5); tidak membuka koneksi baru per permintaan.

## 3. Jalur permintaan

- Pekerjaan lambat atau tidak dibutuhkan untuk respons (kirim email/notifikasi, generate PDF, sinkron ke
  pihak ketiga, pemrosesan gambar) dipindah ke job/antrean (adapter §8); endpoint mengembalikan respons
  segera.
- Panggilan independen ke layanan lain/database dijalankan **paralel**.
- Kerja CPU berat (kriptografi massal, parsing besar, kompresi) tidak memblokir thread yang melayani
  permintaan; pindahkan ke worker/job.
- Ekspor/impor besar memakai streaming, bukan memuat semua data ke memori.
- Respons dikompresi; tidak mengirim field yang tidak dibutuhkan klien (DTO, bukan entitas mentah).

## 4. Cache

- Data yang sering dibaca dan jarang berubah di-cache dengan invalidasi yang jelas (`reliability.md`).
- Endpoint publik/statis memakai header cache HTTP (`Cache-Control`, `ETag`) bila datanya memungkinkan.
- Cache tidak menutupi query yang lambat: perbaiki query dan indeksnya dulu.

## 5. Dependensi dan startup

- Dependensi baru = **wajib tanya**, dengan alasan, ukuran, dan dampaknya ke waktu startup dan memori.
- Tidak ada pekerjaan berat saat aplikasi start yang memperlambat deploy/scale-out; inisialisasi
  koneksi dilakukan sekali dan dipakai ulang.

## 6. Cara mengukur dan melapor

1. Query baru/berubah pada tabel besar: lampirkan ringkasan rencana eksekusi (indeks dipakai, perkiraan
   baris) di laporan/MR.
2. Endpoint baru atau di jalur panas: ukur latensi (log timing, APM, atau load test di adapter §11, mis.
   k6/Artillery) dan jumlah query per permintaan; angka **sebelum dan sesudah** bila mengubah yang sudah ada.
3. Tidak bisa diukur → tulis "performa belum terukur" beserta alasannya. **Jangan pernah mengklaim target
   tercapai tanpa angka.**
4. Regresi terhadap target di bagian 1 menahan MR sampai diperbaiki atau user menyetujui pengecualiannya.
5. Bagian lama yang **sudah** di bawah target sebelum PR ini: PR tidak boleh memperburuknya, dan selisihnya
   dilaporkan sebagai utang performa (angka + penyebab dugaan), bukan penahan MR. Bila PR memang menyentuh
   penyebabnya, perbaiki sekalian selama masih dalam lingkup; bila tidak, sarankan tugas terpisah.
