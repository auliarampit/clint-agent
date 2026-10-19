# Keamanan API — OWASP API Security Top 10 (2023), praktis

Dibaca bila task menyentuh auth, izin, input pengguna, upload, rate limit, atau data pribadi.

| Risiko | Yang wajib dilakukan |
|---|---|
| API1 BOLA | Setiap akses objek lewat ID memeriksa kepemilikan/jangkauan pemanggil. Tidak ada → 404 (jangan bocorkan keberadaan) atau 403 sesuai kontrak |
| API2 Autentikasi rusak | Pakai mekanisme auth project; token diverifikasi tanda tangan, masa berlaku, audiens. Login/OTP/reset dibatasi laju dan tidak membocorkan "email tidak terdaftar" |
| API3 Otorisasi properti | Respons lewat DTO (tanpa field internal); input lewat skema (field yang tidak boleh diubah pengguna ditolak/diabaikan) |
| API4 Konsumsi sumber daya | Batas ukuran halaman, ukuran body, ukuran upload, timeout, dan pembatas laju untuk endpoint mahal |
| API5 Otorisasi fungsi | Aksi admin/berbahaya dicek izinnya di server per endpoint, default tolak |
| API6 Alur bisnis sensitif | Alur yang bisa disalahgunakan massal (voucher, pendaftaran, pemesanan stok terbatas) punya pembatasan |
| API7 SSRF | URL yang diambil server dari input pengguna divalidasi (daftar host diizinkan, tolak alamat internal) |
| API8 Miskonfigurasi | CORS hanya origin yang diizinkan; header keamanan; mode debug mati di produksi; error tanpa stack trace |
| API9 Inventaris | Endpoint lama/dev/dokumentasi tidak terbuka di produksi tanpa sengaja; kontrak mencerminkan endpoint nyata |
| API10 Konsumsi API pihak ketiga | Respons layanan luar divalidasi seperti input pengguna; timeout dan penanganan gagal |

## Data pribadi dan rahasia

- Sandi di-hash dengan algoritma lambat yang dipakai project; tidak pernah dienkripsi bolak-balik.
- Rahasia dari konfigurasi terkelola; tidak di repo, log, respons, atau pesan error.
- Log dan event tidak memuat token, sandi, OTP, nomor identitas lengkap.

## Upload

Validasi jenis dari isi file (bukan nama), batas ukuran, nama file dibuat server, simpan di luar
direktori yang bisa dieksekusi, pindai bila project mewajibkan.
