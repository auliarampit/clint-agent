# Backend Stack Adapter — `{NAMA PROJECT}`

> Simpan sebagai `.claude/backend-stack.md`. `skill-backend` membacanya di Step 0 dan berhenti bila tidak
> ada. Setiap baris punya **perintah verifikasi**: jalankan, tempel hasilnya, jangan mengisi dari ingatan.
> Baris yang tidak berlaku ditulis `TIDAK ADA`.
> **Batas: ≤ 300 baris / 25 KB.** Adapter berisi fakta stack, bukan jurnal. Catatan keputusan per modul,
> riwayat perbaikan, dan log selisih desain ditulis di ADR atau file rencana; adapter cukup menautkannya.

Terakhir diverifikasi: `{YYYY-MM-DD}` oleh `{nama}`

## 0. Ringkasan placeholder

| Placeholder | Nilai | Sumber |
|---|---|---|
| `{serviceRoot}` | | §1 |
| `{modulesRoot}` · `{transportLayer}` · `{domainLayer}` · `{dataLayer}` · `{testLocation}` | | §3 |
| `{lintCmd}` · `{typecheckCmd}` · `{testCmd}` · `{formatCmd}` | | §2, §10 |
| `{migrateCmd}` · `{newMigrationCmd}` | | §5 |

Baris WAJIB di §10 (gerbang mesin) dan §11 (harness ukur) juga wajib diisi (`quality-gates.md` §1–§2).

## 1. Service di project ini

Verifikasi: `ls -d */ apps/*/ services/*/ 2>/dev/null` lalu cari entry point server.

| Label | Root path | Peran | Port dev |
|---|---|---|---|

## 2. Runtime, framework, perintah

Verifikasi: file manifest/lock dan skrip.

| Hal | Nilai |
|---|---|
| Bahasa + runtime + versi | |
| Framework HTTP | |
| Install / dev / build / start | |
| Lint / typecheck / test | |

## 3. Arsitektur dan lokasi modul

Verifikasi: `ls {modulesRoot}; find {modulesRoot}/<modul-contoh> -maxdepth 2` (pilih modul yang matang)

| Hal | Nilai |
|---|---|
| `{modulesRoot}` | |
| Lapisan transport / domain / data (folder atau file) | |
| Ada lapisan repository terpisah, atau service memanggil ORM langsung? | |
| Lokasi test (folder sendiri / berdampingan) | |
| Cara mendaftarkan modul/route baru | |
| Path alias | |

## 4. Validasi & DTO

| Hal | Nilai |
|---|---|
| Library skema validasi + lokasi skema | |
| Pola DTO/serializer respons | |
| Tipe bersama dengan frontend (package/generator) | |

## 5. Database & migrasi

| Hal | Nilai |
|---|---|
| Database + versi | |
| ORM / query builder | |
| Lokasi skema dan migrasi | |
| Buat migrasi / jalankan migrasi | |
| Helper transaksi | |
| Kebijakan hapus (soft/hard) dan data pribadi | |

## 6. Auth & izin

| Hal | Nilai |
|---|---|
| Mekanisme autentikasi (token/sesi) | |
| Guard/middleware auth + lokasi | |
| Model izin (peran/permission) + cara mengecek | |
| Endpoint publik yang disengaja | |

## 7. Kontrak, error, konvensi respons

| Hal | Nilai |
|---|---|
| Envelope error + lokasi daftar kode error | |
| Casing field JSON | |
| Pola paginasi (offset/kursor) + batas | |
| Strategi versi API | |

## 8. Integrasi, job, event, cache

| Hal | Nilai |
|---|---|
| Klien HTTP keluar (timeout, retry) | |
| Antrean/job + lokasi worker | |
| Broker/event + pola outbox | |
| Cache | |

## 9. Konfigurasi & observability

| Hal | Nilai |
|---|---|
| Validasi variabel lingkungan | |
| Logger + format + ID korelasi | |
| Metrik/trace | |
| Endpoint kesehatan | |

## 10. Lint, format, quality gate

| Tool | Perintah | Catatan |
|---|---|---|

**Gerbang mesin wajib** (`.claude/rules/quality-gates.md` §1). Semua baris WAJIB diisi; dijalankan oleh
skrip lint supaya ikut `ciOnMr`. Ditolak user → `TIDAK ADA (ditolak <tanggal>, <alasan>)`.

Verifikasi: `grep -n -E "sonarjs|jscpd|knip|no-restricted-(paths|imports)|dependency-cruiser|audit|glossary" package.json eslint.config.* .jscpd.json knip.json 2>/dev/null`

| Gerbang | Perintah / config |
|---|---|
| Rule Sonar (`eslint-plugin-sonarjs` atau job sonar MR) | `{config / TIDAK ADA (ditolak <tanggal>)}` |
| Duplikasi ≤ 3% (`jscpd --min-tokens 50 --threshold 3`) | `{perintah / TIDAK ADA (ditolak <tanggal>)}` |
| Kode mati (`knip` atau padanan bahasa) | `{perintah / TIDAK ADA (ditolak <tanggal>)}` |
| Batas lapisan (controller/transport tidak mengimpor repository/ORM langsung; modul tidak mengimpor internal modul lain) | `{rule + lokasi / TIDAK ADA (ditolak <tanggal>)}` |
| Audit dependensi (`<pm> audit --audit-level=high`) | `{perintah / TIDAK ADA (ditolak <tanggal>)}` |
| Glosarium istilah terlarang (`docs/glossary.md`) | `{perintah grep / TIDAK ADA}` |

## 11. Testing

| Hal | Nilai |
|---|---|
| Unit test runner | |
| Integrasi: database test (container/instans test) + perintah | |
| Factory/fixture data | |
| Test kontrak | ya/TIDAK ADA |
| Pengukuran performa (APM, log timing, load test mis. k6/Artillery + perintah) | ya/TIDAK ADA |
| Harness: uji beban endpoint panas p50/p95/p99 + galat (WAJIB) | perintah + daftar endpoint |
| Harness: RSS/heap setelah 10.000 permintaan (WAJIB) | perintah + ambang (default < 10%) |
| Harness: `EXPLAIN` query jalur panas (WAJIB) | perintah |
| Lingkungan acuan (CPU, RAM, data volume) | |
| Dokumen angka | `docs/performa/baseline.md` |
| Target performa khusus project | hanya bila lebih ketat dari `references/performance.md` / TIDAK ADA |

## 12. Dokumen

| Dokumen | Path |
|---|---|
| API contract (OpenAPI/lainnya) | |
| PRD / SAD / STD / ADR / rencana | |

## 13. Larangan khusus project ini

- …
