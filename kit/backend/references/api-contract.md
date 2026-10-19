# Kontrak API

Dibaca bila task membuat/mengubah endpoint, bentuk respons, error, atau paginasi.

## Sumber kebenaran

Kontrak (OpenAPI/dokumen kontrak, adapter §12) ditulis atau diperbarui **sebelum/bersama** kode, bukan
sesudahnya. Implementasi yang berbeda dari kontrak adalah bug, walaupun "lebih bagus".

## Konvensi REST

- Resource kata benda jamak (`/orders/{id}`); aksi yang bukan CRUD → sub-resource kata kerja yang
  jelas (`POST /orders/{id}/cancel`).
- `GET` tanpa efek samping · `POST` membuat · `PUT` mengganti utuh · `PATCH` mengubah sebagian ·
  `DELETE` menghapus (idempoten).
- `201` + lokasi/objek untuk pembuatan · `204` tanpa body · `202` untuk proses asinkron.
- Casing field konsisten di seluruh API (adapter §7). Tanggal ISO 8601 UTC. Uang sebagai integer
  satuan terkecil atau desimal string, sesuai kontrak.

## Envelope error

Satu bentuk untuk semua error (adapter §7), berisi minimal: kode error stabil yang bisa dibaca mesin,
pesan untuk manusia, dan rincian per field untuk error validasi. Kode error adalah bagian kontrak:
tidak diganti nama, satu kode satu arti. Error 500 tidak membocorkan stack trace atau query.

## Paginasi, filter, urutan

- Batas ukuran halaman (default dan maksimum). Kembalikan metadata yang dibutuhkan klien.
- Kursor untuk data yang terus bertambah/berubah; offset hanya untuk data kecil dan stabil.
- Filter dan urutan hanya pada field yang diizinkan (daftar putih) dan berindeks.

## Idempotensi

Operasi `POST` yang bisa diulang klien karena jaringan (pembayaran, pemesanan, pengiriman pesan) menerima
kunci idempotensi; permintaan ulang dengan kunci sama mengembalikan hasil pertama, bukan membuat dua kali.

## Perubahan kontrak

| Aman (tidak merusak) | Merusak (butuh versi/keputusan) |
|---|---|
| tambah endpoint baru | hapus/ganti nama endpoint atau field |
| tambah field opsional di respons | ubah tipe atau arti field |
| tambah nilai enum yang klien abaikan dengan aman | field opsional jadi wajib di request |
| tambah parameter opsional | ubah status code atau kode error |

Perubahan merusak tidak dilakukan diam-diam: tandai di deskripsi MR, sebutkan klien terdampak (web,
mobile, layanan lain), dan ikuti strategi versi project.
