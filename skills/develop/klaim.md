# Status di menu bar dan klaim PR

Dipakai `develop`, `test`, dan `docs`.

File status **per sesi** `~/Library/Logs/clint/kerja/<sid>.json`. Tulis saat PR dipilih (klaim), setiap ganti
PR/tahap, dan hapus di akhir, termasuk bila berhenti karena gagal (murah, satu perintah):
```bash
mkdir -p ~/Library/Logs/clint/kerja && printf '%s' '{"dir":"<repo utama absolut>","rencana":"docs/plans/mob-10.md","prs":["PR-2","PR-3"],"perintah":"/clint:develop docs/plans/mob-10.md PR-2,PR-3","path":"<path kerja>","judul":"develop MOB-10","mulai":"11.21","pr":2,"total":3,"label":"PR-2/3","tahap":"ditinjau code-reviewer","catatan":"PR-1 → MR !127 · PR-3 menunggu"}' > ~/Library/Logs/clint/kerja/<sid>.json
```
`dir` = repo utama (bukan worktree): `dirname "$(git rev-parse --path-format=absolute --git-common-dir)"`.
`rencana` = path relatif rencana, `null` bila tanpa rencana. `perintah` = perintah clint persis seperti diketik user
(dipakai untuk membuang saran yang sama di sesi lain); sebut juga ID butir (FB-/BUG-/MR-MOB-...) di `judul`. `prs` = PR yang **masih** dipegang sesi ini; PR yang
sudah jadi MR dikeluarkan dari `prs` supaya sesi lain bisa melanjutkan PR sesudahnya. `label` pendek (tampil di
sebelah ikon); tugas tunggal `"pr":1,"total":1`. Akhir run: `rm -f ~/Library/Logs/clint/kerja/<sid>.json`.

Bila tugas berasal dari butir laporan `status` (feedback, bug, temuan), setelah MR terverifikasi pindahkan
butir itu ke "menunggu review" supaya badge menu bar ikut berkurang (tanpa token):
`python3 "$R/scripts/update-report.py" review "<ID/teks butir>" "MR !<n>" "<url MR>" --proyek <nama project>`
Itu hanya badge menu bar. **Status di tracker docs juga wajib ditulis**: panggil `tech-writer` (jalur skill `docs`,
status butir feedback/bug) untuk memperbarui butir itu di `docs.feedback` repo docs **utama**, bukan salinan di
worktree, supaya PM tidak masih melihat Open. Isi: status (menunggu review + tautan MR), hasil verifikasi jalur
persis laporan (sumber gambar, tombol, perangkat; sebelum dan sesudah), dan centang Definition of Done project
(bila ada di dokumen QA/STD: test, E2E, review, deskripsi MR). Jalur yang belum terverifikasi ditulis "belum
terverifikasi", bukan fix; jangan menyatakan "sudah fix" di laporan sebelum verifikasinya lulus.

Tindak lanjut yang tidak menghasilkan MR baru (mis. perbaikan di MR yang sama) → `... selesai "<ID/teks>"`.

