# Keamanan sisi klien — ringkas, mengikuti OWASP Top 10

Dibaca bila task merender input pengguna, menyentuh auth/token, URL eksternal, upload, atau konfigurasi.

## XSS (A03)

- Default framework sudah meng-escape teks; **jangan** mem-bypass-nya (render HTML mentah) kecuali
  kontennya disanitasi dengan sanitizer yang dipakai project.
- URL dari pengguna/API divalidasi skemanya (`http`/`https`) sebelum dipakai di `href`/`src`;
  tolak `javascript:` dan `data:` yang tidak diharapkan.
- Tidak menyusun HTML/skrip dengan penggabungan string.

## Rahasia dan konfigurasi (A02, A05)

- Tidak ada API key privat, token server, atau kredensial di kode klien atau variabel lingkungan publik.
- Header keamanan (CSP, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors`) diatur di tempat
  yang ditunjuk adapter §13; perubahan CSP dibahas, bukan dilonggarkan diam-diam.
- Source map produksi tidak dipublikasikan bila project tidak menginginkannya.

## Autentikasi dan sesi (A07)

- Token sesi disimpan sesuai keputusan project (mis. cookie `HttpOnly` + `Secure` + `SameSite`); tidak
  di storage yang bisa dibaca skrip kecuali itu keputusan tertulis.
- Logout membersihkan semua state pengguna di klien (cache data, storage, state global).
- Pembaruan sesi: logout hanya bila server **menolak** (401/403). Jaringan putus, timeout, atau 5xx →
  sesi dipertahankan dan galat jaringan ditampilkan. Setiap `fetch`/klien HTTP punya timeout.
- Menyembunyikan tombol bukan otorisasi: pengecekan izin selalu juga dilakukan di server (A01).

## Data dan permintaan

- Mutasi dilindungi dari CSRF sesuai mekanisme project.
- Tidak mencatat data pribadi atau token ke console, analytics, atau pelacak error.
- Init SDK monitoring (Sentry dan sejenisnya) wajib punya `beforeBreadcrumb`/`beforeSend` yang membuang query
  string URL dan header sensitif, dengan test unit scrubber. Daftar redaksi: `Authorization`, `Cookie`, dan
  semua header di `securitySchemes` kontrak API.
- Upload: batasi jenis dan ukuran di klien sebagai kenyamanan, validasi tetap di server.
- Pengalihan setelah login hanya ke path internal yang diizinkan (cegah open redirect).

## Dependensi (A06)

Audit package manager berjalan sebagai gerbang MR (`quality-gates.md` §1); yang tingkat tinggi/kritis
diperbaiki atau dicatat alasannya beserta versi perbaikannya.
