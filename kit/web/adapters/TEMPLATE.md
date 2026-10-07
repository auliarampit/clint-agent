# Web Stack Adapter — `{NAMA PROJECT}`

> Simpan sebagai `.claude/web-stack.md`. `skill-web` membacanya di Step 0 dan berhenti bila tidak ada.
> Setiap baris punya **perintah verifikasi**: jalankan, tempel hasilnya, jangan mengisi dari ingatan.
> Baris yang tidak berlaku ditulis `TIDAK ADA`.

Terakhir diverifikasi: `{YYYY-MM-DD}` oleh `{nama}`

## 0. Ringkasan placeholder

| Placeholder | Nilai | Sumber |
|---|---|---|
| `{appRoot}` | | §1 |
| `{featuresRoot}` · `{uiFolder}` · `{logicFolder}` · `{dataFolder}` · `{testFolder}` | | §6 |
| `{lintCmd}` · `{typecheckCmd}` · `{testCmd}` · `{formatCmd}` | | §2, §10 |
| `{e2eCmd}` · `{e2ePath}` | | §11 |

## 1. App web di project ini

Verifikasi: `ls -d */ apps/*/ 2>/dev/null` lalu cari file config framework di tiap app.

| Label | Root path | Peran (admin / publik / dashboard) | Port dev |
|---|---|---|---|

## 2. Package manager & perintah

Verifikasi: `ls *.lock* package-lock.json 2>/dev/null; jq .scripts {appRoot}/package.json`

| Hal | Perintah |
|---|---|
| Install / dev / build | |
| Lint / typecheck / unit test | |

## 3. Framework, routing, render

Verifikasi: `jq '.dependencies' {appRoot}/package.json`; lihat folder route.

| Hal | Nilai |
|---|---|
| Framework + versi | |
| Model render | SPA / SSR / komponen server + klien |
| Lokasi route/page dan cara menambah halaman | |
| Penanda komponen klien (bila ada) | |
| Metadata halaman (judul, SEO) diatur di | |
| Halaman error/404/loading bawaan | |

## 4. Data, state, form

| Kebutuhan | Yang dipakai | Lokasi |
|---|---|---|
| Server state / cache | | |
| State global UI | | |
| Form + validasi skema | | |
| Auth/sesi di klien | | |

> Ini pilihan project dan mengikat. Mencampur dua mekanisme untuk hal yang sama ditolak review.

## 5. HTTP & lingkungan

| Hal | Nilai |
|---|---|
| Klien HTTP + path | |
| Penanganan error/401/refresh | |
| Pemetaan kode error → pesan | |
| Prefix variabel lingkungan publik | |
| Casing payload API | |

## 6. Struktur folder feature

Verifikasi: `ls {featuresRoot}; ls -R {featuresRoot}/$(ls {featuresRoot} | head -1)`

| Hal | Nilai |
|---|---|
| `{featuresRoot}` | |
| Subfolder UI / logic / data / test | |
| Path alias | |

## 7. Komponen bersama & design system

| Tingkat | Lokasi | Cara melihat isinya |
|---|---|---|
| Library/design system | | |
| Komponen bersama app | | |
| Ikon | | |

| Pola | Komponen yang dipakai |
|---|---|
| Dialog / toast / tabel / form field / dropdown | |

## 8. Styling & token

| Hal | Nilai |
|---|---|
| Sistem styling | |
| File token (warna, jarak, tipografi) | |
| Util penggabung kelas | |
| Mode gelap | ya/TIDAK ADA |
| Breakpoint | |

## 9. i18n

| Hal | Nilai |
|---|---|
| Library + file locale | |
| Locale wajib lengkap | |
| Format key | |
| Util tanggal/angka/uang | |

## 10. Lint & format

| Tool | Perintah | Catatan |
|---|---|---|

Satu formatter saja; formatter yang **tidak** dipakai: …

## 11. Testing

| Hal | Nilai |
|---|---|
| Unit/komponen test runner + lokasi | |
| E2E tool + lokasi + perintah | |
| Format penanda test | |
| Fixture login / seed data | |
| Pemeriksa aksesibilitas otomatis | ya/TIDAK ADA |
| Analisis bundle / audit performa | ya/TIDAK ADA |

## 12. Dokumen & desain

| Dokumen | Path |
|---|---|
| PRD / STD / API contract / rencana | |
| Desain / prototype | |

## 13. Keamanan & deploy

| Hal | Nilai |
|---|---|
| Header keamanan / CSP diatur di | |
| Penyimpanan token sesi | |
| Sanitizer HTML (bila ada) | |

## 14. Larangan khusus project ini

- …
