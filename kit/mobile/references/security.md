# Keamanan mobile — OWASP Mobile Top 10 dan MASVS

Dibaca bila task menyentuh auth, token, penyimpanan lokal, deep link, WebView, izin, log, atau konfigurasi
build. Notasi `§N` = bagian adapter (`.claude/mobile-stack.md`).

## Rahasia dan konfigurasi

- **Tidak ada rahasia di bundle aplikasi.** Semua yang ada di JS bundle dan variabel env publik (mis.
  `EXPO_PUBLIC_*`) bisa dibaca siapa pun yang membongkar aplikasi. Kunci API privat, secret OAuth, dan
  kredensial layanan hanya ada di backend.
- Konfigurasi per lingkungan dari mekanisme env project (adapter §2), bukan dihardcode.

## Penyimpanan lokal

- Token akses/refresh, PIN, dan data sensitif disimpan di penyimpanan aman platform (Keychain/Keystore,
  lewat library di adapter §4/§5). **Tidak pernah** di AsyncStorage, MMKV tanpa enkripsi, atau file biasa.
- Simpan seminimal mungkin; data pribadi yang tidak perlu offline tidak disimpan.
- Logout menghapus token, cache data pengguna, dan state yang dipersistenkan.

## Jaringan

- Hanya HTTPS. Pengecualian cleartext (ATS iOS, `usesCleartextTraffic` Android) hanya untuk dev lokal dan
  tidak ikut ke build rilis.
- Certificate pinning bila diwajibkan project/klien (adapter §13); jangan dimatikan untuk "sementara".
- Token tidak dikirim di query string. Error jaringan tidak menampilkan detail server ke pengguna.

## Autentikasi dan sesi

- Refresh token ditangani wrapper HTTP (adapter §5); kegagalan refresh → logout bersih, bukan loop.
- Biometrik lokal hanya membuka kunci rahasia yang tersimpan aman; ia **bukan** pengganti autentikasi server.
- Otorisasi selalu ditegakkan di server; menyembunyikan tombol di klien bukan kontrol akses.

## Deep link dan navigasi

- Parameter deep link divalidasi (tipe, format, kepemilikan) sebelum dipakai.
- Deep link tidak menjalankan aksi berdampak (bayar, hapus, ubah data) tanpa konfirmasi pengguna yang login.
- Universal/App Links diutamakan daripada skema kustom untuk alur sensitif.

## WebView

- Hanya memuat domain yang diizinkan (`originWhitelist`/pengecekan URL); tautan luar dibuka di browser.
- Tidak menyuntikkan data sensitif ke WebView; jembatan `postMessage` memvalidasi asal dan bentuk pesan.
- Akses file dan konten campuran dimatikan kecuali benar-benar dibutuhkan.

## Log, clipboard, dan layar

- Tidak ada token, kata sandi, OTP, atau data pribadi di log, crash report, atau analytics.
- Data sensitif tidak disalin ke clipboard tanpa aksi eksplisit pengguna.
- Layar sensitif (OTP, kartu, saldo) dilindungi dari tangkapan layar/pratinjau multitasking bila
  diwajibkan project.

## Izin

- Minta izin seminimal mungkin dan tepat saat dibutuhkan, dengan penjelasan; tangani penolakan dengan baik.
- Deklarasi izin di konfigurasi build hanya untuk fitur yang memang ada.

## Dependensi

- Dependensi baru = wajib tanya (sudah aturan skill). Periksa reputasi, pemeliharaan, dan audit
  (`npm audit`/setara) sebelum dipakai.

Audit mendalam dilakukan `security-auditor`; dokumen ini adalah aturan saat menulis kode.
