# clint

![clint — tim agent Claude Code yang mengerjakan tiket sampai jadi MR](docs/images/cover.png)

**clint** adalah plugin Claude Code untuk tim Badr Interactive. Isinya 18 agent senior yang bekerja sebagai
satu tim: membaca dokumen, merencanakan, menulis kode, meninjau berlapis, menguji, merilis, dan menjaga
dokumen tetap sinkron. Dipasang sekali, berlaku di semua project, baik project baru maupun project lama
yang sedang di-enhance.

- **Tujuh perintah, satu per jenis kerja.** Tidak perlu menghafal agent; perintah yang memilih agent.
- **Tinjauan berlapis sebelum MR.** Kesesuaian dokumen, clean code, standar SonarQube, keamanan OWASP,
  aksesibilitas WCAG 2.2, performa, database, kontrak API, dan desain. Temuan wajib diperbaiki otomatis.
- **Lolos SonarQube sejak ditulis.** Standar quality gate Badr ikut diterapkan saat kode ditulis dan ditinjau.
- **Mobile, web, dan backend.** Skill platform yang portabel: konvensi inti + adapter fakta stack per project.
- **Dua bahasa.** Jawaban dan laporan dalam Bahasa Indonesia atau English, sesuai setelan masing-masing orang.
- **Hemat token.** Agent hanya dipanggil bila menambah nilai; menu bar, suara, dan status tidak memakai token.

---

## Daftar isi

1. [Mulai cepat](#mulai-cepat)
2. [Tujuh perintah](#tujuh-perintah)
3. [Bingung pakai yang mana?](#bingung-pakai-yang-mana)
4. [Panduan per peran](#panduan-per-peran)
5. [Bahasa](#bahasa)
6. [Standar SonarQube](#standar-sonarqube)
7. [Cara kerja `develop`](#cara-kerja-develop)
8. [Tim agent](#tim-agent)
9. [Platform: mobile, web, backend](#platform-mobile-web-backend)
10. [Laporan pagi](#laporan-pagi)
11. [Menu bar](#menu-bar)
12. [Mode JARVIS](#mode-jarvis)
13. [Otomatis tanpa perintah](#otomatis-tanpa-perintah)
14. [Hemat token](#hemat-token)
15. [Konfigurasi](#konfigurasi)
16. [Pindah dari clint v1](#pindah-dari-clint-v1)
17. [Tanya jawab](#tanya-jawab)
18. [Struktur repo dan perawatan](#struktur-repo-dan-perawatan)
19. [Peta jalan](#peta-jalan)

---

## Mulai cepat

**1. Pasang plugin** (sekali per laptop):

```bash
claude plugin marketplace add auliarampit/clint-agent
claude plugin install clint@clint
```

Lalu di VS Code: `Cmd+Shift+P` → **Developer: Reload Window**.

**2. Siapkan project** (sekali per project, oleh satu orang; hasilnya di-commit untuk seluruh tim):

```
/clint:setup mobile        # atau: web, backend, atau gabungan "mobile web backend"
```

Perintah ini:

- menyalin prinsip kerja, skill platform, aturan test, dan standar SonarQube ke `.claude/`;
- mengisi adapter stack dari hasil perintah verifikasi (bukan tebakan);
- membuat `.claude/clint.json` (base branch, cara MR, perintah lint/test, lokasi dokumen, bahasa dokumen);
- menanyakan bahasa pribadi Anda bila belum pernah diatur.

Tidak ada yang di-commit otomatis; periksa dulu hasilnya.

**3. Mulai bekerja:**

```
/clint:status                                   # ada apa hari ini?
/clint:develop perbaiki tombol simpan di profil  # kerjakan sampai jadi MR
```

## Tujuh perintah

| Perintah | Untuk | Contoh |
|---|---|---|
| `/clint:status` | Kondisi kerja: update docs/design dan dampaknya ke kode, feedback QA yang masih open, MR, pipeline, branch, disk | `/clint:status`, `/clint:status all` |
| `/clint:develop` | Mengerjakan **kode** apa pun sampai jadi MR, dari perbaikan kecil sampai modul penuh | `/clint:develop MOB-10` |
| `/clint:review` | Meninjau kode. Milik sendiri: ditinjau lalu diperbaiki. MR rekan: hanya temuan, tanpa mengubah kode | `/clint:review !123` |
| `/clint:test` | Menguji tanpa mengubah kode produk: menulis dan menjalankan E2E, menyelesaikan E2E yang tertunda | `/clint:test e2e !123` |
| `/clint:docs` | Pekerjaan **dokumen** tanpa kode: status feedback/bug, README, CHANGELOG, ADR | `/clint:docs tandai FB-MOB-008 diperbaiki di !130` |
| `/clint:release` | Build dan rilis: APK/IPA untuk UAT, update OTA, versi, changelog, kesiapan deploy | `/clint:release build APK UAT Android` |
| `/clint:setup` | Pasang clint di project, sinkronkan dengan master (`sync`), atau ganti bahasa (`language id`) | `/clint:setup sync` |

Setiap perintah ditutup dengan baris **Berikutnya**: satu perintah siap ketik untuk pekerjaan berikutnya,
atau "Selesai semua pekerjaan." Baris yang sama muncul di layar laporan dan menu bar, dengan tombol salin.

Anda **tidak perlu memanggil agent** dan tidak wajib mengetik perintah. Kalimat biasa seperti "tolong
perbaiki pipeline MR 123" atau "ada update apa hari ini?" juga dikenali dan diarahkan ke perintah yang tepat.

## Bingung pakai yang mana?

Tanyakan pada diri sendiri: **apa yang akan berubah?**

```
Belum tahu mau mengerjakan apa?          → /clint:status
Kode aplikasi berubah?                   → /clint:develop
Ingin memeriksa kode (sendiri/rekan)?    → /clint:review
Ingin menguji tanpa mengubah kode?       → /clint:test
Hanya dokumen yang berubah?              → /clint:docs
Ingin build, rilis, atau deploy?         → /clint:release
Memasang/memperbarui clint atau bahasa?  → /clint:setup
```

Beberapa contoh yang sering tertukar:

| Permintaan | Perintah | Alasan |
|---|---|---|
| "Perbaiki bug FB-MOB-008" | `develop` | kode berubah |
| "Tandai FB-MOB-008 sudah diperbaiki" | `docs` | hanya dokumen QA berubah |
| "E2E MR !123 masih tertunda" | `test` | menguji, kode produk tidak berubah |
| "Pipeline !123 merah" | `develop` | perbaikannya mengubah kode/konfigurasi |
| "Build APK untuk UAT" | `release` | build dan distribusi, bukan kode |
| "Cek dulu sebelum MR" | `review` | memeriksa hasil kerja |
| "Ada update docs?" | `status` | mencari pekerjaan |

`status` **mencari** pekerjaan, `review` **memeriksa** hasil pekerjaan, `develop` **mengerjakan**.

## Panduan per peran

clint tidak menanyakan peran Anda dan tidak membatasi apa pun: semua orang boleh memakai semua
perintah. Pilih perintah sesuai **jenis kerjanya**. Tabel ini hanya titik awal.

### Developer (fullstack, mobile, web, backend)

```
pagi     /clint:status                                  → apa yang berubah dan perlu dikerjakan
kerja    /clint:develop MOB-10                           → rencana, kode, tinjauan, E2E, MR
         /clint:develop perbaiki FB-MOB-008               → satu bug, langsung 1 MR
         /clint:develop terapkan saran reviewer di !123   → tindak lanjut MR, push ke MR yang sama
         /clint:develop perbaiki pipeline !123            → CI merah, termasuk quality gate SonarQube
rekan    /clint:review !124                               → temuan untuk MR rekan, tanpa mengubah kode
rilis    /clint:release build APK UAT Android
```

### QA

```
/clint:status                          → MR yang siap diuji, feedback yang masih open
/clint:test login                      → tulis dan jalankan E2E fitur login, hasilnya jadi MR
/clint:test e2e !123                   → selesaikan E2E yang tertunda di MR !123
/clint:docs tandai FB-MOB-008 diverifikasi tanggal 20 Okt
/clint:review !123                     → baca temuan teknis sebelum menguji
```

Bug yang ditemukan dilaporkan; perbaikannya lewat `/clint:develop` oleh developer.

### PM dan SA

```
/clint:status                                 → apa yang berubah di docs, design, dan kode; butir milik Anda
/clint:docs catat ADR: pembayaran memakai Midtrans Snap
/clint:docs perbarui CHANGELOG untuk rilis 1.4.0
/clint:review !123                            → apakah implementasi sesuai PRD/API contract
```

Penulisan dokumen requirement (BRD, PRD, SAD, API contract, STD) dan pelacakan sprint sedang dikembangkan.
Lihat [Peta jalan](#peta-jalan).

### Designer

```
/clint:status                                 → layar yang berubah di prototype dan dampaknya ke kode
/clint:review !123                            → selisih tampilan dengan prototype (design-auditor)
```

## Bahasa

Ada dua setelan yang terpisah:

| Setelan | Disimpan di | Mengatur | Default |
|---|---|---|---|
| **Bahasa pribadi** | `~/.config/clint/user.json` (laptop masing-masing) | tanya jawab, laporan, kabar suara, **file rencana** | English |
| **Bahasa dokumen project** | `.claude/clint.json` → `docs.language` (repo, sama untuk satu tim) | dokumen project baru: feedback QA, README, CHANGELOG, ADR, dokumen requirement | English |

Ganti bahasa pribadi kapan saja:

```
/clint:setup language id      # Bahasa Indonesia
/clint:setup language en      # English
```

Berlaku penuh mulai sesi berikutnya. Untuk satu percakapan, cukup bilang "pakai bahasa Indonesia".

Kenapa dipisah? Supaya dokumen klien dalam satu project tetap satu bahasa walaupun anggota tim memakai
bahasa berbeda. Sebaliknya, rencana kerja (`docs/plans`) adalah alat kerja pribadi, jadi mengikuti bahasa
orang yang membuatnya.

Isi file instruksi clint (skill, agent, rules) ditulis dalam Bahasa Indonesia. Nama perintah, agent, dan
file memakai bahasa Inggris.

## Standar SonarQube

Semua project Badr dianalisis SonarQube, dan quality gate memblokir merge. clint menerapkan standarnya
**sejak kode ditulis**, bukan setelah pipeline gagal.

Quality gate yang dipakai (default *Sonar way*, kecuali project punya gate sendiri):

| Syarat (kode baru) | Ambang |
|---|---|
| Bug dan vulnerability baru | 0 |
| Security hotspot | 100% ditinjau |
| Maintainability (code smell) | rating A |
| Coverage | ≥ 80% |
| Duplikasi | ≤ 3% |

Cara clint menegakkannya:

1. `/clint:setup` menyalin `kit/sonarqube.md` ke `.claude/rules/sonarqube.md` bila project memakai
   SonarQube. Isinya ambang di atas, cognitive complexity ≤ 15, dan daftar rule yang paling sering gagal di
   project Badr (mis. props React `Readonly<>`, tanpa `any`, tanpa ternary bertingkat, `replaceAll`,
   `globalThis`), lengkap dengan contoh salah dan benar.
2. `developer` mengikuti aturan itu saat menulis kode, menulis test untuk logika baru, dan melaporkan angka
   coverage file yang diubah (tidak pernah mengklaim "≥ 80%" tanpa angka).
3. `code-reviewer` menjadikan pelanggaran yang akan menggagalkan gate sebagai temuan **Wajib**.
4. Gate tetap gagal di CI → `/clint:develop perbaiki pipeline !123`; `pipeline-fixer` membaca issue Sonar-nya
   dan memperbaiki kode.

`// NOSONAR`, menonaktifkan rule, atau menambah exclusion untuk meloloskan gate **dilarang** tanpa
persetujuan Anda.

## Cara kerja `develop`

**Tim seperlunya.** Di awal, `develop` menilai ukuran dan jenis tugas sekali, lalu hanya memanggil agent
yang menambah nilai. Tugas kecil tidak dibuat kompleks:

| Ukuran | Ciri | Tim |
|---|---|---|
| Mikro | 1–2 file, ≤ ~30 baris, area biasa | tanpa subagent; dikerjakan langsung, lalu lint/test dan MR |
| Kecil | 1 PR, ≤ ~150 baris | `developer` + `code-reviewer` |
| Sedang | PR besar atau area sensitif | + `conformance-reviewer` + maksimal 2 auditor paling relevan |
| Besar | modul, > 1 PR, lintas platform | `solution-architect` sekali → `planner` → tiap PR sesuai ukurannya |

Bug yang penyebabnya belum jelas → `bug-investigator` dulu. Pipeline merah → `pipeline-fixer`.

![Alur /clint:develop](docs/images/develop-flow.png)

- **Tarik terbaru dulu**: base branch, docs, dan design, supaya rencana dan kode memakai acuan terbaru.
- **Rencana otomatis** untuk modul atau tugas > 1 PR; diperbarui bila dokumen berubah sejak rencana
  terakhir. Tugas kecil langsung dikerjakan tanpa file rencana.
- **Tempat kerja**: satu PR dikerjakan langsung di repo utama; worktree hanya dibuat bila beberapa PR
  jalan bersamaan. Perubahan Anda yang belum di-commit tidak pernah disentuh.
- **Tinjauan paralel** setelah kode ditulis; temuan wajib dikirim balik ke `developer`, maksimal 2
  putaran. Masih gagal → berhenti tanpa MR, perubahan disimpan sebagai commit `wip` lokal.
- **E2E** dijalankan bila rencana memintanya atau bila perubahan terlihat pengguna. Project Expo dengan
  **Pratinjau E2E** di adapter menguji sebelum MR lewat EAS Update ke channel khusus simulator (tanpa
  build native lokal, QA tidak ikut menerima). Status E2E wajib tertulis (lulus / tidak perlu /
  tertunda); **tertunda → MR dibuat Draft** (mode `push-base`: tidak di-push ke base) dan muncul di
  `status` sampai `/clint:test e2e !<n>` lulus.
- **Saran tinjauan langsung diterapkan**: saran di kode yang diubah PR ikut diperbaiki, lewat lint/test dan
  tinjauan ulang, lalu di-commit terpisah (`refactor: terapkan saran tinjauan`) supaya mudah diperiksa dan
  di-revert. Saran luar cakupan masuk deskripsi MR dengan tautan file#baris dan diff sekarang/usulan;
  terapkan nanti dengan `/clint:develop terapkan saran di !<n>`.
- **MR**: stage eksplisit (tanpa `git add -A`), tarik base lagi, push, buat MR, dan pastikan MR-nya
  benar-benar ada. PR yang bergantung dibangun di atas branch dependensinya; deskripsi MR menyebut
  urutan merge.

## Tim agent

![18 agent senior](docs/images/agent-team.png)

| Kelompok | Agent | Peran | Model |
|---|---|---|---|
| **Kerja** | `planner` | rencana per PR dari PRD, SAD, STD, API contract, prototype | Sonnet |
| | `developer` | menulis kode, lint, typecheck, test, standar SonarQube | Opus |
| | `e2e-tester` | E2E happy path + error path (mobile, web, API) | Sonnet |
| | `pipeline-fixer` | memperbaiki CI yang gagal dari penyebabnya, termasuk quality gate Sonar | Opus |
| | `bug-investigator` | akar masalah bug sebelum diperbaiki (hanya bila penyebab belum jelas) | Opus |
| | `release-engineer` | build, APK/IPA untuk UAT, update OTA, versi, changelog, kesiapan deploy | Sonnet |
| | `tech-writer` | status feedback/bug di docs, README, CHANGELOG, ADR | Sonnet |
| **Arsitektur** (tugas Besar saja) | `solution-architect` | tinjau rencana modul besar, keputusan lintas platform, ADR | Opus |
| **Tinjauan inti** (setiap PR) | `conformance-reviewer` | sesuai rencana, dokumen, dan aturan project? | Sonnet |
| | `code-reviewer` | clean code, clean architecture, SonarQube | Opus |
| **Tinjauan spesialis** (bila diff relevan) | `security-auditor` | OWASP Mobile Top 10 + MASVS, Top 10 web, API Security Top 10 | Opus |
| | `accessibility-auditor` | WCAG 2.2 AA: semantik, keyboard, fokus, label, kontras | Sonnet |
| | `performance-auditor` | target performa ketat: web (Core Web Vitals), mobile (startup, 60 fps), backend (latensi, query) | Sonnet |
| | `database-auditor` | migrasi aman, integritas, transaksi, indeks, N+1 | Opus |
| | `api-contract-auditor` | implementasi vs API contract, perubahan yang merusak klien | Sonnet |
| | `design-auditor` | selisih tampilan dengan prototype | Sonnet |
| **Pemantau** | `change-tracker` | apa yang berubah di docs, design, base branch, plus feedback QA yang masih open | Sonnet |
| | `status-reporter` | MR, pipeline, branch, worktree, disk | Haiku |

Setiap agent adalah engineer senior berpengalaman 10–15+ tahun di bidangnya, dan semuanya memegang standar
yang sama: pahami konteks dulu, solusi paling sederhana yang benar, setiap kesimpulan dibuktikan, kualitas
setara produksi (pengguna, keamanan, performa, biaya perawatan), jujur soal yang belum selesai, dan berhenti
bila keputusan di luar wewenangnya.

## Platform: mobile, web, backend

Setiap platform punya skill inti yang ringkas, referensi yang dibaca hanya bila task menyentuhnya, aturan
test, dan adapter berisi fakta stack project. Agent yang sama bekerja di ketiganya; yang berbeda adalah
skill dan auditor spesialis yang ikut meninjau.

| | Mobile | Web | Backend |
|---|---|---|---|
| Pasang | `/clint:setup mobile` | `/clint:setup web` | `/clint:setup backend` |
| Skill | `skill-mobile` | `skill-web` | `skill-backend` |
| Referensi | performance, accessibility, security, patterns | performance, accessibility, security, patterns | performance, api-contract, data, api-security, reliability |
| Aturan test | `mobile-e2e` | `web-e2e` | `backend-test` |
| Adapter | `.claude/mobile-stack.md` | `.claude/web-stack.md` | `.claude/backend-stack.md` |
| Auditor yang sering ikut | performa, keamanan, aksesibilitas, desain | performa, aksesibilitas, keamanan, desain | performa, database, kontrak API, keamanan |

Semua platform memakai `sonarqube.md` yang sama. Monorepo fullstack cukup satu `.claude/clint.json` dengan
beberapa `surfaces` (mis. `apps/mobile`, `apps/admin`, `apps/api`); skill dan auditor dipilih per bagian
kode yang berubah.

### Performa: target ketat di tiga platform

Standar Badr adalah performa terbaik, bukan "cukup". Setiap platform punya `references/performance.md` dengan
target yang lebih ketat dari ambang umum:

| Platform | Target utama | Diukur di |
|---|---|---|
| Web | LCP ≤ 1,8 dtk · INP ≤ 100 ms · CLS ≤ 0,05 · TTFB ≤ 400 ms · JS awal ≤ 170 KB gzip · skor audit lab ≥ 90 mobile / ≥ 95 desktop | build produksi, profil mobile (CPU 4× lebih lambat, 4G) |
| Mobile | cold start ≤ 2 dtk Android / ≤ 1,5 dtk iOS · 60 fps · dropped frames ≤ 1% · respons tap ≤ 100 ms · tanpa kebocoran memori | release build, perangkat acuan |
| Backend | p95 baca ≤ 200 ms / tulis ≤ 300 ms · query ≤ 50 ms · tanpa N+1 · blok event loop ≤ 50 ms · respons ≤ 1 MB | build produksi, data bervolume realistis |

- `developer` membaca acuan ini **selalu** untuk halaman, layar, atau endpoint baru, dan melaporkan angka
  sebelum/sesudah. Kalau tidak bisa diukur, laporannya "belum terukur"; target tidak pernah diklaim tanpa angka.
- `performance-auditor` menjadikan pelanggaran aturan dan regresi target sebagai temuan **Wajib**. Regresi
  menahan MR sampai diperbaiki atau Anda menyetujui pengecualiannya.
- Bagian lama yang sudah di bawah target sebelum PR tidak menahan MR, selama PR tidak memperburuknya;
  selisihnya dilaporkan sebagai utang performa.
- Project boleh menetapkan target lebih ketat di adapter §11, tidak boleh lebih longgar tanpa persetujuan.
- Kenaikan ukuran bundle wajib dijelaskan di MR (web > 20 KB, mobile > 50 KB gzip).

## Laporan pagi

![Laporan pagi gabungan](docs/images/morning-report.png)

Senin–Jumat jam 08.00, clint memeriksa **semua project aktif** (punya `.claude/clint.json` dan dibuka di
Claude Code 3 hari terakhir) dalam satu sesi, mode baca saja (`/clint:status all`). Begitu siap, layar
laporan terbuka, kalimat inti dibacakan, dan notifikasi muncul bersamaan. Jadwalnya dijalankan oleh menu
bar (SwiftBar), sekali per hari sebelum jam 13.00: laptop tidur jam 08.00 → jalan saat dibuka.

- Butir dikelompokkan per tindakan: *Perlu perhatian*, *Perlu dikerjakan*, *Perlu Anda cek*,
  *Menunggu pihak lain*.
- Feedback QA yang masih open dibaca sampai rinciannya, bukan hanya judul tabel.
- **Hanya butir milik Anda**: isi nama Anda di `~/.config/clint/user.json` (`name`) dan, untuk project tim,
  `docs.pic` di `.claude/clint.json` (mis. sprint tracker). Butir milik rekan cukup disebut jumlahnya.

```bash
scripts/install-greeting.sh 8 0          # jadwal Senin–Jumat 08.00 (juga lewat menu bar → Pengaturan)
scripts/install-greeting.sh --cabut      # matikan
scripts/morning-greeting.sh --uji        # uji layar + suara dengan data contoh
scripts/active-projects.sh 3             # project yang dianggap aktif
```

Arsip laporan: `~/Library/Logs/clint/`. Laporan lebih dari 3 hari dihapus otomatis; file teknis hanya
disimpan bila gagal.

## Menu bar

![Menu bar clint](docs/images/menu-bar.png)

Ikon clint di menu bar Mac (lewat SwiftBar) menampilkan kondisi kerja sepanjang hari:

| Ikon | Arti |
|---|---|
| angka | jumlah hal yang menunggu |
| cincin oranye + label | agent sedang bekerja, mis. `PR-2/4` |
| `✓` | semua aman |
| `!` | ada yang gagal |

Isi menu: kemajuan PR, setiap sesi Claude Code yang bekerja (termasuk di VS Code) beserta agent yang
sedang jalan, hal yang menunggu (submenu *Salin perintah*, *Buka MR di browser*, *Buka project di VS
Code*, *Tandai selesai*), dan tombol *Buka laporan terakhir*, *Cek semua project*, *Cek project*, *Halo
Clint*, *Pengaturan*.

Badge berkurang sendiri tanpa cek ulang: butir yang dikerjakan `develop` pindah ke *Menunggu review*;
MR yang merged/closed hilang, termasuk butir tanpa tautan bila ID-nya (mis. `BUG-42`) disebut MR yang
merged setelah laporan dibuat (dicek tiap 15 menit lewat `glab`/`gh`).

```bash
brew install --cask swiftbar
mkdir -p ~/.config/clint/swiftbar && ln -sf ~/Desktop/clint/swiftbar/clint.py ~/.config/clint/swiftbar/
defaults write com.ameba.SwiftBar PluginDirectory -string "$HOME/.config/clint/swiftbar" && open -a SwiftBar
```

Avatar dan ikon cincin (opsional): taruh gambar persegi di `~/.config/clint/avatar.jpg`, lalu
`python3 scripts/make-icon.py` (butuh Pillow). Gambar pribadi ini sengaja tidak disimpan di repo.
Setelah file plugin diubah, jalankan ulang SwiftBar.

Catatan: teks menu bar dan layar laporan saat ini masih berbahasa Indonesia.

## Mode JARVIS

![Mode JARVIS](docs/images/jarvis-mode.png)

| Kemampuan | Cara kerja |
|---|---|
| Sapaan pagi | lihat [Laporan pagi](#laporan-pagi) |
| Bersuara | setiap perintah ditutup dengan satu kalimat yang dibacakan + notifikasi Mac. Bahasa Indonesia memakai suara Damayanti; English memakai suara bawaan sistem |
| Perintah suara | **"Hey Siri, Halo Clint"** → clint menyapa → ucapkan *"cek project toko online"* atau *"cek semua project"* |
| Kabar ke HP | notifikasi push Claude saat agent selesai |

Pintasan **Halo Clint** (sekali, di app Pintasan): (1) *Jalankan Skrip Shell*
`bash ~/Desktop/clint/scripts/clint-voice.sh sapa`, (2) *Dikte Teks* bahasa Indonesia, (3) *Jalankan
Skrip Shell* `bash ~/Desktop/clint/scripts/clint-voice.sh "$1"` dengan *Teks yang Didikte* sebagai
argumen.

Matikan suara per project dengan `"suara": false` di `.claude/clint.json`, sementara dengan
`CLINT_SUARA=0`, atau *Pengaturan → Bisukan sampai besok* di menu bar. Agent **tidak** bergerak sendiri
tanpa perintah; ia hanya mengabari dan menyiapkan perintahnya.

## Otomatis tanpa perintah

| Kapan | Efek |
|---|---|
| sesi dimulai | 4 prinsip kerja dan setelan bahasa dimuat (prinsip kerja tidak dobel bila project sudah punya salinannya) |
| file diedit | formatter project dijalankan pada file itu, termasuk di worktree |
| sesi selesai dengan ≥ 40 baris kode belum ditinjau | `/clint:review` jalan sendiri: tinjau + perbaiki, sekali per perubahan |
| perintah selesai | kalimat inti dibacakan + notifikasi Mac |
| prompt, agent mulai/selesai, sesi berakhir | status sesi untuk menu bar (`~/.config/clint/sesi/`) |

Hook dimuat saat proses Claude dinyalakan. Setelah memasang atau memperbarui clint, lakukan **Reload
Window** di VS Code agar sesi baru memakai hook terbaru.

## Hemat token

Model tidak diturunkan; yang dijaga cara kerjanya:

- tiap perintah hanya memuat instruksi untuk jenis kerjanya (perintah dipecah per jenis kerja);
- peninjau menerima path file diff + potongan rencana, bukan dokumen utuh;
- hasil test `developer` diteruskan, tidak dijalankan ulang;
- putaran perbaikan hanya memverifikasi temuan sebelumnya;
- auditor hanya jalan bila diff relevan, maksimal 2 per PR; potret layar hanya bila perlu;
- review otomatis hanya untuk ≥ 40 baris, sekali per perubahan;
- pemantau (`change-tracker`, `status-reporter`) mengumpulkan bahan dalam **satu panggilan skrip**
  (`scripts/collect-changes.sh`, `scripts/collect-status.sh`) alih-alih puluhan putaran `git`/`grep`;
- `e2e-tester` menjalankan semua flow sekali, mengulang hanya yang gagal, dan tidak membuka potret layar
  kecuali log teks tidak cukup;
- menu bar, suara, status sesi, dan pembaruan badge berjalan di Mac tanpa token.

Gambaran dari pemakaian nyata (4 hari, tim mobile + monorepo): per PR, `developer` ≈ 1,1 dan semua
peninjau ≈ 0,6 (setara USD harga API). Biaya terbesar justru datang dari agent umum tanpa aturan clint
untuk E2E panjang; gunakan `/clint:develop` atau `/clint:test` agar `e2e-tester` dan aturannya yang dipakai.

## Konfigurasi

### Per project: `.claude/clint.json`

Dibuat oleh `/clint:setup` dan di-commit untuk seluruh tim:

```jsonc
{
  "baseBranch": "dev",
  "mr": { "cli": "glab", "targetBranch": "dev",      // glab (GitLab) / gh (GitHub)
          "mode": "mr" },                             // "push-base": langsung push ke baseBranch, tanpa MR
  "autoReviewMinLines": 40,                           // "autoReview": false untuk mematikan
  "worktreeRoot": "../mobile-worktrees",
  "relatedRepos": [                                   // [] untuk monorepo
    { "name": "docs",    "path": "../docs",    "branch": "main", "role": "docs" },
    { "name": "designs", "path": "../designs", "branch": "main", "role": "design" }
  ],
  "docs": { "language": "en",                         // bahasa dokumen project: en / id
            "plans": "docs/plans", "requirements": "../docs", "design": "../designs/aplikasi.html",
            "feedback": "../docs/qa/feedback",        // butir feedback/bug QA
            "pic": "docs/sprints" },                   // pembagian tugas; laporan hanya butir milik Anda
  "suara": true,
  "surfaces": [
    { "name": "mobile", "root": ".", "adapter": ".claude/mobile-stack.md",
      "lint": "bun run lint", "typecheck": "bun run typecheck", "test": "bun run test",
      "e2e": "bun run test:e2e", "formatFile": "bunx prettier --write" }
  ]
}
```

Path yang tidak berlaku diisi `"TIDAK ADA"`. Monorepo: tambah entri `surfaces` per app (mis.
`apps/admin` web, `apps/api` backend).

### Per orang: `~/.config/clint/`

Tidak disimpan di repo mana pun:

| File | Isi |
|---|---|
| `user.json` | `{"name": ["Nama Anda", "username-git"], "language": "id"}`: nama untuk filter PIC, bahasa pribadi |
| `avatar.jpg` | avatar laporan dan menu bar (opsional) |

## Pindah dari clint v1

clint v2 mengganti nama perintah, agent, dan file ke bahasa Inggris. Tidak ada alias untuk nama lama.

| v1 | v2 |
|---|---|
| `/clint:cek` | `/clint:status` (`semua` → `all`) |
| `/clint:jalankan` | `/clint:develop`; rilis → `/clint:release`; dokumen → `/clint:docs`; `jalankan e2e !n` → `/clint:test e2e !n` |
| `/clint:tinjau` (`--saja`) | `/clint:review` (`--only`) |
| `/clint:siapkan-project` (`sinkron`) | `/clint:setup` (`sync`) |
| `pengembang`, `perencana`, `penguji`, `peninjau`, `reviewer-senior` | `developer`, `planner`, `e2e-tester`, `conformance-reviewer`, `code-reviewer` |
| `auditor-keamanan`, `-aksesibilitas`, `-performa`, `-database`, `-kontrak-api`, `penyelaras-desain` | `security-`, `accessibility-`, `performance-`, `database-`, `api-contract-auditor`, `design-auditor` |
| `arsitek-solusi`, `insinyur-rilis`, `penulis-teknis`, `penyidik-bug`, `pemulih-pipeline` | `solution-architect`, `release-engineer`, `tech-writer`, `bug-investigator`, `pipeline-fixer` |
| `pelacak-perubahan`, `penjaga` | `change-tracker`, `status-reporter` |
| `~/.config/clint/saya.json` (`nama`) | `~/.config/clint/user.json` (`name`, `language`); dipindah otomatis saat sesi pertama |

Langkah per laptop: `claude plugin marketplace update clint && claude plugin update clint@clint`, lalu
**Reload Window**. Langkah per project (sekali, oleh satu orang): `/clint:setup sync`. Perintah ini
mengganti nama file referensi lama (`referensi/` → `references/`), menawarkan `sonarqube.md` dan
`docs.language`, lalu menunjukkan perbedaan lain dengan master. Commit hasilnya.

## Tanya jawab

**Apakah saya harus memilih peran?** Tidak. Semua orang boleh memakai semua perintah; pilih sesuai jenis
kerjanya.

**Rekan saya tidak memasang plugin. Apakah project tetap konsisten?** Ya untuk aturannya: skill platform,
rules, standar SonarQube, dan adapter disalin ke `.claude/` project. Perintah `/clint:*` dan agent hanya ada
bagi yang memasang plugin.

**Apakah clint akan push atau merge sendiri?** Push ke branch fitur dan membuat MR, ya. Merge selalu oleh
manusia. Mode `push-base` hanya dipakai bila tim memang push langsung ke base branch, dan tugas besar tetap
meminta konfirmasi sebelum push pertama.

**Kenapa tugas kecil saya tidak ditinjau semua auditor?** Karena tidak menambah nilai dan memboroskan token.
Ukuran dan area tugas menentukan siapa yang ikut meninjau.

**Quality gate Sonar project kami berbeda dari default.** Ambang dari quality gate project yang berlaku;
default *Sonar way* hanya dipakai bila tidak diketahui. Konvensi Sonar milik project (mis.
`docs/sonar-conventions.md`) ikut dipakai.

**Bagaimana menambahkan aturan khusus project?** Tulis di `CLAUDE.md` atau `.claude/rules/` project. Aturan
project selalu mengalahkan kebiasaan umum agent.

## Struktur repo dan perawatan

```
clint/
  README.md
  agents/            18 agent
  skills/            status · develop · review · test · docs · release · setup
  hooks/             prinsip kerja + bahasa, format, review otomatis, kabar, status sesi
  scripts/           sapaan pagi, layar laporan, perintah suara, aksi menu bar, ikon
  swiftbar/          plugin menu bar (clint.py, streamable)
  kit/               master skill/rules/adapter + sonarqube.md yang DISALIN ke project (lihat kit/README.md)
  docs/images/       gambar README; sumbernya di docs/images/source (python3 build.py)
  .claude-plugin/    plugin.json + marketplace.json (jangan dihapus atau dipindah)
```

Skill platform, rules, dan adapter **disalin** ke `.claude/` project supaya rekan tim tanpa plugin
tetap mendapat aturan yang sama. Aturan emas untuk master skill: kalimat yang bisa menjadi salah karena
orang lain mengubah kode tidak boleh ada di skill; tempatnya di adapter, atau diganti perintah
verifikasi (penjelasan: `kit/mobile/README.md`).

Memperbarui setelah mengubah kit:

```bash
cd ~/Desktop/clint && git commit -am "..."
claude plugin marketplace update clint && claude plugin update clint@clint
```

Lalu **Reload Window** di VS Code. Gambar README dibuat ulang dengan `python3 docs/images/source/build.py`
(butuh Microsoft Edge atau Google Chrome); datanya contoh fiktif.

## Peta jalan

| Fase | Isi | Status |
|---|---|---|
| 1 | core + mobile, alur PR otomatis, laporan pagi, menu bar, mode JARVIS | selesai |
| 2 | web: skill inti + referensi, aturan E2E, adapter; auditor aksesibilitas dan performa | selesai |
| 3 | backend: skill inti + referensi, aturan test, adapter; auditor database dan kontrak API | selesai |
| 4 | sweeping token: skrip pengumpul untuk pemantau, aturan gambar untuk `e2e-tester` | selesai |
| 5 | tim lengkap 18 agent + aturan tim seperlunya | selesai |
| 6 | **v2**: nama bahasa Inggris, 7 perintah per jenis kerja, dua bahasa, standar SonarQube | selesai |
| 7 | rantai dokumen yang bisa diatur per project (`docs` di `clint.json`) + template dokumen di `kit/docs/` | berikutnya |
| 8 | `business-analyst` (PM): MoM, confirmation list, risk register, BRD, PRD | rencana |
| 9 | `solution-architect` diperluas: SAD, API contract (OpenAPI 3.1 YAML), ADR | rencana |
| 10 | `qa-analyst` (QA): STD dan test case, uji terpandu, regresi, laporan bug; `/clint:test` diperluas | rencana |
| 11 | `sprint-tracker` + tampilan `status` per peran (PM, SA, QA, Dev, Designer) | rencana |
| 12 | `/clint:release` diperluas: ops (preflight, backup, health check), ekspor dokumen DOCX/PDF | rencana |
| 13 | mode adopsi: memetakan agent/skill lama di project ke clint, lalu uji di turborepo, magnet-rezeki, lajoo | rencana |
