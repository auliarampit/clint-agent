---
name: develop
description: Mengerjakan kode sampai jadi MR — dari perbaikan kecil sampai modul penuh. Menentukan sendiri perlu rencana atau tidak, membuat/memperbarui rencana bila perlu, lalu mengerjakan semua PR (paralel bila tidak saling bergantung), meninjau dan memperbaiki otomatis, menguji, membuat MR, dan memberi satu laporan di akhir. Pakai untuk pekerjaan kode apa pun ("kerjakan X", "perbaiki Y", "jalankan rencana ini", "kerjakan hasil status", "perbaiki pipeline !123"). Dokumen saja → docs; build/rilis/deploy → release; E2E saja → test.
argument-hint: <deskripsi tugas | ID modul | path-rencana> [PR-x..PR-y]
---

# Develop: dari tugas sampai MR

Kamu orkestrator untuk banyak PR sekaligus. Subagent tidak bisa memanggil subagent lain, jadi
**kamu** yang memanggil setiap agent. User hanya ingin dihubungi di akhir, kecuali ada
pertanyaan teknis yang benar-benar memblokir.

## 0. Tim seperlunya (tentukan sekali, di awal)

Setiap agent yang dipanggil punya biaya awal (instruksi + konteks) dan menambah waktu. Panggil agent hanya
bila ia menambah nilai yang tidak bisa didapat murah di sesi ini. **Tugas kecil tidak dibuat kompleks.**

**Ukuran tugas** (per PR; nilai sekali dari permintaan + perkiraan diff, jangan berlebihan):

| Ukuran | Ciri | Tim |
|---|---|---|
| **Mikro** | 1–2 file, ≤ ~30 baris, area biasa (teks, warna, testID, satu kondisi, konfigurasi kecil) | **Tanpa subagent.** Kerjakan langsung di sesi ini mengikuti skill platform → lint/typecheck/test → commit → MR. Cocokkan sendiri dengan checklist skill |
| **Kecil** | 1 PR, ≤ ~150 baris, area biasa | `developer` + **satu** peninjau: `code-reviewer` (clean code + aturan project) |
| **Sedang** | 1 PR > ~150 baris, atau menyentuh area sensitif (auth, data/migrasi, kontrak API, pembayaran) | `developer` + `conformance-reviewer` + `code-reviewer` + **maksimal 2** auditor paling relevan (tabel 5.3) |
| **Besar** | modul / > 1 PR / lintas platform / arsitektur atau teknologi baru | `solution-architect` sekali (tinjau rencana) → `planner` → setiap PR ditangani sesuai ukurannya sendiri |

**Jenis tugas** (menggantikan tim di atas):

| Jenis | Yang dipanggil |
|---|---|
| Bug, penyebab **belum jelas** dari laporan | `bug-investigator` dulu → hasilnya jadi masukan `developer`. Penyebab sudah jelas → lewati |
| Pipeline merah | `pipeline-fixer` saja |
| Build / rilis / APK / update OTA / deploy | bukan tugas skill ini → ikuti skill `release` |
| Dokumentasi saja (status feedback, README, CHANGELOG, ADR) | bukan tugas skill ini → ikuti skill `docs` |
| E2E | `e2e-tester` hanya bila syarat 5.4 terpenuhi |

**Dilarang**: memanggil agent untuk sesuatu yang selesai dengan satu `grep`/satu perintah; memanggil auditor
"untuk berjaga-jaga"; menjalankan seluruh tim untuk tugas mikro; membaca dokumen panjang di sesi utama
hanya untuk diteruskan ke agent (beri path/potongan saja).

## 1. Prasyarat

- **Bahasa**: laporan ke user, kabar suara, dan file rencana memakai bahasa user (baris *Bahasa clint*
  di konteks sesi; default English). Sebut bahasa itu di setiap prompt agent. Dokumen project lain
  (feedback QA, README, CHANGELOG, ADR) memakai `docs.language` di `.claude/clint.json`.
- Baca `.claude/clint.json`. Tidak ada → berhenti, tawarkan `/clint:setup`.
- `R` = path plugin dan `<sid>` = id sesi, dari baris *Sesi clint* di konteks sesi (cadangan
  `R=$(ls -d ~/.claude/plugins/cache/clint/clint/*/ | sort -V | tail -1)`). Teruskan `R` ke agent yang butuh skrip.
- **Sesi lain di repo ini**: PR yang diklaim sesi lain terlihat di `plan-status.py` (🔄) dan tidak dikerjakan di
  sini. Apakah repo utama boleh dipakai ditentukan di langkah 5.1.
- `git fetch origin --prune`. Tarik juga `relatedRepos` (`git -C <path> pull --ff-only` bila
  bersih) supaya rencana dan implementasi memakai dokumen dan desain terbaru.
- Cocokkan tugas dengan `surfaces[]` (dari path/app yang disebut, atau dari rencana). Tugas
  menyentuh app yang tidak ada di `surfaces[]` (mis. backend/web saat clint baru dipasang
  untuk mobile) → berhenti, sebut surface yang tidak tercakup, dan sarankan mengerjakannya
  tanpa clint (skill/rules project untuk app itu) atau menambah surface lewat
  `/clint:setup`. Tugas campuran → kerjakan hanya bagian surface yang tercakup bila
  user setuju.
- `df -h ~`. Tentukan paralelisme: sisa ≥ 20 GB → maks 3 PR sekaligus; 5–20 GB → 1; < 5 GB →
  berhenti dan laporkan.

## 2. Tentukan jalur (otomatis, jangan tanya user)

| Argumen | Jalur |
|---|---|
| Deskripsi tugas yang muat dalam **1 PR** (perbaikan, penyesuaian, butir feedback, temuan `status` yang kecil) | langsung ke langkah 5 sebagai satu PR, **tanpa file rencana** |
| Tindak lanjut MR yang sudah ada ("terapkan saran reviewer di !123", komentar review) | kerjakan di **branch MR itu** (`git fetch` lalu `git switch <source_branch>`, tanpa branch/MR baru): langkah 5.2–5.5, push ke branch yang sama, MR tidak dibuat ulang. Butir yang bertentangan dengan aturan project atau memang disengaja → lewati dan sebut alasannya di laporan |
| Build/rilis/APK/update OTA/deploy ("build APK untuk UAT", "rilis ke kanal preview") | ikuti skill `release`; selesai |
| Tugas dokumentasi saja ("perbarui status feedback #8 di docs", README, CHANGELOG, ADR) | ikuti skill `docs`; selesai |
| E2E saja untuk MR/fitur yang sudah ada ("e2e !123") | ikuti skill `test`; selesai |
| "perbaiki pipeline !123", pipeline merah | panggil agent `pipeline-fixer` untuk MR itu, laporkan hasilnya; selesai |
| Kosong, setelah `status` di percakapan ini | pakai temuan "perlu dikerjakan" dari laporan itu sebagai argumen |
| ID/nama modul, atau tugas yang butuh > 1 PR | cari rencana di `docs.plans` (`grep -il <ID>`) |
| Path file rencana (di `docs.plans`, punya tabel *Urutan pekerjaan*) | pakai rencana itu |
| Path dokumen lain (feedback QA, bug report, MoM, notulen) | jadikan **sumber tugas**: ambil butir yang masih open dan menyangkut surface ini; muat 1 PR → langsung; lebih → `planner` membuat rencana di `docs.plans` dari butir itu. Jangan mengubah dokumen sumber |

Untuk tugas **Besar**, panggil `solution-architect` sekali untuk meninjau rencana (baru atau yang sudah ada)
sebelum PR pertama; putusan `PERLU DIUBAH` → teruskan daftar perubahan rencana dari SA apa adanya ke `planner`
sebagai masukan, baru lanjut.

Untuk jalur rencana, panggil agent `planner` bila:
- rencana belum ada → buat baru; atau
- dokumen/desain terkait berubah sejak rencana terakhir diubah
  (`git -C <relatedRepo> log --since=<tanggal commit terakhir rencana>` tidak kosong) → perbarui
  bagian PR yang belum selesai.

Bila `planner` melaporkan butir **PERLU KEPUTUSAN USER** (konflik dokumen): tanyakan ke
user sekaligus dalam satu pesan (butir + rekomendasi), tulis jawabannya ke tabel
ketidakjelasan rencana, baru lanjut. PR yang tidak tersangkut konflik boleh jalan lebih dulu.

Rencana baru/berubah di-commit sebagai commit pertama (`docs(plans): ...`) di branch PR pertama.
Ambil tabel **Urutan pekerjaan** (PR · Branch · Isi · Menutup · Bergantung · E2E).

## 3. Pilih PR yang dikerjakan

Status setiap PR diambil dari satu skrip (tanpa token):
`python3 "$R/scripts/plan-status.py" <rencana> --session <sid>` (`--json` untuk dibaca mesin). Skrip memakai MR
(merged/open/Draft), trailer `Plan:` di base, branch yang tertinggal, klaim sesi lain, dan bagian `## Status PR`.

- Pilihan dari argumen (`PR-2,PR-4`, `PR-2..PR-5`); tanpa pilihan → PR `⏸️ tertahan` milik run ini dulu, lalu
  PR `⬜` yang siap (dependensi selesai, atau MR dependensinya open untuk ditumpuk).
- PR yang `🔄 dikerjakan sesi lain` dilewati, termasuk bila disebut di argumen: sebut sesi dan tahapnya di
  laporan. PR `✅`, `🔍`, `🧪` tidak dikerjakan ulang (tindak lanjut MR → jalur MR di langkah 2, E2E → `test`).
- `❔ belum tercatat` (push-base tanpa bukti) → jangan menebak; tanya user PR mana yang sudah selesai, atau
  sarankan `/clint:docs perbarui Status PR di <rencana> dari git log` dulu.
- **Maksimal 3 PR per run** (paralel maupun berurutan), supaya konteks sesi tidak membengkak. PR lain
  masuk *Berikutnya*.
- Segera setelah PR dipilih, **klaim** dengan menulis file status sesi (lihat *Status di menu bar*): `dir`,
  `rencana`, dan `prs` wajib terisi, supaya sesi lain yang memilih PR sesudahnya tidak mengambil PR yang sama.

## 4. Susun gelombang

Dari kolom *Bergantung*:

- PR yang semua dependensinya sudah merged → base `origin/<baseBranch>`.
- PR yang dependensinya ikut dikerjakan di run ini atau MR-nya masih open → base = **branch
  dependensi** (bertumpuk). MR tetap ke `mr.targetBranch`, deskripsi menyebut
  "Bergantung pada !X, merge setelahnya".
- Gelombang 1 = PR tanpa dependensi yang belum selesai; gelombang berikutnya = PR yang
  dependensinya selesai di gelombang sebelumnya. Dalam satu gelombang, jalankan paralel sampai
  batas paralelisme.

## 5. Kerjakan setiap PR

Untuk PR paralel, panggil agent-agent sejenis dalam satu pesan. Langkah per PR:

### 5.1 Siapkan branch dari base terbaru

**Path kerja: repo utama bila bebas, worktree bila sedang dipakai.** Satu perintah, tanpa token:
`bash "$R/scripts/repo-busy.sh" . <sid>` → `bebas` atau `dipakai: <alasan>` (sesi clint lain bekerja di repo
utama, sesi Claude lain sedang aktif di folder repo ini, atau working tree kotor). Cek sekali saat run mulai,
dan sekali lagi tepat sebelum `git switch` bila PR berikutnya dikerjakan berurutan.

- **Bebas, satu PR pada satu waktu** (tugas tunggal, atau beberapa PR berurutan): kerjakan langsung di repo
  utama, **tanpa worktree**. Catat branch asal user, lalu:
  ```bash
  git fetch origin --prune
  git switch -c <branch> <base>
  ```
- **Dipakai**, atau **lebih dari satu PR bersamaan** di run ini: satu worktree per PR, supaya tidak mengganggu
  sesi lain atau perubahan user (jangan stash/reset/switch di repo utama):
  ```bash
  git fetch origin --prune
  git worktree add -b <branch> <worktreeRoot>/<slug> <base>
  ```
  Dependensi untuk lint/test di worktree, cara tercepat dulu: lockfile sama dengan repo utama
  (`cmp -s <repo>/<lockfile> <worktree>/<lockfile>`) → tautkan `ln -s <repo>/node_modules <worktree>/node_modules`
  (juga untuk `node_modules` per app di monorepo); berbeda, atau lint/test gagal karena modul → install dengan
  perintah dari adapter. Selain JS ikuti adapter.

`<base>` = `origin/<baseBranch>`, kecuali PR ini bergantung pada PR yang belum merged: base =
branch PR dependensi itu, dan deskripsi MR menyebut "Bergantung pada !X, merge setelahnya".
Nama branch diambil dari kolom *Branch* rencana bila ada; tanpa kolom itu, ikuti pola branch
yang sudah ada di repo (`git branch -r | head -20`).

Di langkah berikutnya, `<path kerja>` = repo utama atau path worktree tersebut.

### 5.2 Implementasi → agent `developer` (Mikro: kerjakan langsung di sesi ini, tanpa agent)

Bug yang penyebabnya belum jelas: panggil `bug-investigator` dulu dan sertakan diagnosisnya ke `developer`.


Beri: `<path kerja>` (absolut), teks lengkap bagian rencana PR, surface yang terlibat.
Tunggu laporannya. Kalau `developer` berhenti dengan pertanyaan (teknis atau situasi
wajib-tanya dari skill platform):

1. Kumpulkan pertanyaan dari semua PR yang berhenti di gelombang ini, teruskan ke user dalam
   **satu** pesan (per PR: pertanyaan, opsi, rekomendasi `developer`). Jangan menjawab sendiri.
2. PR lain di gelombang yang sama tetap jalan sampai tinjauan; yang bergantung pada PR
   tertahan menunggu.
3. Setelah user menjawab, lanjutkan **agent developer yang sama** dengan SendMessage berisi
   jawaban user (konteks dan pekerjaannya tetap). Agent sudah tidak tersedia → panggil
   `developer` baru dengan bagian rencana + jawaban user + daftar file yang sudah diubah.

### 5.3 Tinjauan sesuai ukuran

- **Mikro**: tanpa agent conformance-reviewer.
- **Kecil**: hanya `code-reviewer`.
- **Sedang/Besar**: `conformance-reviewer` + `code-reviewer` + **maksimal 2** auditor dari tabel di bawah yang paling
  relevan dengan diff (urutkan: keamanan/database/kontrak untuk data dan API, aksesibilitas/desain/performa
  untuk UI). Auditor lain dilewati walaupun pemicunya tersentuh sedikit.

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
- `pr.diff`: `git -C <path kerja> diff <base> > <folder>/pr.diff`; peninjau diberi **path**-nya, bukan isi diff;
- beri hanya potongan rencana untuk PR ini, plus hasil lint/typecheck/test dari laporan
  `developer` (supaya tidak dijalankan ulang);
- `findings.md`: gabungan temuan semua peninjau.

Setiap peninjau menutup laporan dengan blok seragam `PUTUSAN: LULUS | PERLU PERBAIKAN` + `TEMUAN:` berlabel
`[wajib]`/`[saran]` (`path:baris · kategori · masalah`, `sekarang`, `usulan`, `(luar cakupan)` bila perlu).
Gabungkan ke `findings.md`: buang temuan ganda (lokasi + masalah sama → satu butir, sebut kedua peninjau), lalu
kirim ke `developer` dalam satu pesan: path `findings.md`, semua `[wajib]`, dan `[saran]` di kode yang diubah PR
(kecuali luar cakupan). SendMessage ke agent yang sama bila masih ada. Butir saran yang bertentangan dengan
aturan project → lewati dan sebut alasannya. `developer` menandai setiap butir diperbaiki/dilewati di laporannya.
Putaran ulang: perbarui `pr.diff`, lalu jalankan **hanya** peninjau yang tadinya memberi `[wajib]`, dengan path
`findings.md` + `pr.diff`; mereka memverifikasi temuannya saja, bukan meninjau dari awal.
**Maksimal 2 putaran perbaikan.** Masih ada temuan wajib setelah itu →
berhenti, laporkan ke user, jangan buat MR. Saran tidak pernah menahan alur: saran yang masih
tersisa setelah batas putaran, dan saran luar cakupan, dicantumkan di deskripsi MR.

Hasil perbaikan saran di-commit **terpisah** dari commit utama (mis. `refactor: terapkan saran
tinjauan`, ikuti gaya commit repo) supaya mudah diperiksa di tab Commits MR dan bisa di-revert
sendiri. Bila perbaikan wajib dan saran menyentuh baris yang sama, satukan di commit utama.

### 5.4 E2E → agent `e2e-tester`

Jalankan bila **salah satu** benar (adapter menyebut tool E2E, bukan `TIDAK ADA`):
- rencana PR mencantumkan E2E;
- tanpa rencana, dan PR mengubah perilaku yang **terlihat pengguna** (layar, alur, interaksi);
- tindak lanjut MR yang deskripsinya masih menyebut E2E belum dikerjakan.

Lewati untuk perubahan murni internal (refactor tanpa perubahan perilaku, test, konfigurasi)
dan sebut alasannya di laporan. Perangkat/simulator tidak tersedia → laporkan apa adanya,
jangan dianggap lulus.

Beri: `<path kerja>`, fitur, sumber test case. Flow gagal karena bug produk → kembali ke
langkah 5.2 dengan temuan itu (dihitung dalam batas 2 putaran); penyebabnya tidak jelas dari laporan
`e2e-tester` → `bug-investigator` dulu, diagnosisnya ikut ke `developer`. Adapter mengisi **Pratinjau
E2E** → `e2e-tester` menguji lewat EAS Update ke channel khusus simulator, bukan build lokal; satu
channel E2E dipakai satu PR pada satu waktu, jadi E2E antar-PR dijalankan berurutan.

**Status E2E wajib tertulis** untuk setiap PR: `lulus`, `tidak perlu: <alasan>`, atau
`tertunda: <alasan + langkah>`. Tidak boleh kosong. **Gerbang siap-dev:** status `tertunda`
berarti PR belum siap masuk base branch:
- mode `"mr"` → MR dibuat sebagai **Draft** (`glab mr create --draft` / `gh pr create --draft`),
  deskripsi memuat `E2E: tertunda, <alasan>` dan langkahnya;
- mode `"push-base"` → jangan push ke base branch; push ke branch PR itu saja dan laporkan.
Lanjutannya `/clint:test e2e !<n>` (skill `test`).

### 5.5 Commit, push, MR

- `git -C <path kerja> status` lalu **stage eksplisit** per path dari laporan `developer`/`e2e-tester`.
  Jangan `git add -A` / `commit -a`. Pastikan tidak ada screenshot, log, atau output build.
- Pesan commit mengikuti gaya `git log --oneline -15` repo. PR dari rencana: commit utama diberi trailer
  `Plan: <nama-file-rencana-tanpa-.md> PR-<n>` (baris terakhir pesan), supaya status selesai terdeteksi di
  mode `push-base`.
- **Status di rencana** (PR dari rencana): sebelum commit utama, tulis status PR ini ke bagian `## Status PR`
  dan stage file rencananya bersama commit itu:
  `python3 "$R/scripts/plan-status.py" <rencana> --repo <path kerja> --set PR-<n>=<review|draft|done> --write`
  (`review` untuk MR biasa, `draft` bila E2E tertunda, `done` untuk `push-base`). Skrip sekaligus memperbarui butir
  PR lain yang faktanya berubah (mis. MR-nya sudah merged). Butir dipisah baris kosong, jadi PR paralel yang
  masing-masing mengubah butirnya sendiri tidak bentrok saat merge.
- Tarik base sekali lagi sebelum push; rebase kalau tertinggal, lalu ulangi **cek cepat** saja (lint,
  typecheck, test terkait). Setelah push, jangan menunggu pipeline; hasilnya muncul di `/clint:status`.

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
- Lewati langkah MR di bawah; saran yang tidak diterapkan masuk laporan akhir. Di 5.6 hapus branch
  lokal PR setelah push.

**`"mr"`**:
- `git push -u origin <branch>`.
- Buat MR ke `mr.targetBranch` dengan `mr.cli` (`glab mr create` / `gh pr create`). Deskripsi:
  ringkasan, requirement yang dipenuhi (ID), cara verifikasi, hasil lint/typecheck/test/E2E,
  dan yang belum dikerjakan. Ikuti format MR sebelumnya kalau repo punya pola. Tanpa AI slop
  (`no-ai-slop.md`): tanpa nama agent, jumlah putaran tinjauan, atau kalimat pujian.
- **Saran tinjauan yang tidak diterapkan** (luar cakupan, atau tersisa setelah batas putaran) dicatat
  supaya user bisa memvalidasinya: tulis ke file sementara sebagai JSON
  `[{"path","line","sekarang","usulan","alasan","agent"}]`, lalu setelah MR dibuat jalankan dari repo:
  `python3 "$R/scripts/mr-suggestions.py" <nomor MR> <file.json> --deskripsi`
  Hasilnya blok "Saran tinjauan" (tautan file#baris + diff) yang ditempel ke deskripsi MR
  (`glab mr update <n> --description` / `gh pr edit`). Tanpa komentar *suggestion*: Apply di MR membuat
  commit per saran, saling bentrok, dan tidak melewati lint/test. Menerapkannya nanti:
  `/clint:develop terapkan saran di !<n>`. Mode `push-base` (tanpa MR): cetak blok itu di laporan akhir.
- **Verifikasi MR benar-benar ada** (`glab mr view` / `gh pr view`). CLI bisa gagal diam-diam
  (mis. 403). Kalau gagal, berikan user tautan "create merge request" dari keluaran push.
- **Wajib, tanpa token:** bila PR berasal dari butir laporan `status`, pindahkan butir itu ke "menunggu
  review" supaya menu bar ikut diperbarui:
  `python3 "$R/scripts/update-report.py" review "<ID/teks butir>" "MR !<n>" "<url MR>" --proyek <nama project>`

### 5.6 Bersihkan

Setelah push dan MR terverifikasi (mode `push-base`: setelah push base berhasil):
- tanpa worktree: kembali ke branch asal user (`git switch <branch-asal>`), hapus branch lokal
  PR (`git branch -D <branch>`) karena sudah ada di remote;
- dengan worktree: `git worktree remove <path>`, `git worktree prune`, `git branch -D <branch>`.

Kegagalan satu PR (masih ada temuan wajib setelah 2 putaran, test gagal, konflik rebase):

- jangan buat MR untuk PR itu;
- commit lokal semua perubahannya (stage eksplisit) dengan pesan `wip(<PR>): tertahan, <alasan>`,
  **jangan push**; PR dari rencana: tulis dulu `--set PR-<n>=held:<alasan>` ke rencana (langkah 5.5) dan
  ikutkan di commit itu. Tanpa worktree, kembali ke branch asal user. Branch/worktree itu disebut di
  laporan untuk diperiksa user. (Working tree bersih = hook tinjau otomatis tidak terpicu ulang.)
- PR yang bergantung padanya **dilewati**; PR lain tetap jalan.

## Status di menu bar dan klaim PR

File status **per sesi** `~/Library/Logs/clint/kerja/<sid>.json`. Tulis saat PR dipilih (klaim), setiap ganti
PR/tahap, dan hapus di akhir, termasuk bila berhenti karena gagal (murah, satu perintah):
```bash
mkdir -p ~/Library/Logs/clint/kerja && printf '%s' '{"dir":"<repo utama absolut>","rencana":"docs/plans/mob-10.md","prs":["PR-2","PR-3"],"path":"<path kerja>","judul":"develop MOB-10","mulai":"11.21","pr":2,"total":3,"label":"PR-2/3","tahap":"ditinjau code-reviewer","catatan":"PR-1 → MR !127 · PR-3 menunggu"}' > ~/Library/Logs/clint/kerja/<sid>.json
```
`dir` = repo utama (bukan worktree): `dirname "$(git rev-parse --path-format=absolute --git-common-dir)"`.
`rencana` = path relatif rencana, `null` bila tanpa rencana. `prs` = PR yang **masih** dipegang sesi ini; PR yang
sudah jadi MR dikeluarkan dari `prs` supaya sesi lain bisa melanjutkan PR sesudahnya. `label` pendek (tampil di
sebelah ikon); tugas tunggal `"pr":1,"total":1`. Akhir run: `rm -f ~/Library/Logs/clint/kerja/<sid>.json`.

Bila tugas berasal dari butir laporan `status` (feedback, bug, temuan), setelah MR terverifikasi pindahkan
butir itu ke "menunggu review" supaya badge menu bar ikut berkurang (tanpa token):
`python3 "$R/scripts/update-report.py" review "<ID/teks butir>" "MR !<n>" "<url MR>" --proyek <nama project>`
Tindak lanjut yang tidak menghasilkan MR baru (mis. perbaikan di MR yang sama) → `... selesai "<ID/teks>"`.


## Hemat token

- Jangan membaca dokumen/rencana utuh di sesi utama; cukup tabel *Urutan pekerjaan* dan potongan
  bagian tiap PR (`grep -n` + `sed -n`). Agent yang butuh detail membacanya sendiri.
- Teruskan ke setiap agent hanya potongan yang relevan untuk PR-nya.
- Minta setiap agent melapor ringkas (±25 baris). Simpan hanya putusan, daftar file, dan temuan wajib;
  jangan menyalin ulang laporan panjang ke pesan berikutnya.
- Tidak ada `sleep`/polling untuk pipeline, build, atau pihak luar lain (lihat aturan agent).

## 6. Laporan akhir (satu pesan, singkat dan manusiawi)

Seperti rekan kerja mengabari lewat chat, maksimal ±12 baris (di luar blok *Berikutnya*):

- Satu kalimat hasil, mis. "Beres: 3 MR siap Anda review, 1 tertahan karena test gagal."
- Satu baris per MR: tautan + apa yang berubah dari sudut pengguna aplikasi. Mode `push-base`:
  satu baris per PR yang sudah di-push (commit pendek + perubahannya), plus saran tinjauan yang
  tidak diterapkan (pengganti deskripsi MR); push yang tertahan ditulis beserta perintahnya.
- Bila ada MR bertumpuk: "Merge berurutan: !a → !b."
- Bila ada yang tertahan atau belum bisa diverifikasi: satu baris alasannya + apa yang Anda
  perlu putuskan.
- Tanpa tabel, tanpa putusan per agent, tanpa hash/path kecuali untuk tindak lanjut.

Merge tetap oleh user.

### Berikutnya (wajib, blok terakhir; aturan ini dipakai semua skill clint)

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
3. Lalu butir *Perlu dikerjakan* milik project ini saja di laporan `status` (`~/Library/Logs/clint/terakhir.json`,
   ambil hanya butir yang `proyek`-nya project ini; cocokkan `dir` di `proyek[]`). Butir project lain **tidak
   pernah** masuk *Berikutnya*.
4. Tidak ada langkah → "Menunggu review: !n" bila ada, selain itu **"Selesai semua pekerjaan."**

Run mengerjakan 3 PR atau lebih, atau masih ada PR tersisa dari batas per run → judul blok menyebut
"sesi baru: ketik /clear dulu". Maksimal 5 langkah.

## Kabar suara (wajib, di akhir)

Tulis **satu kalimat inti** (maks ±20 kata, bahasa lisan, tanpa simbol/kode/path) ke file kabar sesi ini;
hook akan menampilkannya sebagai notifikasi dan membacakannya:

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar-<sid>.txt"
```
Contoh: "Selesai. Tiga MR siap direview, satu tertahan karena test gagal."
