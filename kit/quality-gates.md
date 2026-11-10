---
paths:
  - "**/*.{ts,tsx,js,jsx,mjs,cjs,kt,kts,java,swift,dart,py,go,php,rb,cs,sql}"
---

# Gerbang kualitas: dipasang mesin, diukur di perangkat

> **Portable.** Berlaku di semua project (mobile, web, backend). Disalin `/clint:setup` ke
> `.claude/rules/quality-gates.md`. Aturan di dokumen lain (SonarQube, skill platform) menjelaskan *cara menulis*
> kode; dokumen ini menetapkan *apa yang wajib diperiksa mesin dan diukur* sebelum pekerjaan dinyatakan selesai.

Latar: audit Sprint 1–4 project pertama yang memakai clint menemukan 137 temuan walaupun lint, typecheck, 525
suite test, dan coverage 95,7% semuanya hijau. Sebagian besar lolos karena aturannya hanya ditegakkan disiplin
peninjau, bukan mesin, dan karena performa tidak pernah diukur.

## 1. Gerbang mesin wajib di MR

Dipasang saat `/clint:setup` (ditanya sekali ke user project, lalu dipasang semuanya) dan dijalankan oleh
skrip `lint` project supaya ikut `ciOnMr`. Nilai dan perintahnya dicatat di adapter §10.

| Gerbang | JS/TS (mobile, web, backend Node) | Bahasa lain | Ambang |
|---|---|---|---|
| Rule SonarQube | `eslint-plugin-sonarjs` config `recommended` | job `sonar` di pipeline MR (`sonar.pullrequest.*`) | 0 pelanggaran |
| Duplikasi | `jscpd` (`--min-tokens 50 --threshold 3`, folder sumber, tanpa test) | `jscpd` atau PMD CPD | ≤ 3% |
| Kode mati | `knip` (ekspor, berkas, dependensi tak terpakai; test tidak dihitung pemakai) | `staticcheck`/`deadcode` (Go), `vulture` (Python), padanan lain di adapter | 0 |
| Batas lapisan | `import/no-restricted-paths` atau `no-restricted-imports` sesuai lapisan di adapter §6 (presentation tidak mengimpor data/API/store mentah; fitur tidak mengimpor fitur lain) | `dependency-cruiser`, ArchUnit, `depguard` | 0 |
| Audit dependensi | `<pm> audit --audit-level=high` (`bun audit`, `npm audit`, `pnpm audit`) | `govulncheck`, `pip-audit`, `composer audit` | 0 high/critical tanpa alasan tertulis |
| Glosarium | bila ada `docs/glossary.md` (tabel *Terlarang → Pengganti*): `grep -rniw` istilah terlarang di locale, teks UI, dan pesan error | sama | 0 |

- **Sonar tidak berjalan di MR** (`sonar` tidak ada di `ciOnMr`): `eslint-plugin-sonarjs` atau job sonar MR
  **tidak boleh** dilewati. Ini satu-satunya penjaga rule Sonar sebelum merge.
- Pelanggaran diperbaiki, tidak dibungkam (`NOSONAR`, `eslint-disable` tanpa alasan, exclusion baru).
- User project menolak satu gerbang → adapter §10 menulis `TIDAK ADA (ditolak <tanggal>, <alasan>)`.
  `/clint:status` dan laporan `develop` menyebut gerbang yang belum terpasang di setiap laporan.
- Project lama yang baru memasang gerbang: pelanggaran lama dicatat sebagai PR perbaikan tersendiri; aturan
  tidak dimatikan untuk menunggu.

## 2. Pengukuran wajib (performa, memori, ukuran)

### 2.1 Harness ukur

Setiap project punya harness ukur yang bisa diulang dengan satu perintah per metrik, dibuat sebagai PR
pertama setelah setup (`chore/perf-baseline`) bila belum ada. Perintah dan perangkatnya dicatat di adapter
§11; angka mentah dan median di `docs/performa/baseline.md` (perangkat, versi OS, commit, tanggal, perintah).
Median dari ≥ 5 putaran, pada build rilis/produksi, bukan dev.

| Platform | Metrik dan alat minimal |
|---|---|
| Mobile | startup dingin sampai layar pertama interaktif (`am start -W` + flow E2E; iOS `devicectl`/`xctrace` App Launch); FPS dan jank saat scroll daftar dan mengetik (Android `dumpsys gfxinfo` framestats, Flashlight sebagai pelengkap; iOS `xctrace` Animation Hitches); memori (Android `dumpsys meminfo` TOTAL PSS, Native Heap, Graphics; iOS `xctrace` Activity Monitor atau Allocations); ukuran APK/AAB/IPA dan bundle JS/OTA |
| Web | Lighthouse CI pada build produksi (LCP, CLS, TBT) dan INP dari `web-vitals`; ukuran JS awal per route (bundle analyzer); heap JS (`performance.memory` atau heap snapshot DevTools/Playwright) |
| Backend | uji beban (`k6`/`autocannon`/setara) p50/p95/p99 dan galat per endpoint di jalur panas; RSS dan heap proses; `EXPLAIN` query di jalur panas |

**Perangkat acuan** wajib fisik untuk mobile (adapter §11). Emulator/simulator hanya bila tidak ada perangkat,
dan angkanya ditulis "indikatif".

### 2.2 Skenario sesi panjang (memori)

Kebocoran memori tidak terlihat di satu layar. Harness wajib punya skenario berikut, dengan ambang default
(adapter §11 boleh lebih ketat, tidak boleh lebih longgar tanpa persetujuan user):

| Platform | Skenario | Ambang (Major bila dilewati) |
|---|---|---|
| Mobile | 10× masuk-keluar layar yang sama; dan baca/gulir panjang (±100 halaman atau item) | 10× masuk-keluar: memori kembali ke ±5% awal. Sesi panjang: kenaikan < 50 MB dari titik awal (mis. halaman 10) ke titik akhir (halaman 100) |
| Web | 10× navigasi bolak-balik antar route utama | heap setelah GC naik < 10% dari awal |
| Backend | 10.000 permintaan ke endpoint panas | RSS/heap stabil, naik < 10% setelah pemanasan |

### 2.3 Anggaran aset

- Gambar raster ≤ 3× ukuran tampil terbesarnya (px); ikon ≤ 30 KB per berkas, SVG/vektor diutamakan.
- Audio terkompresi (`ogg`/`aac`/`m4a`). Pengecualian: suara notifikasi iOS (`wav`/`caf`/`aiff`, ≤ 30 dtk),
  dipangkas sependek mungkin.
- Font hanya berat dan subset yang dipakai.
- Kenaikan total aset atau bundle > 50 KB per MR dijelaskan di deskripsi MR beserta angkanya.
- Alat kompresi (mis. `pngquant`, `oxipng`, `ffmpeg`, `svgo`) dipasang di mesin, bukan dependency proyek.

### 2.4 Kapan wajib diukur

- **PR yang memicu `performance-auditor`** (daftar, startup, animasi, aset, dependensi, query, endpoint panas,
  job): angka sebelum/sesudah dari harness wajib ada di MR dan di `baseline.md`.
- Harness atau perangkat belum ada → MR dibuat **Draft** dengan status "performa belum terukur" dan alasannya;
  pekerjaan tidak dinyatakan selesai sampai angka ada atau user menyetujui pengecualian tertulis.
- **Penutupan modul dan akhir sprint**: seluruh harness dijalankan ulang dan `baseline.md` diperbarui. Regresi
  terhadap target atau ambang = PR perbaikan.
- Tidak pernah menulis "target tercapai" tanpa angka.

## 3. Penutupan modul

Modul (atau sprint) belum selesai sebelum semua ini ada dan dilampirkan di laporan:

1. **Matriks FR/AC → kode**: setiap FR dan AC di PRD modul punya `path:baris` implementasi dan test/E2E yang
   membuktikannya. FR tanpa bukti = Major.
2. **Review fitur per layar/endpoint** (`/clint:review fitur <nama>`) terhadap PRD, kontrak, dan prototipe
   **terbaru** (bukan versi saat rencana dibuat).
3. **Sapu duplikasi dan kode mati** di seluruh repo (gerbang §1 dijalankan pada seluruh folder sumber).
4. **Harness ukur** dijalankan (§2.4).
5. **Deviasi** (§4) yang terbuka disebut beserta dokumen yang belum diperbarui.

## 4. Deviasi dan saran tinjauan

- **Deviasi**: setiap keputusan yang membuat kode berbeda dari PRD, SAD, STD, kontrak, atau prototipe dicatat di
  bagian `## Deviasi` rencana: ID, tanggal, pemutus, isi keputusan, dan dokumen yang harus diubah. Kode yang
  menyimpang tanpa ID deviasi atau Change Request = Major. Deviasi yang lebih dari satu sprint belum diturunkan ke
  dokumennya dilaporkan `/clint:status`.
- **Saran tinjauan** (komentar MR, saran senior, temuan luar cakupan): diterapkan sebelum merge, atau dijadikan
  butir rencana/issue ber-ID. Menandai RESOLVED wajib menyebut commit yang mengubah baris itu. Suggestion
  GitLab/GitHub hanya berisi kode pengganti, tidak pernah prosa.
