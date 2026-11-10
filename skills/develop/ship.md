# Develop · commit, MR, dan penutupan (langkah 5.5 dan 5.6)

Dibaca saat sampai langkah 5.5 (juga dirujuk `test`, `docs`, `release`). Ringkasan ada di `SKILL.md` 5.5.

## 5.5 Commit, push, MR, bersihkan (satu perintah)

Yang ditulis model hanya isi berkas; sisanya dijalankan skrip tanpa token:
- **Pesan commit** mengikuti gaya `git log --oneline -15` repo. PR dari rencana: commit utama diberi trailer
  `Plan: <nama-file-rencana-tanpa-.md> PR-<n>` (baris terakhir pesan), supaya status selesai terdeteksi di
  mode `push-base`. Perbaikan Low punya pesan sendiri (langkah 5.3).
- **Daftar file** per commit, satu path per baris, dari laporan `developer`/`e2e-tester` (stage eksplisit;
  tanpa screenshot, log, atau output build).
- **Deskripsi MR**: ringkasan, requirement yang dipenuhi (ID), cara verifikasi, hasil lint/typecheck/test/E2E,
  dan yang belum dikerjakan. Ikuti format MR sebelumnya kalau repo punya pola. Tanpa AI slop: tanpa nama
  agent, jumlah putaran tinjauan, atau kalimat pujian. E2E tertunda → memuat `E2E: tertunda, <alasan>`.
- **Temuan luar cakupan dan usulan yang dilewati** sebagai JSON
  `[{"path","line","sekarang","usulan","alasan","agent","tingkat"}]`, supaya user bisa memvalidasinya.
  Yang Critical/Major/Minor juga ditambahkan sebagai butir rencana atau issue ber-ID (`quality-gates.md` §4),
  supaya tidak hanya tinggal di deskripsi MR.

```bash
python3 "$R/scripts/ship-pr.py" --dir <path kerja> \
  --commit <pesan-utama.txt>:<file-utama.txt> [--commit <pesan-low.txt>:<file-low.txt>] \
  [--plan <rencana> --pr PR-<n> --state review|draft|done] [--desc <deskripsi.md>] [--draft] \
  [--saran <saran.json>] [--check "<lint>" --check "<test terkait>"] \
  [--butir "<ID/teks butir status>" --proyek <nama project>] \
  [--verifikasi lulus|belum|tidak-terreproduksi] [--asal <branch asal> | --worktree]
```

`--verifikasi` wajib diisi untuk PR dari bug/feedback: `lulus` (jalur persis laporan lulus sebelum dan sesudah),
`belum`, atau `tidak-terreproduksi`; dicatat ke log audit.

Skrip menulis `## Status PR` di rencana dan mengikutkannya di commit pertama (`review` untuk MR biasa, `draft`
bila E2E tertunda, `done` untuk `push-base`), commit berurutan, menarik base dan rebase bila tertinggal (lalu
menjalankan ulang `--check` saja), push, membuat MR ke `mr.targetBranch` (Draft dengan `--draft`),
**memverifikasi MR benar-benar ada**, menempel blok "Saran tinjauan" ke deskripsi, memindahkan butir laporan
`status` ke "menunggu review" (`--butir`, wajib bila PR berasal dari butir itu), lalu bersih-bersih: kembali
ke `--asal` dan menghapus branch lokal, atau menghapus worktree. Tidak pernah force push; tidak menunggu
pipeline (hasilnya muncul di `/clint:status`).

Keluaran `commit=`, `rebase=`, `mr=!<n> <url>`, `push=`, `bersih=`; berhenti dengan `error=` dan exit:
3 konflik rebase (branch dibiarkan seperti sebelum rebase), 4 cek setelah rebase gagal, 5 push ke base ditolak
(commit tetap di base lokal; minta user menjalankan `git push origin <baseBranch>`), 6 MR tidak terverifikasi
(beri user tautan "create merge request" dari keluaran push). Exit selain 0 → jalur kegagalan di bawah.

**`push-base`** (tim langsung push ke base, tanpa MR): PR dikerjakan satu per satu urut gelombang, tanpa MR
bertumpuk; skrip fast-forward base di repo utama lalu push. Tugas besar (> 1 PR) atau menyentuh pekerjaan
orang lain → konfirmasi ke user sekali sebelum push pertama. Blok saran dicetak di laporan akhir. Menerapkan
saran di MR nanti: `/clint:develop terapkan saran di !<n>`.

Kegagalan satu PR (masih ada temuan setelah 3 putaran, test gagal, konflik rebase):

- jangan buat MR untuk PR itu;
- commit lokal semua perubahannya (stage eksplisit) dengan pesan `wip(<PR>): tertahan, <alasan>`,
  **jangan push**; PR dari rencana: tulis dulu `--set PR-<n>=held:<alasan>` ke rencana (langkah 5.5) dan
  ikutkan di commit itu. Tanpa worktree, kembali ke branch asal user. Branch/worktree itu disebut di
  laporan untuk diperiksa user. (Working tree bersih = hook tinjau otomatis tidak terpicu ulang.)
- PR yang bergantung padanya **dilewati**; PR lain tetap jalan.

## 5.6 Penutupan modul (`quality-gates.md` §3)

Setelah PR terakhir sebuah rencana modul jadi MR (sisa `plan-status.py` hanya PR penutupan, atau semua ✅/🔍),
jalankan penutupan sebelum melaporkan modul selesai:
1. `/clint:review fitur <nama>` per layar/endpoint modul. `conformance-reviewer` menghasilkan matriks FR/AC →
   `path:baris` + test/E2E terhadap PRD, kontrak, dan prototipe **terbaru**.
2. Gerbang `quality-gates.md` §1 pada seluruh folder sumber (duplikasi, kode mati, sonarjs, audit).
3. Harness ukur penuh dan `baseline.md` diperbarui.
4. Deviasi terbuka di `## Deviasi` rencana disebut beserta dokumen yang belum diperbarui.

Temuan menjadi PR perbaikan di rencana yang sama. Modul dilaporkan selesai hanya bila keempatnya bersih.
