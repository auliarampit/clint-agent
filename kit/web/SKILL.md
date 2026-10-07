---
name: skill-web
description: >
  Use this skill whenever implementing or changing anything in a web frontend app in this repo:
  pages, routes, layouts, components, forms, tables, data fetching, state, styling, i18n,
  accessibility, performance, or tests. Stack-agnostic: reads the project's own stack facts from
  `.claude/web-stack.md` and verifies inventory against the filesystem instead of assuming a
  framework, router, styling system, or folder layout. Deeper guidance lives in `referensi/` and
  is read only when the task touches that topic. Do NOT trigger for: backend, mobile apps, or
  docs-only changes.
---

# Skill Web (inti portable)

> **Prioritas mutlak — 4 prinsip kerja.** Logika sederhana, jangan over code · bingung → tanya ·
> ikuti semua aturan (`CLAUDE.md`, `.claude/rules/`, skill, adapter) · review hasil terhadap docs atau
> permintaan sebelum menyatakan selesai.

> **Konvensi diikuti, inventaris diverifikasi.** File ini hanya berisi konvensi yang stabil lintas
> project. Nama framework, library, path, dan isi config ada di adapter. Kesimpulan negatif dari
> ingatan ("komponen X belum ada", "route Y tidak ada") wajib dibuktikan dengan perintah sebelum
> membuat yang baru. Kalau menemukan nama library atau path konkret di file ini, itu bug.

Notasi `{...}` = ambil dari adapter (`{appRoot}`, `{featuresRoot}`, `{lintCmd}`, dan seterusnya).

---

## Step 0 — Baca adapter (WAJIB)

```bash
cat .claude/web-stack.md
```

- Tidak ada → **berhenti**. Tawarkan `/clint:siapkan-project web` (atau salin
  `kit/web/adapters/TEMPLATE.md` dari clint). Jangan menebak stack dari nama folder.
- Bertentangan dengan filesystem → **filesystem menang**; sebutkan bahwa adapter perlu diperbarui.
- Monorepo dengan beberapa app web → pastikan app mana yang disentuh task ini (adapter §1).

## Step 1 — Klasifikasi task

| Tipe | Ciri | Jalur |
|---|---|---|
| **Kecil** | styling saja, teks/i18n, satu prop, `data-testid` | Fast path: Step 0, Step 3, lalu Step 9 |
| **Fitur** | layar/komponen/alur baru | Semua langkah |
| **Perbaikan bug** | perilaku salah | Step 2 → reproduksi → test gagal dulu → perbaiki → Step 9 |
| **Refactor** | tanpa perubahan perilaku | Test yang ada harus lulus sebelum dan sesudah; scope tidak melebar |

Referensi yang dibaca **hanya bila task menyentuhnya**:

| Task menyentuh | Baca |
|---|---|
| elemen interaktif, form, dialog, navigasi, warna | `.claude/skills/skill-web/referensi/aksesibilitas.md` |
| daftar besar, gambar, data fetching, bundle, render ulang | `.claude/skills/skill-web/referensi/performa.md` |
| input pengguna yang dirender, auth, token, URL eksternal, upload | `.claude/skills/skill-web/referensi/keamanan.md` |
| form, tabel, paginasi, filter, dialog, toast, upload, wizard | `.claude/skills/skill-web/referensi/pola.md` |

## Step 2 — Baca sebelum menulis (seperlunya)

1. Requirement: hanya bagian yang relevan dari PRD/STD/API contract (cari dengan `grep -n`).
2. Desain: layar yang sesuai di prototype/desain (adapter §12). Ukuran, warna, dan jarak diambil dari
   nilai literal di desain, bukan ditebak dari gambar.
3. Kode: feature terdekat yang sudah ada sebagai contoh pola; ikuti polanya.

## Step 3 — Pakai yang sudah ada dulu

Urutan sebelum membuat sesuatu yang baru:

1. Komponen dari library/design system project (adapter §7).
2. Komponen bersama di app (adapter §7).
3. Komponen feature lain yang sama persis → **angkat** ke lokasi bersama pada pemakaian kedua, jangan
   disalin.
4. Baru membuat komponen baru.

Hal yang sama untuk hook/composable, util format (tanggal, uang, angka), dan klien HTTP.

## Step 4 — Struktur feature

```
{featuresRoot}/{feature}/
  {uiFolder}       komponen tampilan: menerima data, memanggil handler, tanpa logika bisnis
  {logicFolder}    state, hook/composable, aturan bisnis murni (bisa dites tanpa render)
  {dataFolder}     pemanggilan API, pemetaan payload ↔ model, kunci cache
  {testFolder}     atau berdampingan dengan file yang dites, sesuai adapter
```

Nama dan bentuk lokasi (folder atau satu file, mis. satu file API per feature) **mengikuti adapter
§6 dan feature yang sudah ada**, bukan bagan di atas. Yang wajib adalah pemisahan perannya.

- Route/page **tipis**: memilih data dan layout, lalu menyerahkan ke komponen feature.
- Arah dependensi: `ui → logic → data`. Data tidak pernah mengimpor UI.
- Satu feature tidak mengimpor isi internal feature lain; bila butuh, angkat ke lokasi bersama.

## Step 5 — Pisahkan logika dari tampilan

- Komponen tampilan tanpa `fetch`/klien HTTP langsung, tanpa akses storage, tanpa aturan bisnis.
- Kondisi kompleks (> 1 operator logika, atau dipakai > 1 kali) diekstrak menjadi nama yang
  menjelaskan maksud (`const canSubmit = ...`), lalu diuji di `{logicFolder}`.
- State turunan **dihitung**, tidak disimpan ganda.
- Efek samping (langganan, timer, listener) selalu punya pembersihan.

## Step 6 — Render: server vs klien

Ikuti model render project (adapter §3: SPA, SSR, atau komponen server).

- Bila framework mendukung render di server: ambil data di server secara default; jadikan komponen
  interaktif sekecil mungkin di sisi klien. Jangan menandai seluruh halaman sebagai klien hanya karena
  satu tombol.
- Rahasia dan token server **tidak pernah** masuk kode yang dikirim ke browser. Variabel lingkungan
  publik hanya yang memang boleh dilihat pengguna (aturan prefix di adapter §5).
- Setiap halaman punya judul dan metadata yang benar (adapter §3).

## Step 7 — Data dan state

- Satu mekanisme per kebutuhan, sesuai adapter §4: server state lewat lapisan cache yang dipilih
  project; state UI lokal di komponen; state global hanya untuk yang benar-benar lintas halaman.
  Mencampur dua mekanisme untuk hal yang sama = ditolak review.
- Semua HTTP lewat klien project (adapter §5). Kunci cache didefinisikan di `{dataFolder}`, bukan di
  komponen.
- Setiap pengambilan data menangani empat keadaan: **loading, error, kosong, berisi**. Kosong ≠ error.
- Error dari API dipetakan ke pesan pengguna lewat satu pemetaan; jangan menampilkan pesan mentah.
- Mutasi: nonaktifkan pemicu selama berjalan (cegah kirim ganda), lalu invalidasi atau perbarui cache
  yang terdampak. Optimistic update hanya bila rollback-nya jelas.
- URL adalah state: filter, halaman, tab, dan pencarian yang perlu bisa dibagikan disimpan di query
  string, bukan hanya di state komponen.

## Step 8 — Styling, i18n, dan penanda test

**Styling** (adapter §8):
- Warna, jarak, radius, bayangan, dan tipografi selalu dari token/design system; tidak ada nilai hex
  atau piksel acak.
- Tidak ada style inline statis. Kelas kondisional lewat util penggabung kelas project.
- Responsif dirancang dari lebar ponsel; tidak ada scroll horizontal pada halaman.
- Mode gelap (bila project mendukung) diuji, bukan diasumsikan.

**i18n** (adapter §9): semua teks yang dilihat pengguna lewat fungsi terjemahan dengan format key
project; tidak ada string keras. Format tanggal, angka, dan mata uang lewat util locale.

**Penanda test** (adapter §11): elemen interaktif dan elemen yang di-assert punya penanda test dengan
format project. Jangan mengganti nama penanda yang sudah ada tanpa memperbarui test-nya.

## Step 9 — Selesai berarti

```bash
{lintCmd} && {typecheckCmd} && {testCmd}
```

Semua lulus, lalu periksa:

- [ ] Setiap poin permintaan/requirement terpenuhi; tidak ada tambahan di luar scope.
- [ ] Empat keadaan data (loading/error/kosong/berisi) tertangani di layar yang disentuh.
- [ ] Bisa dioperasikan dengan keyboard, fokus terlihat, label lengkap (`.claude/skills/skill-web/referensi/aksesibilitas.md`).
- [ ] Tidak ada teks keras, warna acak, style inline statis, `fetch` langsung di komponen.
- [ ] Test baru menguji perilaku, bukan detail implementasi; bug fix punya test yang tadinya gagal.
- [ ] Yang belum dikerjakan atau belum terverifikasi dilaporkan apa adanya.

---

## Larangan absolut (semua project)

- Logika bisnis di komponen tampilan · HTTP/storage langsung di komponen.
- String keras untuk pengguna · warna/ukuran di luar token · style inline statis.
- Merender HTML dari input pengguna tanpa sanitasi · rahasia di kode klien.
- Elemen klik tanpa semantik tombol/tautan · gambar informatif tanpa teks alternatif.
- Menelan error tanpa tampilan ke pengguna · loading tanpa batas waktu/penanganan gagal.
- Menambah library baru tanpa persetujuan user (itu keputusan arsitektur).
- Melonggarkan aturan lint atau assertion test supaya lulus.

## Kapan berhenti dan bertanya (hanya pertanyaan teknis)

- Adapter dan filesystem bertentangan soal hal yang menentukan arsitektur.
- Task butuh library baru, mengganti mekanisme state, atau mengubah struktur route bersama.
- Requirement bertentangan dan dokumen tidak bisa memutuskan (cek prototype dan API contract dulu).
- Perubahan menyentuh auth, izin, atau data pribadi di luar yang disebut task.
