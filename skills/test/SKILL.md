---
name: test
description: Menguji fitur atau MR tanpa mengubah kode produk — menulis dan menjalankan E2E (Maestro, Playwright, dll. sesuai adapter) untuk satu fitur, menyelesaikan E2E yang tertunda di MR Draft (satu, beberapa, atau semua Draft sekaligus), serta pekerjaan QA lewat qa-analyst (test case dari AC, pilih regresi untuk MR, laporan bug). Pakai saat QA/dev bilang "uji fitur X", "jalankan E2E login", "lanjutkan E2E !123", "tutup semua draft", "e2e !12 !14", "test case modul X", "regresi untuk !123", "catat bug ini". Bug yang ditemukan diperbaiki lewat develop.
argument-hint: <fitur | e2e !n [!m ...] | e2e draft | tc <modul> | regresi !n | bug <deskripsi>>
---

# Test

Kode produk **tidak** diubah di sini. Bug produk yang ditemukan dilaporkan, lalu diperbaiki lewat
`/clint:develop`.

## 1. Prasyarat

- Baca `.claude/clint.json`. Tidak ada → berhenti, tawarkan `/clint:setup`.
- **Bahasa**: laporan dan kabar suara memakai bahasa user (baris *Bahasa clint* di konteks sesi; default
  English). Sebut bahasa itu di prompt agent. Dokumen QA memakai `docs.language`.
- `R` = path plugin dan `<sid>` = id sesi, dari baris *Sesi clint* di konteks sesi.
- Untuk E2E: tentukan surface dari fitur/MR. Adapter surface itu menyatakan E2E `TIDAK ADA` → berhenti dan laporkan.

## 2. Jalur

| Argumen | Jalur |
|---|---|
| `e2e !<n>` | satu MR Draft: langkah 3 untuk MR itu |
| `e2e !<a> !<b> ...` | beberapa MR: langkah 3 untuk setiap MR, **berurutan** (lihat di bawah) |
| `e2e draft` | semua MR Draft milik user di project ini: `glab mr list --draft --author=@me -F json` / `gh pr list --draft --author @me --json number,headRefName,baseRefName`, lalu sama seperti beberapa MR |
| Nama fitur/flow | branch baru dari `origin/<baseBranch>` (aturan path kerja: skill `develop` langkah 5.1), panggil `e2e-tester` dengan path kerja, fitur, dan sumber test case (STD/TC di `docs.requirements` bila ada) |
| `tc <modul>`, "buat test case", "review test case" | agent `qa-analyst`: test case dari PRD/AC (TC→AC) di `docs.requirements`; perubahan dokumen di-commit seperti skill `docs` |
| `regresi !<n>` / "regresi untuk rilis" | agent `qa-analyst`: pilih TC yang terdampak diff MR/rilis; hasilnya daftar TC (dan flow E2E yang ada) untuk dijalankan |
| `bug <deskripsi>` | agent `qa-analyst`: laporan bug di `docs.feedback` dengan format yang sudah dipakai project |

**Beberapa MR Draft: urutan, bukan paralel.** Satu simulator/perangkat dan satu channel pratinjau E2E dipakai
satu MR pada satu waktu, jadi beberapa sesi yang menjalankan E2E bersamaan saling mengganggu. Urutan: MR
bertumpuk dari dasarnya dulu (MR yang target branch-nya `mr.targetBranch` lebih dulu, lalu yang menumpuk di
atasnya), selain itu nomor MR terkecil dulu. Satu MR gagal tidak menghentikan MR lain yang tidak menumpuk di
atasnya. Maksimal 3 MR per run (konteks sesi); sisanya masuk *Berikutnya*.

## 3. E2E untuk satu MR

`git fetch`, lalu kerjakan di branch MR itu: `bash "$R/scripts/repo-busy.sh" . <sid>` → `bebas` →
`git switch <source_branch>` di repo utama; `dipakai` → worktree (aturan skill `develop` langkah 5.1). Tulis klaim
sesi seperti skill `develop` (*Status di menu bar dan klaim PR*). Panggil `e2e-tester` dengan path kerja, fitur dari deskripsi MR, dan sumber
test case.

- **Lulus**: commit file flow saja (stage eksplisit, gaya commit repo), push ke branch MR yang sama, perbarui
  deskripsi menjadi `E2E: lulus` dan tandai siap (`glab mr update <n> --ready` / `gh pr ready <n>`). PR dari
  rencana: ikutkan `python3 "$R/scripts/plan-status.py" <rencana> --repo <path kerja> --set PR-<n>=review --write`
  di commit itu. Mode `push-base`: push ke base mengikuti aturan `push-base` di skill `develop` langkah 5.5.
- **Gagal karena bug produk**: jangan ubah kode produk dan jangan longgarkan assertion. Laporkan flow,
  langkah, yang diharapkan, dan yang terjadi. *Berikutnya* berisi `/clint:develop perbaiki <ringkasan> di !<n>`.
- **Tertunda** (perangkat, build, atau channel belum siap): laporkan langkah persis dari `e2e-tester`; MR
  tetap Draft.

Fitur baru (bukan MR): bila lulus, push dan buat MR seperti skill `develop` langkah 5.5.

## 4. Laporan

Maksimal ±8 baris, ditambah satu baris per MR bila beberapa: status E2E, flow yang dibuat/dijalankan, hasil per
flow, dan tindak lanjutnya. Blok terakhir wajib **Berikutnya** (aturan skill `develop` bagian 6).

Tutup dengan kabar suara: satu kalimat inti (maks ±20 kata, tanpa simbol/kode/path):

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar-<sid>.txt"
```
