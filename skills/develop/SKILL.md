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
| **Mikro** | 1–2 file, ≤ ~30 baris, area biasa (teks, warna, testID, satu kondisi, konfigurasi kecil) | **Tanpa subagent.** Kerjakan langsung di sesi ini mengikuti skill platform → `run-checks.py` → commit → MR. Cocokkan sendiri dengan checklist skill |
| **Kecil** | 1 PR, ≤ ~150 baris, area biasa | `developer` + `code-reviewer` (clean code + aturan project) + auditor `wajib=` (5.3) |
| **Sedang** | 1 PR > ~150 baris, atau menyentuh area sensitif (auth, token/penyimpanan data sensitif, query/data/migrasi, kontrak API, pembayaran), dinilai dari **isi** diff, bukan hanya nama file | `developer` + `conformance-reviewer` + `code-reviewer` + auditor `wajib=` + **maksimal 2** auditor lain paling relevan (tabel 5.3) |
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
- `R` = path plugin dan `<sid>` = id sesi, dari baris *Sesi clint* di konteks sesi (cadangan
  `R=$(cat ~/.config/clint/root)`). Teruskan `R` ke agent yang butuh skrip.
- **Sesi lain di repo ini**: PR yang diklaim sesi lain terlihat di `plan-status.py` (🔄) dan tidak dikerjakan di
  sini. Apakah repo utama boleh dipakai ditentukan di langkah 5.1.
- **Satu perintah, tanpa token:** `bash "$R/scripts/preflight.sh" .` → fetch, tarik `relatedRepos` yang bersih
  (dokumen dan desain terbaru), lalu cetak `base`, `mr_mode`, `surface=...`, status tiap related repo, dan
  `paralel=` (sisa disk ≥ 20 GB → 3 PR sekaligus; 5–20 GB → 1; RAM ≤ 8 GB membatasi maks 2, ditandai `batas=ram`;
  sebut batas ini di laporan bila membatasi). Exit 1 = belum ada `.claude/clint.json` →
  tawarkan `/clint:setup`; exit 2 = disk < 5 GB → berhenti dan laporkan. `adapter_besar=` → kerja tetap jalan;
  sebut di laporan akhir dan sarankan `/clint:setup sync` untuk memindahkan isi jurnal adapter.
  `gerbang_kurang=` atau `harness=tidak ada` (`quality-gates.md` §1–2) → kerja tetap jalan, tetapi laporan akhir
  selalu menyebutnya dan *Berikutnya* memuat `/clint:setup sync` (gerbang) atau PR `chore/perf-baseline` (harness).
- Cocokkan tugas dengan `surfaces[]` (dari path/app yang disebut, atau dari rencana). Tugas
  menyentuh app yang tidak ada di `surfaces[]` (mis. backend/web saat clint baru dipasang
  untuk mobile) → berhenti, sebut surface yang tidak tercakup, dan sarankan mengerjakannya
  tanpa clint (skill/rules project untuk app itu) atau menambah surface lewat
  `/clint:setup`. Tugas campuran → kerjakan hanya bagian surface yang tercakup bila
  user setuju.

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
| Path dokumen lain (feedback QA, bug report, MoM, notulen) | jadikan **sumber tugas**: ambil butir yang masih open dan menyangkut surface ini; muat 1 PR → langsung; lebih → `planner` membuat rencana di `docs.plans` dari butir itu. Jangan mengubah isi dokumen sumber; status butir ditulis lewat `tech-writer` (lihat `klaim.md`) |

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
`bash "$R/scripts/prepare-branch.sh" <repo utama> <branch> <base> <sid> [--worktree]`
→ `path=<path kerja> mode=repo|worktree asal=<branch asal user>`.
- Tanpa `--worktree` (tugas tunggal, atau beberapa PR berurutan): skrip memeriksa `repo-busy.sh`; repo utama
  bebas → `git switch -c` di repo utama, selain itu (sesi clint/Claude lain di repo ini, working tree kotor)
  → worktree, dengan alasannya di `alasan_worktree=`.
- `--worktree` bila **lebih dari satu PR bersamaan** di run ini, supaya tidak mengganggu sesi lain atau
  perubahan user (jangan stash/reset/switch di repo utama).
- Di worktree, `node_modules` repo utama ditautkan bila lockfile sama (`node_modules=ditautkan`). Lockfile
  berbeda, atau lint/test gagal karena modul → install dengan perintah dari adapter. Selain JS ikuti adapter.

`<base>` = `origin/<baseBranch>`, kecuali PR ini bergantung pada PR yang belum merged: base =
branch PR dependensi itu, dan deskripsi MR menyebut "Bergantung pada !X, merge setelahnya".
Nama branch diambil dari kolom *Branch* rencana bila ada; tanpa kolom itu, ikuti pola branch
yang sudah ada di repo (`git branch -r | head -20`).

Di langkah berikutnya, `<path kerja>` = repo utama atau path worktree tersebut.

### 5.2 Implementasi → agent `developer` (Mikro: kerjakan langsung di sesi ini, tanpa agent)

Bug yang penyebabnya belum jelas: panggil `bug-investigator` dulu dan sertakan diagnosisnya ke `developer`.


Potongan rencana tanpa token: `python3 "$R/scripts/plan-slice.py" <rencana> PR-<n> --dir <path kerja>` →
`potongan=<path>` (bagian umum + baris tabel dan rincian PR ini saja, di folder kerja PR).
Beri: `<path kerja>` (absolut), path potongan itu (bukan teks atau file rencana utuh), surface yang terlibat, `R`.
Tunggu laporannya. Kalau `developer` berhenti dengan pertanyaan (teknis atau situasi
wajib-tanya dari skill platform):

1. Kumpulkan pertanyaan dari semua PR yang berhenti di gelombang ini, teruskan ke user dalam
   **satu** pesan (per PR: pertanyaan, opsi, rekomendasi `developer`). Jangan menjawab sendiri.
2. PR lain di gelombang yang sama tetap jalan sampai tinjauan; yang bergantung pada PR
   tertahan menunggu.
3. Setelah user menjawab, lanjutkan **agent developer yang sama** dengan SendMessage berisi
   jawaban user (konteks dan pekerjaannya tetap). Agent sudah tidak tersedia → panggil
   `developer` baru dengan path potongan rencana + jawaban user + daftar file yang sudah diubah.

### 5.3 Tinjauan sesuai ukuran

**Baca `review.md` (folder skill ini) saat sampai langkah ini.** Intinya:
- `python3 "$R/scripts/review-prep.py" <path kerja> <base> [--design]` → `pr.diff`, `ukuran=` (batas bawah, boleh
  dinaikkan), `sensitif=`, `wajib=`, dan kandidat auditor dengan buktinya.
- Kecil: `code-reviewer` + auditor `wajib=`. Sedang/Besar: + `conformance-reviewer` + maks 2 auditor relevan.
  Mikro: tanpa agent, cocokkan sendiri.
- Peninjau jalan bersamaan, diberi path (`pr.diff`, `rencana-PR-<n>.md`, `checks.md`), bukan isi. Kumpulkan dulu,
  gabungkan dengan `merge-findings.py`, kirim ke `developer` sekali. Semua tingkat termasuk Low diperbaiki;
  maks 3 putaran; Low tidak memicu putaran ulang.
- `performance-auditor` di `wajib=` → ukur sebelum/sesudah (5.3b di `review.md`); tanpa angka → MR Draft.

### 5.4 E2E → agent `e2e-tester`

Jalankan bila **salah satu** benar (adapter menyebut tool E2E, bukan `TIDAK ADA`):
- rencana PR mencantumkan E2E;
- tanpa rencana, dan PR mengubah perilaku yang **terlihat pengguna** (layar, alur, interaksi);
- tindak lanjut MR yang deskripsinya masih menyebut E2E belum dikerjakan.

Lewati untuk perubahan murni internal (refactor tanpa perubahan perilaku, test, konfigurasi)
dan sebut alasannya di laporan. Perangkat/simulator tidak tersedia → laporkan apa adanya,
jangan dianggap lulus.

Beri: `<path kerja>`, fitur, sumber test case. Flow gagal karena bug produk → kembali ke
langkah 5.2 dengan temuan itu (dihitung dalam batas 3 putaran); penyebabnya tidak jelas dari laporan
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

### 5.5 Commit, push, MR, bersihkan (satu perintah)

**Baca `ship.md` (folder skill ini) saat sampai langkah ini**: isi pesan commit (trailer `Plan:`), daftar file,
deskripsi MR, JSON saran tinjauan, argumen dan kode keluar `python3 "$R/scripts/ship-pr.py"`, mode `push-base`,
jalur kegagalan PR (commit `wip`, jangan push), dan 5.6 penutupan modul (wajib setelah PR terakhir sebuah
rencana modul jadi MR).

## Status di menu bar dan klaim PR

Klaim PR di `~/Library/Logs/clint/kerja/<sid>.json` saat PR dipilih, perbarui setiap ganti tahap, hapus di akhir
(termasuk bila gagal). Format dan `update-report.py review|selesai`: `klaim.md` (folder skill ini).

## Hemat token

- Jangan membaca dokumen/rencana utuh di sesi utama; cukup tabel *Urutan pekerjaan* dan potongan
  bagian tiap PR (`grep -n` + `sed -n`). Agent yang butuh detail membacanya sendiri.
- Teruskan ke setiap agent hanya potongan yang relevan untuk PR-nya (`plan-slice.py`), berupa path.
- Sesi utama tidak menjalankan ulang lint/typecheck/test: hasilnya di `checks.md`. Pengecualian: `--check` di
  `ship-pr.py` (hanya berjalan bila branch di-rebase).
- Sesi utama tidak membuka screenshot, log E2E, atau keluaran tool besar yang tersimpan ke file (`tool-results`):
  kegagalan E2E diserahkan ke `e2e-tester`/`bug-investigator`, file besar cukup di-`grep` untuk baris yang perlu.
- Minta setiap agent melapor ringkas (±25 baris). Simpan hanya verdict, daftar file, dan temuan yang tersisa;
  jangan menyalin ulang laporan panjang ke pesan berikutnya.
- Tidak ada `sleep`/polling untuk pipeline, build, atau pihak luar lain (lihat aturan agent). Pola yang paling
  sering muncul di audit dan penggantinya: menunggu `run-checks.py` atau skrip lokal → jalankan dengan
  `run_in_background` lalu tunggu notifikasi selesai (jangan `until pgrep`); menunggu job pipeline `glab` atau build
  `eas` → satu pengecekan lalu laporkan tertunda, atau Monitor bila user memintanya; menunggu file keluaran
  agent → agent latar belakang sudah memberi notifikasi, jangan `until [ -s file ]`.
- Pertanyaan ke user digabung jadi satu `AskUserQuestion` per gelombang (atau satu di akhir bila bisa memakai
  default yang wajar); jangan bertanya per PR saat jawabannya tidak memblokir PR lain.

## 6. Laporan akhir (satu pesan, singkat dan manusiawi)

Seperti rekan kerja mengabari lewat chat, maksimal ±12 baris (di luar blok *Berikutnya*):

- Satu kalimat hasil, mis. "Beres: 3 MR siap Anda review, 1 tertahan karena test gagal."
- Satu baris per MR: tautan + apa yang berubah dari sudut pengguna aplikasi. Mode `push-base`:
  satu baris per PR yang sudah di-push (commit pendek + perubahannya), plus saran tinjauan yang
  tidak diterapkan (pengganti deskripsi MR); push yang tertahan ditulis beserta perintahnya.
- Bila ada MR bertumpuk: "Merge berurutan: !a → !b."
- Bila ada yang tertahan atau belum bisa diverifikasi: satu baris alasannya + apa yang Anda
  perlu putuskan.
- Performa: angka sebelum/sesudah, atau `belum terukur` beserta alasannya. Gerbang mesin atau harness yang belum
  terpasang (`gerbang_kurang=`, `harness=`) disebut setiap kali.
- Tanpa tabel, tanpa putusan per agent, tanpa hash/path kecuali untuk tindak lanjut.

Merge tetap oleh user.

### Berikutnya (wajib, blok terakhir)

Aturannya di `berikutnya.md` (folder skill ini), dipakai semua skill clint. Susun dari keluaran skrip
(`plan-status.py`, `update-report.py periksa-mr` lalu `langkah`), tidak pernah dari ingatan; maks 5 langkah.

## Kabar suara (wajib, di akhir)

Tulis **satu kalimat inti** (maks ±20 kata, bahasa lisan, tanpa simbol/kode/path) dengan tool Write ke path
`kabar` di baris *Sesi clint*; hook akan menampilkannya sebagai notifikasi dan membacakannya.
Contoh: "Selesai. Tiga MR siap direview, satu tertahan karena test gagal."
