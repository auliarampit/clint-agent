# Aksesibilitas mobile — WCAG 2.2 AA untuk React Native

Dibaca bila task menyentuh elemen interaktif, form, dialog/sheet, navigasi, warna, atau teks. Notasi `§N` =
bagian adapter (`.claude/mobile-stack.md`).

## Semantik dan label

- Setiap elemen yang bisa ditekan punya `accessibilityRole` yang benar (`button`, `link`, `checkbox`,
  `switch`, `tab`, `header`, ...) dan `accessibilityLabel` yang menyebut **tujuannya** ("Hapus alamat
  Rumah"), bukan bentuknya ("ikon tempat sampah").
- Ikon tanpa teks wajib punya label. Teks yang sudah terbaca tidak perlu label ganda.
- Status disampaikan lewat `accessibilityState` (`selected`, `checked`, `disabled`, `busy`, `expanded`),
  bukan hanya lewat warna atau ikon.
- `accessibilityHint` hanya bila akibat aksi tidak jelas dari labelnya.
- Elemen yang dibaca sebagai satu kesatuan (kartu berisi judul + harga + status) dikelompokkan
  (`accessible`) dengan label gabungan; elemen dekoratif disembunyikan dari pembaca layar.
- Label berasal dari file locale seperti teks lain (Step 0c.1).

## Ukuran sentuh dan tata letak

- Target sentuh minimal **44×44 pt (iOS) / 48×48 dp (Android)**. Ikon kecil diperluas dengan `hitSlop`
  atau padding, bukan dengan memperbesar ikon.
- Jarak antar target cukup supaya tidak tertekan bersamaan.

## Teks dan skala huruf

- Skala huruf sistem **tidak dimatikan** (`allowFontScaling` tetap aktif). Tata letak harus tetap terbaca
  sampai skala 200%: teks membungkus, tidak terpotong, kontainer tumbuh.
- `maxFontSizeMultiplier` hanya untuk elemen yang benar-benar rusak di skala besar (mis. tab bar), dengan
  alasan di MR.

## Warna dan kontras

- Kontras teks ≥ 4,5:1; teks besar (≥ 18 pt atau 14 pt tebal) dan komponen UI/ikon penting ≥ 3:1.
  Periksa juga mode gelap bila project mendukungnya.
- Informasi tidak disampaikan hanya lewat warna (error = warna + ikon/teks).

## Fokus, urutan, dan pengumuman

- Urutan baca pembaca layar mengikuti urutan visual.
- Dialog, sheet, dan modal mengunci fokus di dalamnya (`accessibilityViewIsModal` di iOS, perilaku setara di
  Android) dan mengembalikan fokus ke pemicunya saat ditutup.
- Hasil aksi async yang tidak memindahkan layar (tersimpan, gagal, item dihapus) diumumkan
  (`AccessibilityInfo.announceForAccessibility` atau live region).
- Saat layar baru terbuka, fokus pembaca layar jatuh di judulnya.

## Form

- Setiap input punya label yang terbaca (bukan placeholder saja).
- Pesan error terkait dengan inputnya, terbaca oleh pembaca layar, dan menyebut cara memperbaikinya.
- Tipe keyboard, `autoComplete`/`textContentType` sesuai jenis data (email, telepon, OTP, kata sandi).

## Gerak

- Hormati *reduce motion* (`AccessibilityInfo.isReduceMotionEnabled`): animasi dekoratif dimatikan atau
  diganti fade singkat.
- Tidak ada konten yang berkedip lebih dari 3 kali per detik.

## Memeriksa

Cek cepat sebelum selesai: jalankan alur yang diubah dengan VoiceOver (iOS) atau TalkBack (Android), dan
sekali dengan skala huruf terbesar. Pemeriksa otomatis di adapter §11 bila ada. Tidak bisa diperiksa di
perangkat → sebut "aksesibilitas belum diuji di perangkat".
