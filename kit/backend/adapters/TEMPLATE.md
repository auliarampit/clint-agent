# Backend Stack Adapter — `{NAMA PROJECT}`

> Simpan sebagai `.claude/backend-stack.md`. `skill-backend` membacanya di Step 0 dan berhenti bila tidak
> ada. Setiap baris punya **perintah verifikasi**: jalankan, tempel hasilnya, jangan mengisi dari ingatan.
> Baris yang tidak berlaku ditulis `TIDAK ADA`.

Terakhir diverifikasi: `{YYYY-MM-DD}` oleh `{nama}`

## 0. Ringkasan placeholder

| Placeholder | Nilai | Sumber |
|---|---|---|
| `{serviceRoot}` | | §1 |
| `{modulesRoot}` · `{transportLayer}` · `{domainLayer}` · `{dataLayer}` · `{testLocation}` | | §3 |
| `{lintCmd}` · `{typecheckCmd}` · `{testCmd}` · `{formatCmd}` | | §2, §10 |
| `{migrateCmd}` · `{newMigrationCmd}` | | §5 |

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

## 11. Testing

| Hal | Nilai |
|---|---|
| Unit test runner | |
| Integrasi: database test (container/instans test) + perintah | |
| Factory/fixture data | |
| Test kontrak | ya/TIDAK ADA |

## 12. Dokumen

| Dokumen | Path |
|---|---|
| API contract (OpenAPI/lainnya) | |
| PRD / SAD / STD / ADR / rencana | |

## 13. Larangan khusus project ini

- …
