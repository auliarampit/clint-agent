# Performa web — Core Web Vitals dan bundle

Dibaca bila task menyentuh daftar besar, gambar, pengambilan data, dependensi baru, atau render ulang.

## Target (persentil ke-75 pengguna)

| Metrik | Baik |
|---|---|
| LCP (Largest Contentful Paint) | ≤ 2,5 detik |
| INP (Interaction to Next Paint) | ≤ 200 ms |
| CLS (Cumulative Layout Shift) | ≤ 0,1 |

## LCP

- Elemen terbesar di atas lipatan (biasanya gambar hero/judul) dimuat lebih dulu: prioritas tinggi,
  tidak lazy, ukuran sesuai tampilan, format modern.
- Data untuk konten utama diambil paralel, bukan berantai (hindari waterfall: A selesai baru B).
- Font: tampilkan fallback selama memuat; batasi jumlah varian.

## INP

- Handler interaksi ringan; pekerjaan berat dipecah, ditunda, atau dipindah ke worker.
- Input pencarian/filter memakai debounce. Hindari render ulang seluruh halaman untuk perubahan kecil:
  letakkan state sedekat mungkin dengan pemakainya.
- Memoisasi hanya bila profil menunjukkan render mahal, bukan di mana-mana.

## CLS

- Gambar, video, iframe, dan iklan punya dimensi/aspect ratio yang dipesan.
- Skeleton berukuran sama dengan konten akhirnya. Konten tidak disisipkan di atas konten yang sudah
  terlihat kecuali karena aksi pengguna.

## Bundle

- Setiap dependensi baru dipertimbangkan ukurannya; utamakan yang sudah ada di project.
- Pecah kode per route; komponen berat yang jarang dipakai (editor, grafik, peta) dimuat saat dibutuhkan.
- Impor spesifik, bukan seluruh library. Tidak mengirim kode khusus server ke browser.

## Data dan daftar

- Paginasi atau virtualisasi untuk daftar ratusan baris ke atas.
- Cache server state dengan waktu basi yang masuk akal; jangan memuat ulang data yang sama di setiap
  komponen.
- Gambar di daftar memakai lazy loading dan ukuran thumbnail, bukan ukuran asli.

## Cara memeriksa

Gunakan alat yang tersedia di project (adapter §11): laporan ukuran bundle, profiler render, atau audit
lab. Sebutkan angka sebelum/sesudah bila mengklaim perbaikan performa.
