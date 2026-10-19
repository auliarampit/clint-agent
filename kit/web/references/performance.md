# Performa web — target ketat, diukur, bukan dirasa

Dibaca **selalu** untuk task yang membuat halaman/route baru, dan untuk task apa pun yang menyentuh daftar
besar, gambar, font, pengambilan data, dependensi baru, skrip pihak ketiga, atau render ulang. Notasi `§N` =
bagian adapter (`.claude/web-stack.md`). Nama framework dan library diambil dari adapter.

Standar Badr: **performa terbaik, bukan "cukup"**. Target di bawah lebih ketat dari ambang "baik" Core Web
Vitals. Pelanggaran aturan di dokumen ini adalah temuan **Wajib** saat review, bukan saran.

## 1. Target

Diukur pada **build produksi** (bukan dev server) dengan profil **mobile**: CPU diperlambat 4× dan jaringan 4G
lambat (setelan bawaan audit lab), plus data lapangan bila ada. Persentil ke-75. Adapter §11 boleh
menetapkan angka lebih ketat, tidak boleh lebih longgar tanpa persetujuan user.

| Metrik | Target |
|---|---|
| LCP (Largest Contentful Paint) | ≤ 1,8 dtk |
| INP (Interaction to Next Paint) | ≤ 100 ms |
| CLS (Cumulative Layout Shift) | ≤ 0,05 |
| FCP (First Contentful Paint) | ≤ 1,2 dtk |
| TTFB (Time to First Byte) | ≤ 400 ms (≤ 100 ms untuk halaman statis/ter-cache) |
| Total Blocking Time (lab) | ≤ 150 ms |
| Skor Performance audit lab (mis. Lighthouse) | ≥ 95 desktop, ≥ 90 mobile |
| JS awal per route (gzip) | ≤ 170 KB; kenaikan > 20 KB per PR dijelaskan di MR |
| CSS awal (gzip) | ≤ 50 KB |
| Long task di jalur interaksi | tidak ada yang > 50 ms |

## 2. LCP dan pemuatan awal

- Elemen LCP (gambar hero, judul) dimuat paling awal: prioritas tinggi (`fetchpriority="high"`/preload),
  **tidak** lazy, ukuran sesuai tampilan, format modern (AVIF/WebP).
- Render di server/statis bila framework mendukungnya (adapter §3): konten utama ada di HTML pertama, bukan
  menunggu JS di browser.
- Data untuk konten utama diambil **paralel** dan sedini mungkin (di server/loader route bila ada); tidak
  ada waterfall (A selesai baru B, komponen anak baru mulai fetch setelah induk selesai).
- Koneksi ke origin penting dibuka lebih awal (`preconnect`). Tidak ada redirect berantai.
- Font: maksimal 2 keluarga, subset, `font-display: swap`, font kritis di-preload, self-host bila bisa.

## 3. INP dan render

- Handler interaksi selesai cepat: umpan balik visual dulu, pekerjaan berat dipecah (yield ke main thread),
  ditunda, atau dipindah ke worker.
- State sedekat mungkin dengan pemakainya; perubahan kecil tidak merender ulang seluruh halaman.
- Komponen yang dirender berulang (baris tabel, kartu daftar) dibungkus memo dengan prop stabil; kalkulasi
  mahal di badan render dihitung sekali dengan dependensi tepat.
- Komponen interaktif sekecil mungkin: bila framework memisahkan komponen server dan klien, tanda klien
  hanya di daun yang benar-benar interaktif.
- Input pencarian/filter: debounce (±300 ms) dan batalkan permintaan sebelumnya.
- Efek dibersihkan (listener, interval, subscription, permintaan berjalan).

## 4. CLS

- Gambar, video, iframe, embed, dan iklan punya dimensi/`aspect-ratio` yang dipesan.
- Skeleton berukuran sama dengan konten akhirnya.
- Konten tidak disisipkan di atas konten yang sudah terlihat kecuali karena aksi pengguna; banner/cookie
  bar memakai ruang yang dipesan atau overlay.
- Animasi memakai `transform`/`opacity`, bukan properti tata letak.

## 5. JavaScript, CSS, dan bundle

- Setiap dependensi baru = **wajib tanya**, dengan ukuran (gzip), alternatif yang sudah ada, dan dampaknya
  ke JS awal.
- Pecah kode per route; komponen berat yang jarang dipakai (editor, grafik, peta, PDF) dimuat saat
  dibutuhkan.
- Impor spesifik, bukan seluruh library; tidak mengirim kode khusus server ke browser; tidak ada polyfill
  yang tidak dibutuhkan target browser.
- Skrip pihak ketiga (analytics, chat, tag manager) dimuat setelah halaman interaktif (`defer`/setelah idle)
  dan tidak memblokir render.
- CSS kritis kecil; tidak ada CSS tak terpakai dalam jumlah besar.

## 6. Gambar dan media

- Gambar lewat komponen gambar di adapter §7 (bila ada) dengan `srcset`/`sizes` responsif dan format modern.
- Gambar di bawah lipatan memakai lazy loading; thumbnail di daftar, bukan ukuran asli.
- Video tidak autoplay dengan suara, punya poster, dan tidak dimuat penuh sebelum diputar.

## 7. Data, cache, dan daftar

- Server state lewat lapisan cache di adapter §4: data yang sama tidak diambil ulang di setiap komponen;
  waktu basi sesuai sifat data.
- Aset statis memakai nama ber-hash dan cache jangka panjang; HTML/data memakai header cache yang sesuai.
- Respons dikompresi (brotli/gzip).
- Daftar ratusan baris ke atas: paginasi di server atau virtualisasi; tidak pernah merender ribuan baris.
- Prefetch route/data berikutnya saat pengguna menunjukkan niat (hover/fokus pada tautan) bila framework
  mendukung.

## 8. Cara mengukur dan melapor

1. Ukur halaman yang diubah dengan alat di adapter §11 (audit lab, analisis bundle, profiler render) pada
   build produksi dengan profil mobile.
2. Halaman/route baru, perubahan pemuatan, dependensi baru, atau daftar: angka **sebelum dan sesudah**
   (LCP, INP/TBT, CLS, ukuran JS) di laporan/MR.
3. Tidak bisa diukur → tulis "performa belum terukur" beserta alasannya. **Jangan pernah mengklaim target
   tercapai tanpa angka.**
4. Regresi terhadap target di bagian 1 menahan MR sampai diperbaiki atau user menyetujui pengecualiannya.
5. Bagian lama yang **sudah** di bawah target sebelum PR ini: PR tidak boleh memperburuknya, dan selisihnya
   dilaporkan sebagai utang performa (angka + penyebab dugaan), bukan penahan MR. Bila PR memang menyentuh
   penyebabnya, perbaiki sekalian selama masih dalam lingkup; bila tidak, sarankan tugas terpisah.
