# Develop · tinjauan (langkah 5.3 dan 5.3b)

Dibaca orkestrator `develop` (dan `review`) saat sampai langkah tinjauan. Ringkasan ada di `SKILL.md` 5.3.

## 5.3 Tinjauan sesuai ukuran

Setelah implementasi, satu perintah tanpa token:
`python3 "$R/scripts/review-prep.py" <path kerja> <base> [--design]` (`--design` bila `docs.design` bukan
`TIDAK ADA`) → menulis `pr.diff` di folder kerja PR, lalu mencetak `folder=`, `ukuran=`, `sensitif=`, dan
`kandidat <auditor> skor=...: <bukti>` (path dan isi baris yang memicu). Ukuran dari skrip adalah **batas bawah**:
boleh dinaikkan, tidak boleh diturunkan. Pilih auditor dari kandidat; boleh menambah auditor di luar kandidat bila
isi diff menunjukkannya.

- **Auditor wajib** (`wajib=` dari skrip, semua ukuran kecuali Mikro): `design-auditor` (UI dan ada prototipe),
  `security-auditor`, dan `performance-auditor` dipanggil bila menjadi kandidat. Mereka tidak dihitung
  dalam kuota di bawah. Untuk **Kecil**, skrip hanya mewajibkan `security-auditor`, serta design/perf bila
  buktinya kuat (skor ≥ 6, atau perf kena path dependensi/aset); sekadar menyentuh satu file UI tidak cukup.
  Mikro yang menyentuh UI dicocokkan sendiri dengan prototipe terbaru.
- **Mikro**: tanpa agent conformance-reviewer.
- **Kecil**: satu `code-reviewer` yang juga memegang conformance (rencana, dokumen, aturan project) dan a11y
  (WCAG dasar bila UI tersentuh), tanpa `conformance-reviewer`/`accessibility-auditor` terpisah, + auditor wajib.
  Kandidat a11y dengan skor tinggi (form, dialog, warna) boleh dinaikkan jadi auditor sendiri.
- **Sedang/Besar**: `conformance-reviewer` + `code-reviewer` + auditor wajib + **maksimal 2** auditor lain dari
  tabel di bawah yang paling relevan dengan diff (database/kontrak untuk data dan API, aksesibilitas untuk UI).
- `code-reviewer` selalu memeriksa kebenaran logika (race, kasus tepi, galat), sendirian maupun bersama peninjau lain.

Jalankan yang terpilih **bersamaan** (satu pesan), masing-masing diberi `<path kerja>`, base branch, bagian
rencana, dan **daftar peninjau lain di putaran ini** (wilayah auditor yang ikut dipanggil tidak diperiksa ulang
peninjau umum). `code-reviewer` yang dipanggil tanpa peninjau lain (PR Kecil) diberi tahu "sendirian": ia juga
memeriksa kebenaran logika dan kesesuaian dengan rencana.

| Agent | Kapan | Fokus |
|---|---|---|
| `conformance-reviewer` | selalu | kesesuaian rencana, dokumen, aturan project |
| `code-reviewer` | selalu | clean code, clean architecture |
| `security-auditor` | diff menyentuh auth, API/HTTP, storage, konfigurasi, dependensi, WebView/deep link | celah keamanan |
| `design-auditor` | diff menyentuh UI **dan** `docs.design` bukan `TIDAK ADA` | selisih dengan prototype |
| `accessibility-auditor` | diff menyentuh komponen tampilan, form, dialog, navigasi, atau warna | WCAG 2.2 AA |
| `performance-auditor` | diff menambah dependensi, menyentuh daftar besar, gambar, pengambilan data, komponen yang sering dirender, startup/animasi (mobile), query, endpoint di jalur panas, job, atau ekspor/impor data (backend) | target performa ketat per platform |
| `database-auditor` | diff menyentuh migrasi, skema, repository/akses data, atau query | keamanan migrasi, integritas, indeks, N+1 |
| `api-contract-auditor` | diff menyentuh endpoint, DTO/skema validasi, atau file kontrak | kesesuaian dengan API contract, perubahan merusak |

**Folder kerja PR** (dipakai bersama semua agent PR ini): `<git-common-dir>/clint/<branch>/`
(`git -C <path kerja> rev-parse --path-format=absolute --git-common-dir`; di dalam `.git`, jadi tidak ikut
ter-commit).
- `pr.diff` (dari `review-prep.py`): peninjau diberi **path**-nya, bukan isi diff;
- `rencana-PR-<n>.md` (dari `plan-slice.py`) dan `checks.md` (dari `run-checks.py` yang dijalankan `developer`):
  peninjau diberi path keduanya, tidak membaca rencana utuh dan tidak menjalankan ulang lint/typecheck/test;
- `temuan-<agent>.md`: blok keluaran tiap peninjau, ditulis peninjau sendiri (beri path folder di prompt);
- `findings.md`: gabungan dari `merge-findings.py`.

Setiap peninjau menutup laporan dengan blok seragam `VERDICT: LGTM | Needs Fix` + `TEMUAN:` berlabel
`[Critical]`/`[Major]`/`[Minor]`/`[Low]` (`path:baris · aspek · kategori · masalah`, `sekarang`, `usulan`,
`(luar cakupan)` bila perlu). Semua tingkat, termasuk Low, wajib diperbaiki dan menahan MR,
tetapi Low tidak memicu putaran ulang (lihat di bawah). Temuan
`(luar cakupan)` tidak menahan PR ini apa pun tingkatnya; yang Critical/Major disebut di laporan akhir.

**Kumpulkan dulu, perbaiki sekaligus.** Tunggu semua peninjau di putaran itu selesai, lalu gabungkan tanpa token:
`python3 "$R/scripts/merge-findings.py" <folder> --putaran <n>` → `findings.md` (urut per tingkat, temuan ganda
dengan path, baris, dan kategori sama digabung; luar cakupan dipisah), `verdict` per agent, jumlah per tingkat,
dan `putaran_ulang=` (peninjau yang memberi temuan). Lalu kirim ke `developer` dalam
**satu** pesan: path `findings.md`, semua temuan di kode yang diubah PR (kecuali luar cakupan), dan hasil lint/typecheck/test yang gagal bila ada. Jangan meneruskan temuan per peninjau begitu datang.
SendMessage ke agent yang sama bila masih ada. Usulan yang bertentangan dengan aturan project → lewati dan sebut
alasannya. `developer` menandai setiap butir diperbaiki/dilewati di laporannya.
Putaran ulang: jalankan ulang `review-prep.py` (memperbarui `pr.diff`), lalu **hanya** peninjau di `putaran_ulang=`,
dengan path `findings.md` + `pr.diff`; mereka memverifikasi temuannya dan baris yang berubah karena perbaikan,
bukan meninjau dari awal. `putaran_ulang=` hanya memuat peninjau dengan temuan Critical/Major/Minor; peninjau
yang hanya memberi Low tidak dipanggil lagi. `hanya_low=ya` → setelah `developer` memperbaiki, cukup
`run-checks.py` lulus dan laporannya menandai setiap butir `diperbaiki`/`dilewati`, tanpa tinjauan ulang.
**Maksimal 3 putaran perbaikan.** Masih ada temuan setelah itu → berhenti, laporkan
ke user, jangan buat MR. Temuan luar cakupan dan usulan yang dilewati karena bertentangan dengan aturan project
dicantumkan di deskripsi MR.

Hasil perbaikan Low di-commit **terpisah** dari commit utama (mis. `refactor: terapkan saran
tinjauan`, ikuti gaya commit repo) supaya mudah diperiksa di tab Commits MR dan bisa di-revert
sendiri. Bila perbaikan Critical/Major/Minor dan Low menyentuh baris yang sama, satukan di commit utama.

## 5.3b Ukur performa (`quality-gates.md` §2.4)

`performance-auditor` ada di `wajib=` → `developer` menjalankan harness adapter §11 untuk metrik yang disentuh
(startup, FPS/jank, memori termasuk sesi panjang, ukuran) sebelum dan sesudah, di perangkat acuan, lalu menulis
angkanya ke `docs/performa/baseline.md` dan deskripsi MR. Regresi terhadap target atau ambang = temuan Major.
Harness atau perangkat belum ada → status `performa: belum terukur, <alasan>` dan MR **Draft**, sama seperti
gerbang E2E di 5.4. Tidak pernah menulis target tercapai tanpa angka.
