# Pola UI web yang berulang

Dibaca bila task membuat form, tabel, paginasi, filter, dialog, toast, upload, atau wizard. Pakai
komponen project (adapter §7) dan ikuti pola feature yang sudah ada; ini standar perilakunya.

## Form

- Skema validasi tunggal (library adapter §4) dipakai untuk validasi klien dan tipe data form.
- Validasi saat blur dan saat kirim; jangan menampilkan error sebelum pengguna menyentuh field.
- Tombol kirim nonaktif + indikator selama proses; cegah kirim ganda.
- Error dari server dipetakan ke field yang tepat; sisanya ke pesan umum form.
- Perubahan belum tersimpan → konfirmasi sebelum meninggalkan halaman (bila form panjang).

## Tabel dan daftar

- Empat keadaan: loading (skeleton baris), error (pesan + coba lagi), kosong (penjelasan + aksi utama),
  berisi. Kosong karena filter dibedakan dari kosong karena belum ada data.
- Paginasi/urut/filter/pencarian tersimpan di URL. Ganti filter → kembali ke halaman 1.
- Aksi per baris yang merusak (hapus) memakai konfirmasi; aksi massal menyebut jumlah yang terpilih.
- Kolom angka rata kanan dengan digit tabular; tanggal dan uang diformat sesuai locale.

## Pencarian

Debounce input, batalkan permintaan lama yang belum selesai, tampilkan jumlah hasil, dan bedakan
"belum mencari" dari "tidak ada hasil".

## Dialog dan konfirmasi

- Judul menyebut aksinya; tombol utama menyebut hasilnya ("Hapus produk"), bukan "OK".
- Aksi berbahaya: tombol berwarna peringatan, fokus awal pada tombol batal.
- Esc dan klik latar menutup dialog kecuali ada perubahan belum tersimpan.

## Notifikasi (toast)

Untuk hasil aksi yang tidak mengubah halaman. Teks menyebut hasil ("Produk disimpan"). Error yang
perlu tindakan tidak hilang sendiri. Tidak dipakai untuk error validasi field.

## Upload

Tampilkan nama, ukuran, progres, dan pembatalan; validasi jenis/ukuran sebelum mengunggah; pesan gagal
menyebut penyebabnya.

## Wizard multi-langkah

Langkah saat ini dan totalnya terlihat; data tiap langkah disimpan saat pindah langkah; kembali tidak
menghapus isian; validasi per langkah sebelum lanjut.

## Halaman terproteksi

Pengecekan sesi sebelum konten tampil (tanpa kilatan konten terproteksi); sesi habis → arahkan ke login
lalu kembali ke halaman semula; tidak punya izin → halaman 403 yang menjelaskan, bukan halaman kosong.

## Galat, state, dan data bisnis

Aturan ini muncul dari audit Sprint 1–4 project pertama clint; masing-masing pernah menjadi temuan Major.

- **Galat dibedakan.** Hasil permintaan minimal `rejected` (4xx) vs `unreachable` (jaringan, timeout, 5xx);
  pesan "luring/koneksi" hanya untuk `unreachable`. Status gagal yang dikembalikan hook wajib dipakai halaman.
- **Empat keadaan per halaman data**: loading, galat, kosong, berisi. Galat tidak tampil seperti kosong.
- **Satu pemilik state.** Data server tetap di lapisan cache query, tidak disalin ke store global kecuali sesi
  minimal dengan satu fungsi pengganti. Efek global (polling, websocket, sinkronisasi) dipasang satu kali di
  root layout; adaptor fokus/online library query di root.
- **Jawaban basi diabaikan.** Pencarian/lookup membatalkan atau membuang respons untuk input lama
  (`AbortController` atau kunci query).
- **Logika memakai kode/ID**, tidak membandingkan teks terjemahan atau nama dari server.
- **Tanggal bisnis** dihitung dengan zona waktu eksplisit dari adapter, bukan zona browser.
- **Istilah produk** mengikuti glosarium project (`quality-gates.md` §1).
