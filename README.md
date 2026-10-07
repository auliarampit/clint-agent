# clint

Tim agent Claude Code: dari membaca dokumen, menulis kode, meninjau, menguji, sampai membuat MR.
Dipasang sekali sebagai plugin, berlaku di semua project. Anda cukup review dan merge.

## 4 perintah

| Perintah | Untuk |
|---|---|
| `/clint:cek` | pagi / "ada update apa?": tarik docs & design, cocokkan dengan kode, MR & pipeline, disk |
| `/clint:jalankan <apa yang mau dikerjakan>` | **semua pekerjaan**, kecil sampai modul penuh. Hasil: MR + satu laporan |
| `/clint:tinjau !123` | review MR rekan (hanya laporan) |
| `/clint:siapkan-project mobile` | sekali per project |

Anda **tidak perlu memanggil agent**; agent dipanggil oleh perintah di atas.

## Contoh `jalankan`

```
/clint:jalankan perbaiki daftar produk: tambah tarik-untuk-muat-ulang     ← tugas kecil, 1 PR
/clint:jalankan MOB-10                                                   ← modul baru, rencana dibuat otomatis
/clint:jalankan docs/plans/mr-mob-10.md                                  ← lanjutkan rencana (PR selesai dilewati)
/clint:jalankan docs/plans/mr-mob-10.md PR-5                             ← hanya PR-5
/clint:jalankan docs/plans/mr-mob-10.md PR-5..PR-7                       ← PR-5 sampai PR-7
/clint:jalankan ../docs/<feedback-QA>.md                                 ← butir feedback/bug yang masih open
/clint:jalankan terapkan saran reviewer 1 dan 2 di !123             ← tindak lanjut MR, push ke MR yang sama
/clint:jalankan perbaiki pipeline !123                                   ← pipeline merah
/clint:jalankan                                                          ← kerjakan temuan /clint:cek barusan
```

## Rutinitas

```
pagi    /clint:cek
kerja   /clint:jalankan ...   → tunggu laporan → review MR → merge
rekan   /clint:tinjau !123
```

Kode yang Anda tulis langsung di sesi (≥ 40 baris) ditinjau dan dirapikan otomatis.

## Yang terjadi di dalam `jalankan`

```
tarik dev + docs + designs
   → rencana: dibuat / diperbarui bila perlu (tugas kecil: tanpa rencana)
   → per PR (yang tidak saling bergantung: paralel, maks 3):
        branch baru (worktree hanya bila beberapa PR jalan bersamaan) → pengembang menulis kode
        → peninjau + reviewer-senior (+ auditor-keamanan, penyelaras-desain bila relevan)
        → temuan wajib diperbaiki otomatis (maks 2 putaran)
        → penguji E2E bila rencana minta
        → commit (stage eksplisit) → push → MR ke dev → verifikasi MR → kembali ke branch asal
   → satu laporan: tabel PR/MR/putusan peninjau + urutan merge
```

PR yang bergantung pada PR lain dibangun di atas branch-nya; MR tetap ke `dev`, deskripsi
menyebut urutan merge. Satu PR gagal → hanya PR yang bergantung padanya dilewati.

## Agent (dipanggil otomatis)

| Agent | Peran | Model |
|---|---|---|
| `perencana` | rencana per PR dari PRD/SAD/STD/API contract/prototype | Sonnet |
| `pengembang` | menulis kode, lint/typecheck/test | Opus |
| `peninjau` | sesuai rencana, dokumen, aturan project? | Sonnet |
| `reviewer-senior` | clean code & clean architecture? | Opus |
| `auditor-keamanan` | ada celah keamanan? | Opus |
| `penyelaras-desain` | sama dengan prototype? | Sonnet |
| `penguji` | E2E happy path + error path | Sonnet |
| `pemulih-pipeline` | perbaiki CI yang gagal | Opus |
| `pelacak-perubahan` | apa yang berubah di docs/design/dev | Sonnet |
| `penjaga` | MR, pipeline, branch, worktree, disk | Haiku |

## Otomatis tanpa perintah (hooks)

| Kapan | Efek |
|---|---|
| sesi dimulai | 4 prinsip kerja dimuat (tidak dobel bila project sudah punya salinannya) |
| file diedit | formatter project dijalankan pada file itu |
| sesi selesai dengan ≥ 40 baris kode belum ditinjau | `/clint:tinjau` jalan sendiri: tinjau + perbaiki. Sekali per perubahan |

## Mode JARVIS

| Kemampuan | Cara kerja |
|---|---|
| **Sapaan pagi** | Senin–Jumat 08.00, clint memeriksa **semua project aktif** (punya `.claude/clint.json` dan dibuka di Claude Code 3 hari terakhir) dalam satu sesi, mode baca saja. Begitu siap: **layar laporan gabungan terbuka**, kalimat inti dibacakan, notifikasi muncul. Arsip: `~/Library/Logs/clint/<tanggal>.html`. Laptop tidur → jalan saat bangun |
| **Bersuara** | `cek` dan `jalankan` menutup dengan satu kalimat inti yang dibacakan (suara Damayanti, bahasa Indonesia) + notifikasi Mac. Gratis token (suara lokal) |
| **Perintah suara** | **"Hey Siri, Halo Clint"** → clint menjawab → ucapkan *"cek project toko online"* / *"cek semua project"* → layar laporan + suara. Tanpa menekan mikrofon. Perlu Pintasan "Halo Clint" (lihat di bawah) |
| **Kabar ke HP** | notifikasi push saat agent selesai |
| **Ingat kebiasaan** | memori Claude Code |

Agent **tidak** bergerak sendiri tanpa perintah (mis. memperbaiki pipeline diam-diam); ia hanya
mengabari dan menyiapkan perintahnya.

```bash
scripts/pasang-sapaan.sh 8 0                                     # jadwal; project aktif dideteksi otomatis
scripts/pasang-sapaan.sh --cabut                                 # matikan sapaan pagi
scripts/sapaan-pagi.sh --uji                                     # uji layar + suara dengan data contoh
scripts/proyek-aktif.sh 3                                        # lihat project yang dianggap aktif
```

**Pintasan "Halo Clint"** (sekali, di app Pintasan/Shortcuts): buat pintasan baru bernama **Halo Clint**
dengan 3 tindakan: (1) *Jalankan Skrip Shell* `bash ~/Desktop/clint/scripts/clint-suara.sh sapa`,
(2) *Dikte Teks* — bahasa Indonesia, berhenti setelah jeda, (3) *Jalankan Skrip Shell*
`bash ~/Desktop/clint/scripts/clint-suara.sh "$1"` dengan input *Teks yang Didikte* sebagai argumen.

**Menu bar (SwiftBar):** ikon clint di menu bar Mac. Badge oranye = jumlah hal yang menunggu, ✓ hijau =
aman, ! merah = ada yang gagal, ⟳ = agent sedang bekerja (dengan label kemajuan). Menu berisi hal yang
menunggu (submenu *Salin perintah*), tombol *Buka laporan terakhir*, *Cek semua project*, *Cek project ▸*,
*Halo Clint*, dan *Pengaturan ▸* (suara, bisukan sampai besok). Membaca file lokal saja, tidak memakai token.

```bash
brew install --cask swiftbar
mkdir -p ~/.config/clint/swiftbar && ln -sf ~/Desktop/clint/swiftbar/clint.py ~/.config/clint/swiftbar/
defaults write com.ameba.SwiftBar PluginDirectory -string "$HOME/.config/clint/swiftbar" && open -a SwiftBar
```

Bagian **Agent & sesi** di menu menampilkan setiap sesi Claude Code (termasuk di VS Code) yang sedang
bekerja, berjalan di latar, menunggu Anda, atau baru selesai, lengkap dengan agent yang sedang jalan dan
tugasnya. Datanya dari hook clint (`hooks/status-sesi.sh` → `~/.config/clint/sesi/`), tanpa token. Klik
sesi atau butir tugas → VS Code terbuka di project itu; butir MR → MR terbuka di browser.

**Badge ikut berkurang tanpa cek ulang (tanpa token):** `jalankan` yang membuat MR untuk sebuah butir
memindahkannya ke *Menunggu review*; MR yang sudah merged/closed hilang sendiri (status MR dicek tiap
15 menit lewat glab/gh); atau klik *Tandai selesai* di submenu butir.

**Hanya tugas milik Anda:** isi `~/.config/clint/saya.json` (`{"nama":["Aulia"]}`) dan, untuk project tim,
`docs.pic` di `.claude/clint.json` (dokumen pembagian tugas, mis. sprint tracker). `cek` lalu hanya
melaporkan butir yang PIC-nya Anda; milik orang lain cukup disebut jumlahnya.

Ikon dan animasi cincin dibuat dari gambar pribadi `~/.config/clint/avatar.jpg` dengan
`python3 scripts/buat-ikon.py` (butuh Pillow); tanpa itu dipakai ikon bawaan. Plugin berjenis streamable:
perubahan tampil dalam 1 detik dan cincin avatar berputar saat agent bekerja.
Setelah file plugin diubah, jalankan ulang SwiftBar (`osascript -e 'quit app "SwiftBar"'; open -a SwiftBar`).

**Avatar (opsional):** taruh gambar persegi di `~/.config/clint/avatar.jpg`; layar laporan menampilkannya.
Gambar ini sengaja tidak disimpan di repo.

Log dibersihkan otomatis: laporan lebih dari 3 hari dihapus, file teknis hanya disimpan bila gagal.

Matikan suara per project: `"suara": false` di `.claude/clint.json`; sementara: `CLINT_SUARA=0`.

## Hemat token

Model tidak diturunkan; yang dijaga cara kerjanya:

- peninjau menerima path file diff + potongan rencana, bukan dokumen utuh;
- hasil test pengembang diteruskan, tidak dijalankan ulang;
- putaran perbaikan hanya memverifikasi temuan sebelumnya;
- auditor & penyelaras hanya jalan bila diff relevan; potret layar hanya bila perlu;
- tinjau otomatis hanya ≥ 40 baris, sekali per perubahan;
- setiap agent membaca seperlunya (`grep`, potongan baris), memotong keluaran panjang, laporan padat.

## Konfigurasi project: `.claude/clint.json`

Dibuat oleh `siapkan-project`.

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
  "docs": { "plans": "docs/plans", "requirements": "../docs", "design": "../designs/aplikasi.html" },
  "surfaces": [
    { "name": "mobile", "root": ".", "adapter": ".claude/mobile-stack.md",
      "lint": "bun run lint", "typecheck": "bun run typecheck", "test": "bun run test",
      "e2e": "bun run test:e2e", "formatFile": "bunx prettier --write" }
  ]
}
```

Monorepo: tambah entri `surfaces` per app (mis. `apps/admin` web, `apps/api` backend).

## Struktur repo

```
clint/
  README.md
  agents/            10 agent
  skills/            cek · jalankan · tinjau · siapkan-project
  hooks/
  kit/               master skill/rules/adapter yang DISALIN ke project (lihat kit/README.md)
  .claude-plugin/    (tersembunyi) plugin.json + marketplace.json — jangan dihapus/dipindah
```

Skill platform, rules, dan adapter disalin ke `.claude/` project supaya rekan tim tanpa plugin
tetap mendapat aturan yang sama. `/clint:siapkan-project sinkron` membandingkan salinan dengan master.

## Pasang & update

```bash
claude plugin marketplace add auliarampit/clint-agent    # dari GitHub
# atau lokal: claude plugin marketplace add ~/Desktop/clint
claude plugin install clint@clint

# setelah mengubah kit
cd ~/Desktop/clint && git commit -am "..."
claude plugin marketplace update clint && claude plugin update clint@clint
```

Lalu di VSCode: `Cmd+Shift+P` → **Developer: Reload Window**, buka sesi baru.

## Aturan emas master skill

Kalimat yang bisa menjadi salah karena orang lain mengubah kode tidak boleh ada di skill; tempatnya di
adapter, atau diganti perintah verifikasi. Penjelasan: `kit/mobile/README.md`.

## Peta jalan

| Fase | Isi | Status |
|---|---|---|
| 1 | core + mobile | selesai |
| 2 | web (konvensi portable + adapter, dari rules frontend project yang sudah berjalan) | berikutnya |
| 3 | backend (backend-features, backend-i18n, prisma-database) | menyusul |
