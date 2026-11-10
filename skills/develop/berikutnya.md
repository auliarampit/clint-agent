# Berikutnya: blok terakhir wajib di semua skill clint

Blok berisi langkah siap ketik untuk **project sesi ini saja**, setiap baris diberi tanda:

| Tanda | Arti |
|---|---|
| `[paralel]` | PR saling bebas: satu run (develop memprosesnya bersamaan, maks 3), atau satu sesi per PR |
| `[siap]` | satu langkah yang bisa langsung dikerjakan |
| `[urutan, setelah X]` | baru bisa dikerjakan setelah X selesai |
| `[lanjutkan]` | PR yang tertahan atau setengah jalan |
| `[E2E]` | MR Draft yang menunggu E2E (`/clint:test`) |
| `[terblokir]` | menunggu pihak lain; sebut penyebabnya |

```
Berikutnya (magnet-rezeki/mobile, sesi baru: ketik /clear dulu):
[paralel] /clint:develop docs/plans/mr-mob-11.md PR-2,PR-3
[urutan, setelah PR-2,PR-3] /clint:develop docs/plans/mr-mob-11.md PR-4,PR-5,PR-8
[terblokir] PR-7: seeder api data inbox
Sedang dikerjakan sesi lain: PR-1 (ditinjau)
```

Cara menyusun (tanpa menebak):
1. Rencana yang sedang dikerjakan → **jalankan ulang** `python3 "$R/scripts/plan-status.py" <rencana> --session <sid>`
   di akhir run dan pakai baris *Berikutnya* dari skrip apa adanya. Skrip sudah membuang PR yang diklaim sesi
   lain, yang selesai, dan yang MR-nya open, jadi saran tidak mengulang PR yang sedang dikerjakan sesi lain.
2. Lalu butir *Perlu perhatian* dari run ini.
3. Lalu butir laporan `status` milik project ini, dari skrip (bukan membaca `terakhir.json` sendiri):
   `python3 "$R/scripts/update-report.py" periksa-mr; python3 "$R/scripts/update-report.py" langkah --dir <repo utama> --session <sid>`.
   `periksa-mr` membuang butir yang MR-nya sudah merged dan memindahkan yang MR-nya masih open ke "menunggu
   review"; `langkah` membuang butir yang diklaim sesi lain dan butir project lain. Pakai keluarannya apa adanya;
   butir yang baru dikerjakan run ini juga tidak ditulis lagi.
4. Langkah yang sedang dikerjakan sesi lain (klaim di `~/Library/Logs/clint/kerja/`, ditandai skrip "Sedang
   dikerjakan sesi lain") **tidak pernah** ditulis sebagai langkah siap ketik, hanya sebagai baris info.
5. Tidak ada langkah → "Menunggu review: !n" bila ada; sisanya dipegang sesi lain → **"Tidak ada tugas baru untuk
   sesi ini; sisanya sedang dikerjakan sesi lain."**; selain itu **"Tugas hari ini sudah selesai semua."**

Run mengerjakan 3 PR atau lebih, atau masih ada PR tersisa dari batas per run → judul blok menyebut
"sesi baru: ketik /clear dulu". Maksimal 5 langkah.
