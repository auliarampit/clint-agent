---
name: jalankan
description: Satu-satunya perintah kerja — dari perbaikan kecil sampai modul penuh. Menentukan sendiri perlu rencana atau tidak, membuat/memperbarui rencana bila perlu, lalu mengerjakan semua PR (paralel bila tidak saling bergantung), meninjau dan memperbaiki otomatis, menguji, membuat MR, dan memberi satu laporan di akhir. Pakai untuk permintaan kerja apa pun ("kerjakan X", "perbaiki Y", "jalankan rencana ini", "kerjakan hasil cek").
argument-hint: <deskripsi tugas | ID modul | path-rencana> [PR-x..PR-y]
---

# Jalankan satu modul end-to-end

Kamu orkestrator untuk banyak PR sekaligus. Subagent tidak bisa memanggil subagent lain, jadi
**kamu** yang memanggil setiap agent. User hanya ingin dihubungi di akhir, kecuali ada
pertanyaan teknis yang benar-benar memblokir.

## 1. Prasyarat

- Baca `.claude/clint.json`. Tidak ada → berhenti, tawarkan `/clint:siapkan-project`.
- `git fetch origin --prune`. Tarik juga `relatedRepos` (`git -C <path> pull --ff-only` bila
  bersih) supaya rencana dan implementasi memakai dokumen dan desain terbaru.
- Cocokkan tugas dengan `surfaces[]` (dari path/app yang disebut, atau dari rencana). Tugas
  menyentuh app yang tidak ada di `surfaces[]` (mis. backend/web saat clint baru dipasang
  untuk mobile) → berhenti, sebut surface yang tidak tercakup, dan sarankan mengerjakannya
  tanpa clint (skill/rules project untuk app itu) atau menambah surface lewat
  `/clint:siapkan-project`. Tugas campuran → kerjakan hanya bagian surface yang tercakup bila
  user setuju.
- `df -h ~`. Tentukan paralelisme: sisa ≥ 20 GB → maks 3 PR sekaligus; 5–20 GB → 1; < 5 GB →
  berhenti dan laporkan.

## 2. Tentukan jalur (otomatis, jangan tanya user)

| Argumen | Jalur |
|---|---|
| Deskripsi tugas yang muat dalam **1 PR** (perbaikan, penyesuaian, butir feedback, temuan `cek` yang kecil) | langsung ke langkah 5 sebagai satu PR, **tanpa file rencana** |
| Tindak lanjut MR yang sudah ada ("terapkan saran reviewer di !123", komentar review) | kerjakan di **branch MR itu** (`git fetch` lalu `git switch <source_branch>`, tanpa branch/MR baru): langkah 5.2–5.5, push ke branch yang sama, MR tidak dibuat ulang. Butir yang bertentangan dengan aturan project atau memang disengaja → lewati dan sebut alasannya di laporan |
| "perbaiki pipeline !123", pipeline merah | panggil agent `pemulih-pipeline` untuk MR itu, laporkan hasilnya; selesai |
| Kosong, setelah `cek` di percakapan ini | pakai temuan "perlu dikerjakan" dari laporan itu sebagai argumen |
| ID/nama modul, atau tugas yang butuh > 1 PR | cari rencana di `docs.plans` (`grep -il <ID>`) |
| Path file rencana (di `docs.plans`, punya tabel *Urutan pekerjaan*) | pakai rencana itu |
| Path dokumen lain (feedback QA, bug report, MoM, notulen) | jadikan **sumber tugas**: ambil butir yang masih open dan menyangkut surface ini; muat 1 PR → langsung; lebih → `perencana` membuat rencana di `docs.plans` dari butir itu. Jangan mengubah dokumen sumber |

Untuk jalur rencana, panggil agent `perencana` bila:
- rencana belum ada → buat baru; atau
- dokumen/desain terkait berubah sejak rencana terakhir diubah
  (`git -C <relatedRepo> log --since=<tanggal commit terakhir rencana>` tidak kosong) → perbarui
  bagian PR yang belum selesai.

Bila `perencana` melaporkan butir **PERLU KEPUTUSAN USER** (konflik dokumen): tanyakan ke
user sekaligus dalam satu pesan (butir + rekomendasi), tulis jawabannya ke tabel
ketidakjelasan rencana, baru lanjut. PR yang tidak tersangkut konflik boleh jalan lebih dulu.

Rencana baru/berubah di-commit sebagai commit pertama (`docs(plans): ...`) di branch PR pertama.
Ambil tabel **Urutan pekerjaan** (PR · Branch · Isi · Menutup · Bergantung · E2E).

## 3. Pilih PR yang dikerjakan

- Pilihan dari argumen (`PR-2,PR-4`, `PR-2..PR-5`); tanpa pilihan → semua PR yang belum selesai.
- PR dianggap **selesai** bila branch-nya sudah punya MR merged; **sedang jalan** bila MR-nya
  open (lewati dan sebut di laporan). Cek dengan `glab mr list --source-branch <b> --all` /
  `gh pr list --head <b> --state all`.

## 4. Susun gelombang

Dari kolom *Bergantung*:

- PR yang semua dependensinya sudah merged → base `origin/<baseBranch>`.
- PR yang dependensinya ikut dikerjakan di run ini atau MR-nya masih open → base = **branch
  dependensi** (bertumpuk). MR tetap ke `mr.targetBranch`, deskripsi menyebut
  "Bergantung pada !X — merge setelahnya".
- Gelombang 1 = PR tanpa dependensi yang belum selesai; gelombang berikutnya = PR yang
  dependensinya selesai di gelombang sebelumnya. Dalam satu gelombang, jalankan paralel sampai
  batas paralelisme.

## 5. Kerjakan setiap PR

Untuk PR paralel, panggil agent-agent sejenis dalam satu pesan. Langkah per PR:

### 5.1 Siapkan branch dari base terbaru

**Path kerja** ditentukan oleh jumlah PR yang berjalan **bersamaan**:

- **Satu PR pada satu waktu** (tugas tunggal, atau beberapa PR yang dikerjakan berurutan):
  kerjakan langsung di repo utama, **tanpa worktree**. Syarat: working tree bersih
  (`git status --porcelain` kosong). Catat branch asal user, lalu:
  ```bash
  git fetch origin --prune
  git switch -c <branch> <base>
  ```
  Bila working tree **tidak** bersih, jangan sentuh perubahan user (jangan stash/reset): pakai
  worktree seperti di bawah.
- **Lebih dari satu PR bersamaan** (gelombang paralel): satu worktree per PR supaya tidak
  saling bentrok:
  ```bash
  git fetch origin --prune
  git worktree add -b <branch> <worktreeRoot>/<slug> <base>
  ```
  Pasang dependensi di worktree bila dibutuhkan untuk lint/test (perintah install dari adapter).

`<base>` = `origin/<baseBranch>`, kecuali PR ini bergantung pada PR yang belum merged: base =
branch PR dependensi itu, dan deskripsi MR menyebut "Bergantung pada !X — merge setelahnya".
Nama branch diambil dari kolom *Branch* rencana bila ada; tanpa kolom itu, ikuti pola branch
yang sudah ada di repo (`git branch -r | head -20`).

Di langkah berikutnya, `<path kerja>` = repo utama atau path worktree tersebut.

### 5.2 Implementasi → agent `pengembang`

Beri: `<path kerja>` (absolut), teks lengkap bagian rencana PR, surface yang terlibat.
Tunggu laporannya. Kalau pengembang berhenti dengan pertanyaan (teknis atau situasi
wajib-tanya dari skill platform):

1. Kumpulkan pertanyaan dari semua PR yang berhenti di gelombang ini, teruskan ke user dalam
   **satu** pesan (per PR: pertanyaan, opsi, rekomendasi pengembang). Jangan menjawab sendiri.
2. PR lain di gelombang yang sama tetap jalan sampai tinjauan; yang bergantung pada PR
   tertahan menunggu.
3. Setelah user menjawab, lanjutkan **agent pengembang yang sama** dengan SendMessage berisi
   jawaban user (konteks dan pekerjaannya tetap). Agent sudah tidak tersedia → panggil
   `pengembang` baru dengan bagian rencana + jawaban user + daftar file yang sudah diubah.

### 5.3 Tinjauan paralel

Jalankan **bersamaan** (satu pesan, beberapa pemanggilan agent), masing-masing diberi
`<path kerja>`, base branch, dan bagian rencana:

| Agent | Kapan | Fokus |
|---|---|---|
| `peninjau` | selalu | kesesuaian rencana, dokumen, aturan project |
| `reviewer-senior` | selalu | clean code, clean architecture |
| `auditor-keamanan` | diff menyentuh auth, API/HTTP, storage, konfigurasi, dependensi, WebView/deep link | celah keamanan |
| `penyelaras-desain` | diff menyentuh UI **dan** `docs.design` bukan `TIDAK ADA` | selisih dengan prototype |

Input dari orkestrator ke setiap peninjau (hemat token):
- simpan diff sekali ke file sementara (`git -C <path kerja> diff <base> > <tmp>/pr.diff`) dan
  beri **path**-nya, bukan isi diff;
- beri hanya potongan rencana untuk PR ini, plus hasil lint/typecheck/test dari laporan
  pengembang (supaya tidak dijalankan ulang);
- putaran ulang: kirim **hanya** daftar temuan sebelumnya + diff baru, minta peninjau
  memverifikasi temuan itu saja, bukan meninjau dari awal.

Gabungkan temuan yang bersifat wajib (PERLU PERBAIKAN, ADA CELAH tingkat Sedang ke atas,
selisih desain) dan kirim kembali ke `pengembang` dalam satu daftar (SendMessage ke agent yang
sama bila masih ada). Setelah diperbaiki, jalankan ulang **hanya** peninjau yang tadinya
memberi temuan. **Maksimal 2 putaran perbaikan.** Masih ada temuan wajib setelah itu →
berhenti, laporkan ke user, jangan buat MR. Temuan berlabel Saran/Rendah dicantumkan di
deskripsi MR, tidak menahan alur.

### 5.4 E2E → agent `penguji`

Jalankan bila **salah satu** benar (adapter menyebut tool E2E, bukan `TIDAK ADA`):
- rencana PR mencantumkan E2E;
- tanpa rencana, dan PR mengubah perilaku yang **terlihat pengguna** (layar, alur, interaksi);
- tindak lanjut MR yang deskripsinya masih menyebut E2E belum dikerjakan.

Lewati untuk perubahan murni internal (refactor tanpa perubahan perilaku, test, konfigurasi)
dan sebut alasannya di laporan. Perangkat/simulator tidak tersedia → laporkan apa adanya,
jangan dianggap lulus.

Beri: `<path kerja>`, fitur, sumber test case. Flow gagal karena bug produk → kembali ke
langkah 5.2 dengan temuan itu (dihitung dalam batas 2 putaran).

### 5.5 Commit, push, MR

- `git -C <path kerja> status` lalu **stage eksplisit** per path dari laporan pengembang/penguji.
  Jangan `git add -A` / `commit -a`. Pastikan tidak ada screenshot, log, atau output build.
- Pesan commit mengikuti gaya `git log --oneline -15` repo.
- Tarik base sekali lagi sebelum push; rebase kalau tertinggal, lalu jalankan ulang lint/test.

Lanjutannya bergantung pada `mr.mode` (default `"mr"`):

**`"push-base"`** (tim langsung push ke base branch, tanpa MR):
- PR dikerjakan satu per satu urut gelombang; tidak ada MR bertumpuk.
- Setelah rebase ke `origin/<baseBranch>`: di repo utama `git switch <baseBranch>`,
  `git merge --ff-only origin/<baseBranch>`, lalu `git merge --ff-only <branch>`;
  `git push origin <baseBranch>`. Bukan fast-forward → rebase ulang, jangan merge commit.
- Push ditolak/diblokir (proteksi branch, izin) → biarkan commit di `<baseBranch>` lokal,
  jangan force, dan minta user menjalankan `git push origin <baseBranch>` di laporan.
- Tugas besar (> 1 PR) atau menyentuh pekerjaan orang lain → konfirmasi ke user sekali sebelum
  push pertama.
- Lewati langkah MR di bawah; temuan Saran/Rendah masuk laporan akhir. Di 5.6 hapus branch
  lokal PR setelah push.

**`"mr"`**:
- `git push -u origin <branch>`.
- Buat MR ke `mr.targetBranch` dengan `mr.cli` (`glab mr create` / `gh pr create`). Deskripsi:
  ringkasan, requirement yang dipenuhi (ID), cara verifikasi, hasil lint/typecheck/test/E2E,
  dan yang belum dikerjakan. Ikuti format MR sebelumnya kalau repo punya pola.
- **Verifikasi MR benar-benar ada** (`glab mr view` / `gh pr view`). CLI bisa gagal diam-diam
  (mis. 403). Kalau gagal, berikan user tautan "create merge request" dari keluaran push.

### 5.6 Bersihkan

Setelah push dan MR terverifikasi (mode `push-base`: setelah push base berhasil):
- tanpa worktree: kembali ke branch asal user (`git switch <branch-asal>`), hapus branch lokal
  PR (`git branch -D <branch>`) karena sudah ada di remote;
- dengan worktree: `git worktree remove <path>`, `git worktree prune`, `git branch -D <branch>`.

Kegagalan satu PR (masih ada temuan wajib setelah 2 putaran, test gagal, konflik rebase):

- jangan buat MR untuk PR itu;
- commit lokal semua perubahannya (stage eksplisit) dengan pesan `wip(<PR>): tertahan — <alasan>`,
  **jangan push**; tanpa worktree, kembali ke branch asal user. Branch/worktree itu disebut di
  laporan untuk diperiksa user. (Working tree bersih = hook tinjau otomatis tidak terpicu ulang.)
- PR yang bergantung padanya **dilewati**; PR lain tetap jalan.

## Status di menu bar

Bila tugas berasal dari butir laporan `cek` (feedback, bug, temuan), setelah MR terverifikasi pindahkan
butir itu ke "menunggu review" supaya badge menu bar ikut berkurang (tanpa token):
`R=$(ls -d ~/.claude/plugins/cache/clint/clint/*/ | sort -V | tail -1); python3 "$R/scripts/laporan-ubah.py" review "<ID/teks butir>" "MR !<n>" "<url MR>"`
Tindak lanjut yang tidak menghasilkan MR baru (mis. perbaikan di MR yang sama) → `... selesai "<ID/teks>"`.


Saat mulai, setiap ganti PR/tahap, dan saat selesai, perbarui status (murah, satu baris):
`printf '%s\n%s\n' "PR-2/4" "PR-2 · ditinjau reviewer-senior" > ~/Library/Logs/clint/kerja.txt`
Baris 1 pendek (tampil di sebelah ikon), baris berikut rincian. Hapus file itu di akhir
(`rm -f ~/Library/Logs/clint/kerja.txt`), termasuk bila berhenti karena gagal.

## Hemat token

- Jangan membaca dokumen/rencana utuh di sesi utama; cukup tabel *Urutan pekerjaan* dan potongan
  bagian tiap PR (`grep -n` + `sed -n`). Agent yang butuh detail membacanya sendiri.
- Teruskan ke setiap agent hanya potongan yang relevan untuk PR-nya.
- Simpan laporan agent seperlunya (putusan + daftar file + temuan); jangan menyalin ulang
  laporan panjang ke pesan berikutnya.

## 6. Laporan akhir (satu pesan, singkat dan manusiawi)

Seperti rekan kerja mengabari lewat chat, maksimal ±12 baris:

- Satu kalimat hasil, mis. "Beres: 3 MR siap Anda review, 1 tertahan karena test gagal."
- Satu baris per MR: tautan + apa yang berubah dari sudut pengguna aplikasi. Mode `push-base`:
  satu baris per PR yang sudah di-push (commit pendek + perubahannya), plus saran tinjauan yang
  tidak diterapkan (pengganti deskripsi MR); push yang tertahan ditulis beserta perintahnya.
- Bila ada MR bertumpuk: "Merge berurutan: !a → !b."
- Bila ada yang tertahan atau belum bisa diverifikasi: satu baris alasannya + apa yang Anda
  perlu putuskan.
- Tanpa tabel, tanpa putusan per agent, tanpa hash/path kecuali untuk tindak lanjut.

Merge tetap oleh user.

## Kabar suara (wajib, di akhir)

Tulis **satu kalimat inti** (maks ±20 kata, bahasa lisan, tanpa simbol/kode/path) ke file kabar;
hook akan menampilkannya sebagai notifikasi dan membacakannya:

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar.txt"
```
Contoh: "Selesai. Tiga MR siap direview, satu tertahan karena test gagal."
