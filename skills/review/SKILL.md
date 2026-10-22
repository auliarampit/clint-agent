---
name: review
description: Meninjau perubahan kode lalu langsung memperbaikinya sampai bersih — kesesuaian dokumen/aturan, clean code & arsitektur, keamanan, dan desain. Terpicu otomatis oleh hook setelah sesi selesai mengubah kode; bisa juga dipanggil manual ("cek dulu sebelum MR"). Untuk MR orang lain hanya meninjau tanpa mengubah.
argument-hint: [branch | !nomor-MR] [--only]
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
- **Mode hanya-tinjau** bila argumen `--only`, atau MR milik orang lain
  (`glab mr view` / `gh pr view` → author bukan user). Mode ini tidak mengubah apa pun.

## 2. Pilih peninjau sesuai ukuran diff (hemat token)

`python3 "$R/scripts/review-prep.py" <path> <base> [--design]` → `pr.diff` di folder kerja PR, `ukuran=`,
`sensitif=`, dan kandidat auditor beserta buktinya (aturan skill `develop` 5.3: ukuran skrip batas bawah,
kandidat titik awal). Isi diff yang menyentuh auth, token, query, atau pembayaran = area sensitif walaupun nama
filenya netral.

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
- potongan rencana bila branch ini berasal dari rencana (`grep -l <branch> <docs.plans>/*.md`), selain itu tidak ada;
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
