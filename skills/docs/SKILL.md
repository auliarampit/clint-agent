---
name: docs
description: Pekerjaan dokumen tanpa mengubah kode — memperbarui status butir feedback/bug di dokumen QA, README, CHANGELOG, ADR, catatan rencana, dan dokumentasi API agar sinkron dengan kode dan keputusan. Pakai saat user bilang "perbarui status feedback #8", "catat ADR keputusan X", "update CHANGELOG". Perubahan kode → develop.
argument-hint: <dokumen dan perubahan yang diminta>
---

# Docs

## 1. Prasyarat

- Baca `.claude/clint.json`. Tidak ada → berhenti, tawarkan `/clint:setup`.
- **Bahasa**: laporan dan kabar suara memakai bahasa user (baris *Bahasa clint* di konteks sesi; default
  English). Isi dokumen: dokumen yang sudah ada mengikuti bahasanya sendiri; dokumen baru memakai
  `docs.language` (tidak ada → English). **Pengecualian:** file rencana di `docs.plans` memakai bahasa user.
- Permintaan ternyata butuh perubahan kode → serahkan ke skill `develop`.

## 2. Kerjakan

Perubahan satu-dua baris yang jelas letaknya (mis. satu status butir) → kerjakan langsung di sesi ini.
Selain itu panggil agent `tech-writer` dengan: permintaan user, path dokumen (dari `docs.*` atau yang
disebut user), bukti yang sudah diketahui (MR, commit), dan bahasa. Tanpa peninjau kode.

Dokumen di repo terkait (`relatedRepos`): ikuti alur git repo itu (CLAUDE.md/memori project); stage
eksplisit, commit mengikuti gaya repo, push/MR mengikuti `mr.mode` (aturan skill `develop` langkah 5.5).

## 3. Laporan

Maksimal ±6 baris: dokumen dan bagian yang berubah, bukti yang dirujuk, commit/MR bila ada. Baris terakhir
wajib **Berikutnya** (aturannya sama dengan skill `develop` bagian 6).

Tutup dengan kabar suara: satu kalimat inti (maks ±20 kata, tanpa simbol/kode/path):

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar.txt"
```
