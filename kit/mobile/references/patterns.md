# Pola feature mobile yang berulang

Dibaca bila task membuat atau mengubah daftar, paginasi, pull-to-refresh, empty/loading state, wizard,
optimistic UI, aksi async yang bisa ditap berulang, atau bottom sheet. Notasi `§N` = bagian adapter
(`.claude/mobile-stack.md`); "Step N" = langkah di `skill-mobile/SKILL.md`.

Pola berikut portable lintas project; nama library-nya ambil dari adapter.

## Pagination / infinite scroll
Query bertingkat halaman + list yang memanggil halaman berikutnya saat mendekati ujung.
Selalu sertakan `keyExtractor` dengan id stabil, footer loading, dan `testID` pada list.

## Pull-to-refresh
Sambungkan `refreshControl` ke `refetch` + flag `isRefetching` dari query, bukan ke state
manual.

## Empty state
**Selalu** tampilkan setelah loading selesai dan data kosong — jangan pernah meninggalkan
layar kosong tanpa penjelasan. Beri `testID` sendiri. Berlaku juga saat "kosong" datang
dari respons yang **sukses** (200 dengan array/objek kosong), bukan cuma dari error atau
404 — jangan biarkan hasil kosong lolos begitu saja ke cabang "berhasil dimuat" tanpa
pengecekan panjang/isi eksplisit. Kalau ada lebih dari satu sumber data untuk halaman yang
sama (mis. jaringan dan salinan luring), cek kekosongan di **setiap** sumber, bukan cuma
yang paling sering dipakai.

## Skeleton / loading state
Skeleton saat load pertama; spinner refresh saat pull-to-refresh. **Jangan** memakai dialog
loading yang memblokir untuk data list — dialog blocking hanya untuk mutation (submit, hapus).

> Semua pembacaan dan mutation yang menunggu jaringan **wajib** punya indikator: skeleton,
> spinner inline, atau tombol dengan state disabled/loading. Tidak boleh ada request in-flight
> yang tidak terlihat user.

## Wizard multi-langkah
State ada di hook, **bukan** di parameter navigasi. Langkah dirender kondisional — jangan
bernavigasi antar langkah. Panggil navigasi hanya saat wizard selesai atau dibatalkan.
Bersihkan draft wizard saat sesi berakhir supaya data user sebelumnya tidak bocor.

## Optimistic UI
Untuk mutation yang butuh umpan balik instan: batalkan query terkait, simpan snapshot
sebelumnya, tulis optimistis, rollback di `onError`, invalidate di `onSettled`.

## Tap ganda pada aksi async yang bisa disusul

Saat sebuah handler async (panggilan native seperti `Linking`, atau efek samping lain di
luar manajer server-state project) bisa dipicu lagi sebelum panggilan sebelumnya selesai —
dua tap cepat ke item berbeda — dan hasilnya menyetel state UI (membuka modal, menyetel
pesan error) di blok `catch`/`then`, **jangan asumsikan urutan settle promise sama dengan
urutan tap user**. Promise dari tap pertama bisa selesai belakangan dan menimpa state yang
seharusnya milik tap kedua. Jaga dengan penghitung permintaan:

```tsx
const latestRequestId = useRef(0);

async function open(item: Item) {
  const requestId = (latestRequestId.current += 1);
  try {
    await doSomethingAsync(item);
  } catch {
    if (requestId === latestRequestId.current) {
      setFallback(item); // hanya tap TERAKHIR yang boleh menang
    }
  }
}
```

Manajer server-state modern (adapter §4/§5) biasanya sudah menangani ini sendiri untuk
query/mutation lewat library-nya (permintaan terbaru otomatis menang) — pola di atas untuk
efek samping async di **luar** lapisan itu, yang menyetel state lokal langsung dari hasil
promise.

---

## Daftar — FlatList untuk data, `map` hanya untuk grup tetap kecil

| Kasus | Pakai |
|---|---|
| Data dari API, hasil pencarian, konten yang panjangnya ditentukan data | `FlatList` / `SectionList` — **list-nya menjadi scroll container layar**. Konten lain masuk `ListHeaderComponent` / `ListFooterComponent`, keadaan kosong masuk `ListEmptyComponent` |
| Grup kecil yang panjangnya ditetapkan desain (±10 butir ke bawah, mis. 6 tile menu, baris jadwal harian) di dalam kartu atau di layar yang juga berisi konten lain | `map` di dalam `ScrollView` |

- **Jangan menaruh `FlatList` di dalam `ScrollView` searah.** Virtualisasi mati dan React
  Native memperingatkan nested VirtualizedList — kalau layar punya konten lain, jadikan
  konten itu header/footer list.
- `keyExtractor` dan `renderItem` didefinisikan bernama (Step 0c.5); `keyExtractor` boleh di
  level modul.
- Header yang berisi input teks dioper sebagai elemen dari komponen yang didefinisikan di
  level modul, **bukan** komponen inline — kalau tidak, input kehilangan fokus setiap render.
- Item yang dibingkai sebagai satu kartu di dalam `FlatList` menggambar tepinya sendiri
  (atas untuk item pertama, bawah untuk item terakhir), karena list tidak punya pembungkus
  kartu.

## Bottom sheet

Pakai library bottom sheet yang ditunjuk adapter §7. **Jangan merakit sheet sendiri** dari
`Modal` + scrim `Pressable` + animasi manual: swipe-to-close, keyboard, safe area, dan
aksesibilitas hampir selalu tertinggal. Kalau adapter belum menunjuk library, tanya user
sebelum menambah dependency.
