---
name: review
description: Meninjau perubahan kode lalu langsung memperbaikinya sampai bersih — kesesuaian dokumen/aturan, clean code & arsitektur, keamanan, dan desain. Mode `fitur` memeriksa fitur/layar yang sudah ada tanpa diff ("cek layar X sudah sesuai prototipe?", "modul Y ada bug?"). Terpicu otomatis oleh hook setelah sesi selesai mengubah kode; bisa juga dipanggil manual ("cek dulu sebelum MR"). Untuk MR orang lain hanya meninjau tanpa mengubah.
argument-hint: [branch | !nomor-MR | fitur "<nama fitur/layar>" [--desain]] [--only]
---

# Review: tinjau dan perbaiki

## 1. Tentukan yang ditinjau

Laporan memakai bahasa user (baris *Bahasa clint* di konteks sesi; default English); sebut bahasa itu di
prompt agent. `R` = path plugin dari baris *Sesi clint* di konteks sesi (cadangan `R=$(cat ~/.config/clint/root)`).

**Tarik semua repo dulu** (tanpa token): `bash "$R/scripts/sync-repos.sh" .` supaya docs, design, dan kontrak di
`relatedRepos` yang dipakai `conformance-reviewer` dan auditor adalah versi terbaru. Repo kerja yang sedang diubah
otomatis hanya di-fetch (working tree kotor), jadi perubahan yang ditinjau tidak tersentuh.

- Tanpa argumen: perubahan di working tree (belum di-commit) **ditambah** commit branch saat ini
  yang belum ada di `origin/<baseBranch>` (`.claude/clint.json`).
- Branch/MR disebut: `git fetch`, tinjau diff branch itu terhadap base.
- `fitur "<nama>"`: fitur atau layar yang sudah ada di base branch, tanpa diff → ikuti **Mode fitur** di bawah,
  bukan langkah 2–4.
- **Mode hanya-tinjau** bila argumen `--only`, atau MR milik orang lain
  (`glab mr view` / `gh pr view` → author bukan user). Mode ini tidak mengubah apa pun.

## Mode fitur

Memeriksa fitur yang sudah berjalan (selisih dengan prototipe, bug, kesesuaian dengan dokumen) tanpa diff.
Repo sudah ditarik di atas.

1. Cakupan, tanpa token:
   `python3 "$R/scripts/review-prep.py" . --fitur "<nama>" --kata <kata1,kata2> [--design]`.
   `--kata` = nama fitur di kode, yang biasanya berbahasa Inggris (folder fitur, komponen, route), dipisah koma;
   tebak dari nama fitur, atau satu `ls`/`git grep -il` singkat bila belum tahu. `--design` bila `docs.design` bukan
   `TIDAK ADA`. Cakupan meleset (kosong atau berisi fitur lain) → perbaiki `--kata` dan jalankan ulang; jangan
   menelusuri kode sendiri.
2. Peninjau, bersamaan dalam satu pesan. Masing-masing diberi path `cakupan.txt`, baris `rujukan` yang sesuai
   perannya (dokumen untuk `conformance-reviewer`, desain untuk `design-auditor`, api untuk `api-contract-auditor`),
   dan daftar peninjau lain:
   - `--desain` → hanya `design-auditor`;
   - selain itu → `code-reviewer` + `conformance-reviewer` + `design-auditor` (bila ada kandidatnya) + maksimal 2
     auditor lain dengan skor kandidat tertinggi yang memang relevan dengan isi fitur.
3. Gabungkan tanpa token: `python3 "$R/scripts/merge-findings.py" <folder> --putaran 1` → `findings.md`.
4. `--only` → laporan (bagian 5) lalu berhenti. Selain itu perbaikan lewat alur `develop`, karena kode di base
   branch perlu branch, test, dan MR: jalankan skill `clint:develop` dengan tugas
   `perbaiki temuan review fitur <nama> (<path findings.md>)`. Bagian 3–4 di bawah tidak dipakai.

## 2. Pilih peninjau sesuai ukuran diff (hemat token)

`python3 "$R/scripts/review-prep.py" <path> <base> [--design]` → `pr.diff` di folder kerja PR, `ukuran=`,
`sensitif=`, dan kandidat auditor beserta buktinya (aturan skill `develop` 5.3: ukuran skrip batas bawah,
kandidat titik awal). Isi diff yang menyentuh auth, token, query, atau pembayaran = area sensitif walaupun nama
filenya netral.

Lalu sekali, sebelum peninjau dipanggil: `python3 "$R/scripts/run-checks.py" <path> --base <base>` → `checks.md`
di folder kerja PR (lint file berubah, typecheck, test terkait, paralel). Peninjau membaca hasilnya, tidak
menjalankan ulang.

| Diff | Peninjau |
|---|---|
| ≤ ~30 baris di area biasa | **tanpa agent**; periksa sendiri dengan checklist skill platform |
| ≤ ~150 baris di area biasa | `code-reviewer` **sendirian** (ia juga memeriksa kebenaran logika dan kesesuaian dengan rencana bila ada) |
| lebih besar, atau menyentuh auth/data/migrasi/kontrak/pembayaran | `conformance-reviewer` + `code-reviewer` + **maksimal 2** auditor paling relevan dari daftar di bawah |
| MR orang lain (`--only`) | `conformance-reviewer` + `code-reviewer` + semua auditor yang pemicunya tersentuh |

Pemicu auditor:
- `security-auditor`: auth, API/HTTP, storage, konfigurasi, dependensi, WebView/deep link;
- `database-auditor`: migrasi, skema, repository/akses data, query;
- `api-contract-auditor`: endpoint, DTO/skema validasi, file kontrak;
- `design-auditor`: UI **dan** `docs.design` bukan `TIDAK ADA`;
- `accessibility-auditor`: komponen tampilan, form, dialog, navigasi, warna;
- `performance-auditor`: dependensi baru, daftar besar, gambar, pengambilan data, komponen yang sering dirender,
  startup/animasi (mobile), query/endpoint di jalur panas, job, ekspor/impor data (backend).

Jalankan yang terpilih **bersamaan** (satu pesan). Input ke setiap peninjau:
- path diff dan folder kerja PR dari `review-prep.py`, bukan isi diff (folder itu di dalam `.git`, tidak ikut
  ter-commit); peninjau menulis bloknya sendiri ke `<folder>/temuan-<agent>.md`;
- potongan rencana bila branch ini berasal dari rencana (`grep -l <branch> <docs.plans>/*.md`):
  `python3 "$R/scripts/plan-slice.py" <rencana> PR-<n> --dir <path>` → path `potongan=`, selain itu tidak ada;
- path `checks.md`;
- daftar peninjau lain di putaran ini, supaya wilayah auditor yang ikut tidak diperiksa ulang.

Setiap peninjau menutup laporannya dengan `VERDICT: LGTM | Needs Fix` dan `TEMUAN:` berlabel
`[Critical]`/`[Major]`/`[Minor]`/`[Low]`. Semua tingkat, termasuk Low, wajib diperbaiki.
Tunggu semua peninjau selesai, baru gabungkan tanpa token: `python3 "$R/scripts/merge-findings.py" <folder>
--putaran <n>` → `<folder>/findings.md`, verdict per agent, dan `putaran_ulang=`.

## 3. Perbaiki otomatis (kecuali mode hanya-tinjau)

- Kumpulkan dulu, perbaiki sekaligus: kirim ke agent `developer` dalam **satu** pesan: path `findings.md`, semua
  temuan di kode yang berubah (kecuali `(luar cakupan)` atau yang bertentangan dengan aturan
  project). Kerjakan di tempat yang sama
  Jangan commit. Tempatnya: tanpa argumen → di tempat (perubahan yang ditinjau memang ada di working tree ini);
  branch/MR lain → `bash "$R/scripts/repo-busy.sh" . <sid>`: `bebas` → `git switch` di repo utama, `dipakai` →
  worktree (aturan skill `develop` langkah 5.1).
- Putaran ulang: jalankan ulang `review-prep.py`, lalu **hanya** peninjau di `putaran_ulang=`, dengan
  path `findings.md`; mereka memverifikasi temuannya dan baris yang berubah karena perbaikan. Maksimal 3 putaran.
  Temuan Low tidak memicu putaran ulang (aturan skill `develop` 5.3): `hanya_low=ya` → cukup `run-checks.py`
  lulus dan laporan `developer` menandai setiap butir.

## 4. Tandai sudah ditinjau

Setelah selesai (lulus maupun berhenti di batas putaran), jalankan perintah penanda yang
diberikan hook (`... stop-review.sh --mark`, persis seperti di pesan hook) bila tinjauan ini dipicu hook. Ini mencegah
tinjauan berulang untuk perubahan yang sama.

## 5. Laporan singkat

Setiap temuan kode ditulis dengan `path:baris`, tingkat, cuplikan **sekarang**, dan **usulan**. Untuk MR orang
lain, komentar *suggestion* di MR (`"$R/scripts/mr-suggestions.py" <n> <file.json> --mention`, field `tingkat`
diisi) hanya dipasang bila user memintanya atau `mr.reviewComments` di `clint.json` bernilai `true` (default
`false`, supaya tidak dobel dengan bot review di server).

Isi: verdict per peninjau, apa saja yang sudah diperbaiki, temuan yang masih tersisa (bila batas
putaran tercapai), dan usulan yang dilewati beserta alasannya. Tutup dengan blok **Berikutnya** (aturan skill `develop` bagian 6),
mis. `[siap] /clint:develop` untuk membuat MR dari perubahan ini.
