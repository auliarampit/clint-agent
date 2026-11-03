# Keandalan: integrasi, job, event, cache, observability

Dibaca bila task memanggil layanan luar, membuat job/consumer, menerbitkan event, memakai cache, atau
menyentuh logging.

## Panggilan keluar

- Selalu ada timeout (koneksi dan total) di setiap klien HTTP/RPC. Tanpa timeout = permintaan menggantung selamanya.
- Hasil dibedakan: ditolak (4xx dari layanan luar) vs tak terjangkau (jaringan, timeout, 5xx). Hanya penolakan
  yang boleh mengubah state permanen (mis. mencabut sesi, menandai gagal final).
- Retry hanya untuk kegagalan sementara dan operasi idempoten, dengan backoff + jitter dan batas jumlah.
- Kegagalan layanan luar dipetakan ke error yang jelas bagi klien (mis. 502/503 sesuai kontrak), bukan 500 polos.

## Job latar dan consumer event

- Idempoten: aman bila dijalankan/dikirim dua kali (cek kunci unik atau status sebelum memproses).
- Kegagalan permanen masuk antrean gagal (dead letter) atau ditandai, tidak diulang tanpa batas.
- Job panjang menyimpan kemajuan supaya bisa dilanjutkan.
- Job terjadwal (cron, scheduler) didaftarkan satu kali di satu tempat; banyak instans → kunci/leader election
  supaya tidak berjalan ganda.
- Satu penulis per agregat: data yang sama tidak diubah dari dua modul tanpa melewati pemiliknya.

## Menerbitkan event dengan konsisten

Bila perubahan data dan event harus konsisten, simpan event ke tabel outbox dalam transaksi yang sama,
lalu kirim oleh relay terpisah. Jangan mengirim event langsung di tengah transaksi yang masih bisa gagal.

## Cache

- Tentukan sumber kebenaran dan cara invalidasi sebelum menambah cache.
- Kunci cache memuat semua parameter yang memengaruhi hasil, termasuk identitas/izin bila data per pengguna.
- Waktu kedaluwarsa wajar; cache bukan tempat satu-satunya data.

## Observability

- Log terstruktur (JSON/kunci-nilai) dengan ID korelasi yang diteruskan ke layanan lain.
- Error yang perlu tindakan → level error + konteks yang cukup untuk reproduksi, tanpa data sensitif.
- Endpoint kesehatan (liveness/readiness) tidak membocorkan detail internal.
- Metrik/trace mengikuti alat project (adapter §9) bila ada.
