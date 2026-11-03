# Performa mobile — target ketat, diukur, bukan dirasa

Dibaca **selalu** untuk task Tier 2/3, dan untuk task apa pun yang menyentuh daftar, scroll, gambar,
animasi, startup, pengambilan data, dependensi baru, atau layar yang sering dirender. Notasi `§N` = bagian
adapter (`.claude/mobile-stack.md`). Nama library diambil dari adapter; dokumen ini tidak memilih library.

Standar Badr: **performa terbaik, bukan "cukup"**. Pelanggaran aturan di dokumen ini adalah temuan
**Wajib** saat review, bukan saran.

## 1. Target

Diukur di **release build** (bukan dev/debug, yang bisa 5–10× lebih lambat) pada **perangkat acuan** di
adapter §11. Tanpa perangkat acuan → Android kelas menengah (RAM 4 GB) dan iPhone generasi 3 tahun lalu.
Adapter §11 boleh menetapkan angka lebih ketat, tidak boleh lebih longgar tanpa persetujuan user.

| Metrik | Target |
|---|---|
| Cold start sampai layar pertama bisa dipakai | ≤ 2 dtk Android acuan, ≤ 1,5 dtk iOS |
| Warm start | ≤ 1 dtk |
| Frame rate saat scroll, animasi, transisi | 60 fps stabil (120 fps di layar ProMotion bila project mendukung); frame JS dan UI ≤ 16 ms |
| Frame yang terbuang (dropped frames) saat scroll daftar panjang | ≤ 1% |
| Respons tap | umpan balik visual ≤ 100 ms; transisi navigasi mulai ≤ 100 ms |
| Konten layar | skeleton/placeholder muncul seketika; data dari cache ≤ 300 ms; dari jaringan ≤ 1 dtk (jaringan 4G) |
| Pekerjaan sinkron di thread JS | tidak ada blok > 50 ms di jalur interaksi |
| Memori | 10× masuk-keluar layar yang sama: kembali ke ±5% awal; sesi panjang (±100 halaman/item): naik < 50 MB dari titik awal ke akhir (`quality-gates.md` §2.2) |
| Ukuran bundle JS / update OTA | setiap kenaikan > 50 KB (gzip) dijelaskan di MR |
| Skor alat profil (mis. Flashlight) | ≥ 90 untuk alur yang diubah, bila alatnya dipakai project |

## 2. Render

- **Komponen murni dan stabil.** Item daftar dan komponen yang dirender berulang dibungkus memo; prop
  callback dan objek stabil (fungsi bernama di level modul atau `useCallback`; objek konstanta di level
  modul). Prop inline baru di setiap render = memo tidak berguna.
- **State sedekat mungkin dengan pemakainya.** State lokal yang berubah cepat (input, scroll, timer) tidak
  diangkat ke parent layar.
- **Store global dibaca lewat selector sempit**: komponen hanya berlangganan field yang dipakainya, bukan
  seluruh store. Context hanya untuk nilai yang jarang berubah; nilai yang sering berubah dipisah ke context
  sendiri atau store.
- **Tidak ada kerja mahal di badan render**: sort, filter, map besar, format tanggal/angka massal dihitung
  sekali (`useMemo` dengan dependensi tepat) atau di lapisan data.
- **Tidak ada `setState` beruntun** untuk satu perubahan; satukan dalam satu update atau reducer.
- **Efek dibersihkan**: listener, interval, subscription, dan permintaan yang masih berjalan dibatalkan saat
  unmount. Efek tidak memicu render berantai (efek → setState → efek).

## 3. Daftar

- Daftar data **selalu** komponen virtualisasi dari adapter §7 (mis. `FlashList` bila project memakainya,
  selain itu `FlatList`/`SectionList`). Tidak pernah `map` di dalam `ScrollView` untuk data dari API.
- `keyExtractor` memakai id stabil; `renderItem` mengembalikan komponen item yang dibungkus `memo`, dan
  `renderItem` sendiri stabil (`useCallback` atau fungsi level modul). Diperiksa dengan grep: setiap komponen
  item daftar punya `memo(`.
- Tinggi item tetap → berikan ukuran item (`getItemLayout` atau `estimatedItemSize`, sesuai komponen).
- Atur jendela render sesuai layar: jumlah render awal ≈ item yang terlihat; jangan menaikkan
  `windowSize`/`initialNumToRender` untuk menutupi masalah render item yang lambat.
- Item ringan: tanpa efek, tanpa fetch per item, tanpa bayangan/blur berat; gambar item memakai ukuran
  thumbnail.
- Paginasi/infinite scroll untuk data yang bisa tumbuh; ambang muat berikutnya cukup awal supaya pengguna
  tidak melihat ujung kosong.

## 4. Gambar dan aset

- Semua gambar jaringan lewat komponen gambar dari adapter §7 yang punya cache memori dan disk.
- Minta ukuran dari server/CDN sesuai tampilan (thumbnail di daftar, ukuran penuh hanya di detail).
  Gambar didekode sebesar tampilannya, bukan sebesar file aslinya.
- Dimensi atau `aspectRatio` selalu dipesan supaya tata letak tidak melompat.
- Gambar di atas lipatan layar berikutnya boleh di-prefetch; sisanya dimuat saat dibutuhkan.
- Aset lokal dikompresi (WebP/AVIF bila didukung, SVG untuk ikon) dan mengikuti anggaran `quality-gates.md`
  §2.3: raster ≤ 3× ukuran tampil terbesar (ikon 88 dp → ≤ 264 px), ikon ≤ 30 KB, audio `ogg`/`aac`/`m4a`
  kecuali suara notifikasi iOS (`wav`/`caf`/`aiff`, ≤ 30 dtk), font hanya berat yang dipakai.
- Perubahan di folder aset dan konfigurasi app (`app.json`/`app.config.*`) menyebut ukuran sebelum/sesudah di MR.

## 5. Animasi dan gestur

- Animasi berjalan di **thread UI** (native driver atau worklet dari library animasi di adapter §7), bukan
  di thread JS.
- Animasikan `transform` dan `opacity`; hindari menganimasikan `width`/`height`/`top`/`margin` yang memicu
  layout ulang.
- Gestur yang menggerakkan elemen ditangani di thread UI; tidak ada `setState` per frame.
- Hormati *reduce motion* (lihat `accessibility.md`).

## 6. Startup

- Tidak ada pekerjaan berat saat modul dimuat (parse besar, loop, inisialisasi SDK) di file yang diimpor
  layar pertama.
- Inisialisasi yang tidak dibutuhkan layar pertama (analytics, remote config, SDK pihak ketiga, prefetch)
  ditunda sampai setelah frame pertama atau setelah interaksi selesai.
- Layar dan library berat yang jarang dipakai (peta, kamera, editor, grafik, PDF) dimuat saat dibutuhkan.
- Splash/layar awal tetap tampil sampai layar pertama siap dipakai, tanpa layar putih atau lompatan.
- Engine JS yang dioptimalkan (mis. Hermes) harus aktif; cek adapter §2. Mematikannya = tanya user.

## 7. Data dan jaringan

- Permintaan independen dijalankan **paralel**, bukan berantai.
- Server state lewat lapisan cache di adapter §4/§5: data yang sama tidak diambil ulang di setiap komponen;
  waktu basi diatur sesuai sifat data; refetch saat fokus/foreground tidak membanjiri server.
- Respons besar dipaginasi di server, bukan dipotong di klien.
- Input pencarian/filter memakai debounce (±300 ms) dan membatalkan permintaan sebelumnya.
- Data yang dibutuhkan layar berikutnya boleh di-prefetch saat pengguna menunjukkan niat (mis. menekan item).
- Penyimpanan lokal yang sinkron dan cepat untuk data kecil; jangan menyimpan/membaca objek besar di jalur
  render.

## 8. Thread JS

- Pekerjaan > 16 ms di jalur interaksi dipecah, ditunda setelah interaksi, atau dipindah ke native/worklet.
- JSON besar, kriptografi, dan pemrosesan gambar tidak dijalankan di thread JS saat layar sedang dipakai.
- `console.log` tidak tersisa di kode release (mahal di thread JS dan bocor ke log).

## 9. Dependensi dan bundle

- Dependensi baru = **wajib tanya** (Step "When to Stop and Ask"). Sertakan ukuran (gzip), alternatif yang
  sudah ada di project, dan dampaknya ke startup.
- Impor spesifik, bukan seluruh library. Hindari library yang membawa polyfill besar atau data lokal penuh
  (mis. semua locale tanggal) bila hanya sebagian yang dipakai.

## 10. Cara mengukur dan melapor (wajib)

1. Ukur dengan harness adapter §11 (perintah per metrik: startup dingin, FPS/jank, memori, sesi panjang,
   ukuran) di release build pada **perangkat fisik** acuan. Emulator/simulator hanya bila tidak ada perangkat,
   dan angkanya ditulis "indikatif". Harness belum ada → buat dulu sesuai `quality-gates.md` §2.1.
2. PR yang menyentuh daftar, startup, animasi, aset, dependensi, atau layar sesi panjang: angka **sebelum dan
   sesudah** di MR dan di `docs/performa/baseline.md`.
3. Tidak bisa diukur (perangkat/alat tidak tersedia) → MR **Draft** dengan status "performa belum terukur"
   beserta alasannya (`quality-gates.md` §2.4). Pekerjaan belum selesai sampai angka ada atau user menyetujui
   pengecualian tertulis. **Jangan pernah mengklaim target tercapai tanpa angka.**
4. Regresi terhadap target di bagian 1 menahan MR sampai diperbaiki atau user menyetujui pengecualiannya.
5. Bagian lama yang **sudah** di bawah target sebelum PR ini: PR tidak boleh memperburuknya, dan selisihnya
   dilaporkan sebagai utang performa (angka + penyebab dugaan), bukan penahan MR. Bila PR memang menyentuh
   penyebabnya, perbaiki sekalian selama masih dalam lingkup; bila tidak, sarankan tugas terpisah.
