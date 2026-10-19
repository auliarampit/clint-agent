# Tanpa AI slop: tulisan dan kode yang terasa dibuat engineer, bukan mesin

> **Portable.** Berlaku di semua project, untuk semua yang dibaca manusia: kode, komentar, pesan commit,
> deskripsi MR, laporan, dokumen, changelog, teks UI. Aturan project (CLAUDE.md, gaya dokumen yang sudah
> ada) tetap menang bila lebih ketat.

Ukurannya satu: **apakah engineer senior di tim ini akan menulisnya persis begini?** Kalau ada kata, baris,
atau bagian yang hanya ada karena "AI biasanya menulis begitu", hapus.

## 1. Tulisan

**Langsung ke isi.**
- Tanpa pembuka dan penutup basa-basi: "Tentu!", "Baik, saya akan...", "Berikut adalah...", "Semoga
  membantu", "Kesimpulannya", "Great question", "I hope this helps".
- Tanpa mengulang permintaan atau menjelaskan proses ("Pertama saya membaca file, lalu..."). Tulis hasil
  dan yang perlu diputuskan.
- Bagian yang tidak punya isi dihapus, bukan diisi "Tidak ada" atau "Mengikuti dokumen X".

**Kata yang konkret, bukan iklan.**
- Hindari kata pujian kosong: *robust, seamless, comprehensive, powerful, cutting-edge, leverage, delve,
  elevate, streamline, game-changer*, "solusi menyeluruh", "secara signifikan", "sangat optimal".
- Klaim memakai angka atau bukti: "LCP 2,4 → 1,6 dtk", bukan "performa meningkat drastis". Tanpa angka,
  tulis apa yang berubah saja.
- Hindari pola khas mesin: "tidak hanya X, tetapi juga Y"; daftar tiga kata sifat ("cepat, aman, dan
  andal"); pertanyaan retoris; kalimat penutup yang merangkum ulang.

**Tanda baca dan format.**
- **Tanpa em dash (—)** di tulisan baru. Pakai titik dua, koma, titik, atau tanda kurung. En dash untuk
  rentang (`10–20`) boleh.
- Tebal hanya untuk hal yang benar-benar harus terlihat, bukan di setiap kalimat. Judul hanya bila tulisan
  cukup panjang untuk dinavigasi.
- Tidak semua hal harus jadi butir. Satu-dua kalimat biasa sering lebih jelas.
- Emoji hanya bila konvensi project memakainya (mis. status di sprint tracker), bukan dekorasi.

**Jujur.**
- Yang belum diuji ditulis belum diuji. Tidak ada "sudah diuji menyeluruh" tanpa hasil.
- Tidak menyebut proses AI di artefak tim: nama agent, jumlah putaran tinjauan, "dibuat oleh AI" tidak
  masuk deskripsi MR, commit, atau dokumen, kecuali project memintanya.

**Per jenis tulisan.**
- *Commit*: ikuti gaya `git log` repo; apa yang berubah dan kenapa, spesifik ("fix(auth): refresh token
  tidak dikirim ulang setelah 401"), bukan "update files" atau "improve code".
- *Deskripsi MR*: apa yang berubah bagi pengguna, cara memverifikasi, risiko, yang belum dikerjakan.
- *Laporan ke user*: seperti rekan kerja mengabari lewat chat; kalimat pertama adalah hasilnya.
- *Teks UI*: spesifik dan bisa ditindaklanjuti ("Nomor HP harus 10–13 digit"), mengikuti nada produk;
  bukan "Oops! Terjadi kesalahan 😅" atau teks placeholder.

## 2. Kode

### Komentar: default tidak ada

Komentar yang banyak membuat kode kotor dan cepat basi. Kode yang butuh penjelasan biasanya butuh nama
yang lebih baik atau fungsi yang lebih kecil; perbaiki itu, bukan menambah komentar.

- **Jangan menambah komentar** di kode yang ditulis atau diubah, termasuk JSDoc/docstring untuk fungsi
  internal, komentar per langkah (`// ambil data`, `// validasi input`), banner/pemisah bagian,
  `// Added by ...`, `// TODO: implement`, dan kode yang dikomentari.
- **Pengecualian, satu baris pendek saja**, bila tanpa itu orang berikutnya hampir pasti salah mengubah kode:
  jalan pintas untuk bug library/platform (sertakan tautan isu), aturan bisnis yang tidak terbaca dari kode
  (sertakan ID requirement, mis. `// FR-06`), atau angka ajaib dari pihak luar.
- **Tetap boleh** karena bukan komentar penjelas: direktif tool (`eslint-disable-next-line`,
  `@ts-expect-error`, `prettier-ignore`), dan dokumentasi API publik bila konvensi package/project
  memintanya (mis. library yang dipublikasikan).
- Penjelasan panjang (alasan keputusan, kontrak yang ditiru, konflik yang belum selesai) ditulis di ADR,
  rencana, atau deskripsi MR, bukan di kode.
- Komentar milik orang lain di luar lingkup PR tidak dihapus atau diubah.

### Lainnya

- **Tanpa kode defensif yang tidak diminta**: try/catch yang hanya menelan atau mencetak ulang error, cek
  null pada nilai yang tipenya sudah non-null, fallback yang menyembunyikan kegagalan, `console.log` sisa.
- **Tanpa abstraksi spekulatif**: tidak ada interface, factory, opsi konfigurasi, atau parameter untuk
  kebutuhan yang belum ada (prinsip kerja 1).
- **Nama mengikuti codebase**: pola penamaan yang sudah ada; tanpa nama generik (`data2`, `helper`,
  `handleClick2`, `utils/misc`) atau akhiran berlebihan (`...Manager`, `...Handler` tanpa alasan).
- **Tanpa implementasi palsu**: nilai hardcode, mock, atau cabang khusus supaya test lulus; data contoh
  tertinggal di kode produksi.
- **Tanpa kode mati**: parameter, impor, fungsi, atau kode yang dikomentari tidak tertinggal.
- **Tidak menyentuh yang tidak diminta**: tidak merapikan, mengganti nama, atau memformat ulang file di luar
  lingkup PR.
- **Test menguji perilaku**, bukan memastikan mock terpanggil atau menumpuk snapshot yang tidak dibaca orang.
- **Pesan error spesifik**: apa yang gagal dan konteksnya, bukan "Something went wrong".
