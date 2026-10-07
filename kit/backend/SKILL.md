---
name: skill-backend
description: >
  Use this skill whenever implementing or changing anything in a backend service or API in this repo:
  endpoints, modules, domain logic, database schema and migrations, queries, auth and permissions,
  background jobs, integrations, events, caching, or tests. Stack-agnostic: reads the project's own
  stack facts from `.claude/backend-stack.md` and verifies inventory against the filesystem instead of
  assuming a runtime, framework, ORM, or database. Deeper guidance lives in `referensi/` and is read
  only when the task touches that topic. Do NOT trigger for: web or mobile frontends, or docs-only changes.
---

# Skill Backend (inti portable)

> **Prioritas mutlak — 4 prinsip kerja.** Logika sederhana, jangan over code · bingung → tanya ·
> ikuti semua aturan (`CLAUDE.md`, `.claude/rules/`, skill, adapter) · review hasil terhadap docs atau
> permintaan sebelum menyatakan selesai.

> **Konvensi diikuti, inventaris diverifikasi.** File ini hanya berisi konvensi yang stabil lintas
> project. Nama framework, ORM, database, broker, dan path ada di adapter. Kesimpulan "endpoint/tabel/
> modul belum ada" wajib dibuktikan dengan perintah sebelum membuat yang baru.

Notasi `{...}` = ambil dari adapter. Referensi ada di `.claude/skills/skill-backend/referensi/`.

---

## Step 0 — Baca adapter (WAJIB)

```bash
cat .claude/backend-stack.md
```

Tidak ada → **berhenti**, tawarkan `/clint:siapkan-project backend`. Bertentangan dengan filesystem →
filesystem menang; sebutkan bahwa adapter perlu diperbarui. Monorepo → pastikan service mana yang disentuh.

## Step 1 — Klasifikasi task

| Tipe | Jalur |
|---|---|
| **Kecil** (pesan error, validasi tambahan, field opsional) | Step 0, 3, 5, lalu Step 10 |
| **Endpoint/fitur** | Semua langkah |
| **Skema/migrasi** | Wajib `referensi/data.md`; Step 6 diperlakukan sebagai titik risiko tertinggi |
| **Perbaikan bug** | Reproduksi dengan test yang gagal dulu → perbaiki → Step 10 |
| **Refactor** | Test yang ada lulus sebelum dan sesudah; kontrak API tidak berubah |

| Task menyentuh | Baca |
|---|---|
| endpoint baru/berubah, bentuk respons, error, paginasi | `referensi/kontrak-api.md` |
| skema, migrasi, query, transaksi, indeks | `referensi/data.md` |
| auth, izin, input, upload, rate limit, data pribadi | `referensi/keamanan-api.md` |
| panggilan layanan luar, job, event, cache, logging | `referensi/keandalan.md` |

## Step 2 — Kontrak dulu, kode kemudian

1. **API contract adalah sumber kebenaran** (adapter §12). Nama field, tipe, status code, dan bentuk
   error mengikuti kontrak, bukan selera. Kontrak dan permintaan bertentangan → tanya, jangan memilih
   diam-diam.
2. Requirement terkait: hanya bagian relevan dari PRD/SAD/STD (cari dengan `grep -n`).
3. Modul terdekat yang sudah ada sebagai contoh pola; ikuti polanya.

## Step 3 — Pakai yang sudah ada dulu

Middleware auth/izin, validator, pembungkus error, klien HTTP keluar, util paginasi, logger, dan
helper transaksi project (adapter §4–§9) dipakai ulang, bukan ditulis ulang. Kode yang sama di dua
modul → angkat ke lokasi bersama pada pemakaian kedua.

## Step 4 — Lapisan modul

```
{modulesRoot}/{modul}/
  {transportLayer}   route/controller/handler: parse + validasi input, panggil use case, bentuk respons
  {domainLayer}      use case/service + aturan bisnis murni (bisa dites tanpa HTTP dan database)
  {dataLayer}        repository/akses data: query, pemetaan baris ↔ entitas
  {testLocation}
```

Nama dan bentuk lokasi mengikuti adapter §3 dan modul yang sudah ada. Banyak project tidak memisahkan
repository (service memanggil ORM langsung); itu sah bila adapter mencatatnya, dan **jangan dirombak**.
Yang wajib di semua bentuk:

- Transport **tipis**: tidak ada aturan bisnis dan tidak ada query di handler/controller.
- Lapisan domain/service tidak mengimpor framework HTTP (request/response).
- Aturan bisnis yang tidak sepele (perhitungan, transisi status, kelayakan) diekstrak menjadi fungsi
  murni yang bisa dites tanpa HTTP dan tanpa database, walaupun service-nya memanggil ORM.
- Satu modul tidak mengakses tabel/repository internal modul lain secara langsung; gunakan antarmuka
  publik modul itu atau event.

## Step 5 — Validasi dan bentuk respons

- Semua input (body, query, params, header yang dipakai) divalidasi dengan skema di batas transport;
  tolak field tak dikenal atau abaikan secara eksplisit (cegah mass assignment).
- Respons dibentuk lewat DTO/serializer eksplisit; **tidak pernah** mengembalikan entitas database mentah
  (bocor field internal/sensitif).
- Error memakai envelope dan kode error project (adapter §7); satu kode error = satu arti. Status code
  sesuai kontrak (400 validasi, 401 belum login, 403 tidak berizin, 404 tidak ada/tidak boleh tahu,
  409 konflik, 422 aturan bisnis bila project memakainya).
- Daftar selalu berpaginasi dengan batas maksimum ukuran halaman.

## Step 6 — Data dan migrasi

- Perubahan skema **hanya lewat migrasi** (perintah adapter §5), tidak pernah mengubah database manual.
- Migrasi aman untuk data yang sudah ada dan untuk deploy bertahap: tambah dulu, pindahkan data,
  baru hapus di rilis berikutnya. Tidak ada operasi yang mengunci tabel besar lama tanpa rencana.
- Beberapa penulisan yang harus konsisten → satu transaksi. Efek samping keluar (email, event, HTTP)
  tidak dijalankan di dalam transaksi yang bisa gagal; gunakan pola outbox bila project memakainya.
- Tidak ada query di dalam loop (N+1); ambil sekaligus. Kolom yang dipakai filter/urut/join diberi indeks.
- Waktu disimpan dalam UTC; uang tidak memakai tipe float.

## Step 7 — Keamanan (default tolak)

- Setiap endpoint **wajib** terautentikasi kecuali kontrak menyatakan publik.
- Otorisasi per objek: pastikan objek milik/terjangkau pemanggil sebelum membaca/mengubah (BOLA),
  dan per fungsi untuk aksi admin (BFLA). Menyembunyikan tombol di klien bukan otorisasi.
- Rahasia hanya dari konfigurasi terkelola, tidak di kode, log, atau respons error.
- Query selalu berparameter; tidak ada penggabungan string ke query/perintah shell.
- Endpoint mahal atau sensitif (login, OTP, reset sandi, ekspor) punya pembatas laju.

## Step 8 — Error dan observability

- Error tidak ditelan: tangani di tempat yang bisa mengambil keputusan, sisanya biarkan naik ke
  penanganan global yang memetakan ke envelope error.
- Log terstruktur dengan ID korelasi permintaan; level sesuai (error hanya untuk yang perlu tindakan).
- **Tidak mencatat** token, sandi, OTP, data pribadi lengkap, atau isi body sensitif.

## Step 9 — Integrasi, job, event

Setiap panggilan keluar punya timeout; retry hanya untuk operasi idempoten dengan backoff. Job dan
consumer event idempoten (aman dijalankan dua kali). Detail di `referensi/keandalan.md`.

## Step 10 — Selesai berarti

```bash
{lintCmd} && {typecheckCmd} && {testCmd}
```

- [ ] Implementasi sesuai API contract (field, status code, error); tidak ada perubahan merusak tanpa keputusan.
- [ ] Input divalidasi, respons lewat DTO, otorisasi per objek diterapkan.
- [ ] Migrasi bisa dijalankan pada data yang ada; transaksi dan indeks sesuai kebutuhan query.
- [ ] Test: aturan bisnis (unit) + endpoint/repository (integrasi, adapter §11) + kasus error utama.
- [ ] Tidak ada rahasia/data pribadi di log; panggilan keluar punya timeout.
- [ ] Yang belum dikerjakan atau belum terverifikasi dilaporkan apa adanya.

---

## Larangan absolut (semua project)

- Aturan bisnis atau query di handler · entitas database mentah sebagai respons.
- Endpoint tanpa autentikasi/otorisasi yang tidak disebut publik oleh kontrak.
- Query/perintah dari penggabungan string · rahasia atau data pribadi di kode dan log.
- Mengubah skema tanpa migrasi · migrasi yang menghapus kolom/data yang masih dibaca kode yang berjalan.
- Mengubah kontrak API (field, tipe, status) diam-diam · menelan error.
- Menambah dependensi/infrastruktur baru (database, broker, cache) tanpa persetujuan user.
- Melonggarkan validasi, aturan lint, atau assertion test supaya lulus.

## Kapan berhenti dan bertanya (hanya pertanyaan teknis)

- Kontrak dan permintaan bertentangan, atau perubahan akan merusak klien yang sudah ada.
- Migrasi berisiko pada data produksi (hapus/ubah tipe kolom, tabel besar) tanpa rencana tertulis.
- Butuh infrastruktur atau dependensi baru, atau mengubah mekanisme auth.
- Aturan izin untuk aksi baru tidak tertulis di dokumen.
