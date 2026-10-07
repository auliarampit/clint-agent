# Aksesibilitas web — WCAG 2.2 level AA

Dibaca bila task menyentuh elemen interaktif, form, dialog, navigasi, gambar, atau warna.

## Semantik dulu, ARIA belakangan

- Aksi → `<button>`; pindah halaman/lokasi → `<a href>`. Jangan `div`/`span` dengan handler klik.
- Struktur halaman memakai landmark (`header`, `nav`, `main`, `footer`) dan satu `h1` per halaman;
  tingkat heading tidak melompat.
- ARIA hanya untuk yang tidak bisa diungkapkan HTML. ARIA yang salah lebih buruk daripada tanpa ARIA.
- Daftar → `ul/ol`; data tabular → `table` dengan `th` dan `scope`/caption.

## Keyboard dan fokus

- Semua yang bisa diklik bisa dicapai dan dijalankan dengan keyboard (Tab, Shift+Tab, Enter, Spasi,
  Esc untuk menutup).
- Fokus **selalu terlihat** (2.4.7) dan tidak tertutup elemen melekat (2.4.11).
- Urutan fokus mengikuti urutan visual. Tidak memakai `tabindex` positif.
- Dialog: fokus pindah ke dalam saat dibuka, terkurung di dalam, kembali ke pemicu saat ditutup.
- Setelah navigasi di aplikasi satu halaman, fokus dan pengumuman judul berpindah ke konten baru.

## Form

- Setiap input punya label yang terhubung (`<label for>` atau pembungkus); placeholder bukan label.
- Pesan error di dekat field, terhubung lewat `aria-describedby`, dan diumumkan; field ditandai
  `aria-invalid`. Ringkasan error di atas form untuk form panjang.
- Field wajib ditandai secara teks, bukan warna saja. Isian otomatis memakai `autocomplete` yang tepat.
- Target sentuh minimal 24×24 px (2.5.8).

## Warna, teks, gerak

- Kontras teks ≥ 4.5:1 (teks besar ≥ 3:1); komponen UI dan ikon informatif ≥ 3:1.
- Informasi tidak disampaikan lewat warna saja (tambahkan teks/ikon).
- Teks bisa diperbesar 200% tanpa terpotong; tata letak tetap dipakai di lebar 320 px.
- Hormati `prefers-reduced-motion`; tidak ada konten berkedip > 3 kali per detik.

## Gambar dan media

- Gambar informatif punya `alt` yang menjelaskan isinya; gambar dekoratif `alt=""`.
- Ikon tanpa teks (mis. tombol ikon) punya nama aksesibel.
- Video punya teks/caption bila berisi ucapan.

## Konten dinamis

- Perubahan penting (hasil simpan, error, jumlah hasil pencarian) diumumkan lewat live region
  (`role="status"`/`aria-live="polite"`; `alert` hanya untuk yang mendesak).
- State loading memberi tahu pembaca layar (`aria-busy` atau teks status).

## Cara memeriksa

1. Operasikan alur dengan keyboard saja.
2. Jalankan pemeriksa otomatis yang dipakai project (adapter §11) bila ada.
3. Periksa kontras token warna yang baru dipakai.
