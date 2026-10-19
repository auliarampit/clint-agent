# Keandalan: integrasi, job, event, cache, observability

Dibaca bila task memanggil layanan luar, membuat job/consumer, menerbitkan event, memakai cache, atau
menyentuh logging.

## Panggilan keluar

- Selalu ada timeout (koneksi dan total). Tanpa timeout = permintaan menggantung selamanya.
- Retry hanya untuk kegagalan sementara dan operasi idempoten, dengan backoff + jitter dan batas jumlah.
- Kegagalan layanan luar dipetakan ke error yang jelas bagi klien (mis. 502/503 sesuai kontrak), bukan 500 polos.

## Job latar dan consumer event

- Idempoten: aman bila dijalankan/dikirim dua kali (cek kunci unik atau status sebelum memproses).
- Kegagalan permanen masuk antrean gagal (dead letter) atau ditandai, tidak diulang tanpa batas.
- Job panjang menyimpan kemajuan supaya bisa dilanjutkan.

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
