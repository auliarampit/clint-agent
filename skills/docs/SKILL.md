---
name: docs
description: Pekerjaan dokumen tanpa mengubah kode — dokumen requirement (MoM, confirmation list, risk register, BRD, PRD) lewat business-analyst, STD dan test case lewat qa-analyst, sprint tracker (status, centang, PIC, rekap, carry-over) lewat sprint-tracker, serta status feedback/bug QA, Status PR di rencana, README, CHANGELOG, ADR, dokumentasi API, dan logbook harian lewat tech-writer. Pakai saat user bilang "buat PRD modul X dari MoM ini", "susun STD", "perbarui sprint tracker", "rekap sprint 9", "perbarui status feedback #8", "perbarui Status PR di rencana dari git log", "catat ADR keputusan X", "update CHANGELOG", "logbook", "tulis logbook hari ini". Perubahan kode → develop.
argument-hint: <dokumen dan perubahan yang diminta>
---

# Docs

## 1. Prasyarat

- Baca `.claude/clint.json`. Tidak ada → berhenti, tawarkan `/clint:setup`.
- **Bahasa**: laporan dan kabar suara memakai bahasa user (baris *Bahasa clint* di konteks sesi; default
  English). Isi dokumen: dokumen yang sudah ada mengikuti bahasanya sendiri; dokumen baru memakai
  `docs.language` (tidak ada → English). **Pengecualian:** file rencana di `docs.plans` memakai bahasa user.
- `R` = path plugin dan `<sid>` = id sesi, dari baris *Sesi clint* di konteks sesi.
- Permintaan ternyata butuh perubahan kode → serahkan ke skill `develop`.
- **Klaim** di awal setiap run (kecuali perubahan satu-dua baris yang langsung selesai) supaya sesi lain tidak
  disarankan pekerjaan yang sama, dan hapus di akhir termasuk bila gagal:
  `mkdir -p ~/Library/Logs/clint/kerja && printf '%s' '{"dir":"<repo utama absolut>","rencana":null,"prs":[],"perintah":"<perintah persis>","judul":"docs <ringkas + ID butir>","label":"docs","tahap":"<agent>"}' > ~/Library/Logs/clint/kerja/<sid>.json`
  · akhir: `rm -f ~/Library/Logs/clint/kerja/<sid>.json`. `dir` seperti di skill `develop` (*Status di menu bar dan klaim PR*).

## 2. Kerjakan

Perubahan satu-dua baris yang jelas letaknya (mis. satu status butir) → kerjakan langsung di sesi ini.
Selain itu panggil **satu** agent sesuai jenis dokumen, dengan: permintaan user, path dokumen (dari `docs.*`
atau yang disebut user), sumber (MoM/notulen/teks yang ditempel, MR, commit), dan bahasa:

| Dokumen | Agent |
|---|---|
| MoM, confirmation list, risk register, BRD, PRD (FR/AC ber-ID), dampak perubahan requirement ke dokumen turunan | `business-analyst` |
| STD, test case, matriks AC↔TC | `qa-analyst` |
| Sprint tracker (`docs.pic`): status, centang, PIC, rekap, carry-over, teks ekspor | `sprint-tracker` |
| Status feedback/bug QA, Status PR di rencana, README, CHANGELOG, ADR, catatan rencana, dokumentasi API, logbook | `tech-writer` |

Tanpa peninjau kode. Permintaan yang menyentuh dua jenis (mis. PRD berubah lalu STD perlu disesuaikan) →
agent pertama, lalu daftar dampak dari laporannya diteruskan ke agent kedua.

**Status PR di rencana dari git log** (rencana lama, mode `push-base` tanpa trailer `Plan:`): jalankan
`python3 "$R/scripts/plan-status.py" <rencana> --session <sid>`. Ada baris "Sedang dikerjakan sesi lain: catat Status
PR" → berhenti, sebut di laporan, jangan dikerjakan dobel. Selain itu klaim dulu supaya sesi lain tidak
disarankan langkah yang sama: klaim di atas diisi `"rencana":"<rencana>","tugas":"status-pr"`. Lalu beri `tech-writer` daftar PR beserta branch dan isinya.
Ia mencocokkan dengan `git log origin/<baseBranch>` (judul commit, ID modul/requirement, file yang disentuh), lalu
menulis bagian `## Status PR` (format: `- [x] PR-n · ✅ selesai · commit <hash>`, dipisah baris kosong). PR yang
buktinya tidak jelas ditulis `⬜ belum mulai` dan disebut di laporan, bukan ditebak selesai.

**Logbook** (`logbook [YYYY-MM-DD]`, default hari ini): satu entri per hari kerja per orang di
`<docs.logbook>/YYYY-MM.md`, entri terbaru di atas. `docs.logbook` kosong/`TIDAK ADA` → tanya foldernya dan
tawarkan mengisinya di `clint.json`. Tarik repo docs dulu (`git pull --ff-only`) supaya entri rekan tidak bentrok.
Jalankan `bash "$R/scripts/logbook-draft.sh" <repo utama> <tanggal>` lalu beri `tech-writer` keluarannya, plus
yang disampaikan user di percakapan (keputusan, kendala, rencana). Entri tanggal itu sudah ada → diperbarui,
bukan ditambah. Format (judul bagian mengikuti `docs.language`; `en`: Done, Decisions, Blockers, Next):

```markdown
## 2026-10-21 · <git user.name>

**Dikerjakan**
- <hasil, bukan aktivitas> (!12, `a1b2c3d`)

**Keputusan**
- <keputusan singkat> → ADR-007

**Kendala**
- -

**Rencana besok**
- -
```

Isi hanya dari bukti: keluaran skrip, percakapan, `mempalace search "<topik>" --wing <memory.wing> --since <tanggal>`
bila mempalace aktif. Bagian tanpa bahan diisi `-`, tidak dikarang. **Satu fakta di satu tempat**: keputusan yang
sudah atau perlu jadi ADR cukup dirujuk ID-nya, status PR tetap di rencana, status tugas tetap di sprint tracker;
logbook hanya merangkum dan menautkan.

Dokumen di repo terkait (`relatedRepos`): ikuti alur git repo itu (CLAUDE.md/memori project); stage
eksplisit, commit mengikuti gaya repo, push/MR mengikuti `mr.mode` (aturan skill `develop` langkah 5.5).

## 3. Laporan

Maksimal ±6 baris: dokumen dan bagian yang berubah, bukti yang dirujuk, dokumen turunan yang terdampak, commit/MR
bila ada. Blok terakhir wajib **Berikutnya** (aturan skill `develop` bagian 6).

Tutup dengan kabar suara: satu kalimat inti (maks ±20 kata, tanpa simbol/kode/path):

```bash
printf '%s' "<kalimat inti>" > "${TMPDIR:-/tmp}/clint-kabar-<sid>.txt"
```
