---
name: test
description: Menguji fitur atau MR tanpa mengubah kode produk — menulis dan menjalankan E2E (Maestro, Playwright, dll. sesuai adapter) untuk satu fitur, atau menyelesaikan E2E yang tertunda di MR ("e2e !123"). Pakai saat QA/dev bilang "uji fitur X", "jalankan E2E login", "lanjutkan E2E !123". Bug yang ditemukan diperbaiki lewat develop.
argument-hint: <fitur | e2e !nomor-MR>
---

# Test

Kode produk **tidak** diubah di sini. Bug produk yang ditemukan dilaporkan, lalu diperbaiki lewat
`/clint:develop`.

## 1. Prasyarat

- Baca `.claude/clint.json`. Tidak ada → berhenti, tawarkan `/clint:setup`.
- **Bahasa**: laporan dan kabar suara memakai bahasa user (baris *Bahasa clint* di konteks sesi; default
  English). Sebut bahasa itu di prompt agent.
- Tentukan surface dari fitur/MR. Adapter surface itu menyatakan E2E `TIDAK ADA` → berhenti dan laporkan.

## 2. Jalur

| Argumen | Jalur |
|---|---|
| `e2e !<n>` (E2E tertunda di MR) | `git fetch`, lalu kerjakan di branch MR itu (working tree bersih → `git switch <source_branch>`; tidak bersih → worktree). Panggil `e2e-tester` dengan path kerja, fitur dari deskripsi MR, dan sumber test case |
| Nama fitur/flow | Branch baru dari `origin/<baseBranch>` (aturan path kerja: skill `develop` langkah 5.1). Panggil `e2e-tester` dengan path kerja, fitur, dan sumber test case (STD/TC di `docs.requirements` bila ada) |

## 3. Hasil

- **Lulus**: commit file flow saja (stage eksplisit, gaya commit repo), lalu:
  - `e2e !<n>` → push ke branch MR yang sama, perbarui deskripsi menjadi `E2E: lulus` dan tandai siap
    (`glab mr update <n> --ready` / `gh pr ready <n>`). Mode `push-base`: push ke base mengikuti aturan
    `push-base` di skill `develop` langkah 5.5;
  - fitur baru → push dan buat MR seperti skill `develop` langkah 5.5–5.6.
- **Gagal karena bug produk**: jangan ubah kode produk dan jangan longgarkan assertion. Laporkan flow,
  langkah, yang diharapkan, dan yang terjadi. Baris *Berikutnya* berisi `/clint:develop perbaiki <ringkasan>`
  (sebut `!<n>` bila dari MR).
- **Tertunda** (perangkat, build, atau channel belum siap): laporkan langkah persis dari `e2e-tester`; MR
  tetap Draft.

## 4. Laporan

Maksimal ±8 baris: status E2E, flow yang dibuat/dijalankan, hasil per flow, dan tindak lanjutnya. Baris
terakhir wajib **Berikutnya** (aturannya sama dengan skill `develop` bagian 6).

Tutup dengan kabar suara: satu kalimat inti (maks ±20 kata, tanpa simbol/kode/path):

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar.txt"
```
