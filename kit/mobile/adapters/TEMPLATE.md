# Mobile Stack Adapter — `{NAMA PROJECT}`

> **Simpan sebagai `.claude/mobile-stack.md` di root project.**
> `skill-mobile` membaca file ini di Step 0 dan berhenti kalau tidak ada.
> Isi sekali saat fork (~10 menit). Kalau ada yang berubah, update di sini —
> **jangan** mengedit SKILL.md.

Terakhir diverifikasi: `{YYYY-MM-DD}` oleh `{nama}`

---

## 0. Cara mengisi

Setiap baris punya **perintah verifikasi**. Jalankan perintahnya, tempel jawabannya.
Jangan mengisi dari ingatan — itu sumber kesalahan yang paling mahal.
Kalau sebuah baris **tidak berlaku** di project ini, tulis `TIDAK ADA` (bukan dikosongkan),
supaya skill tahu bedanya "belum diisi" dan "memang tidak ada".

---

## 0b. Ringkasan placeholder — WAJIB diisi

SKILL.md merujuk nilai-nilai ini dengan notasi `{nama}`. Tabel ini adalah lookup-nya:
isi di sini, dan agent tidak perlu menebak baris mana yang dimaksud.

| Placeholder | Nilai | Sumber |
|---|---|---|
| `{appRoot}` | `{...}` | §1 |
| `{featuresRoot}` | `{...}` | §6 |
| `{uiFolder}` | `{...}` | §6 |
| `{logicFolder}` | `{...}` | §6 |
| `{dataFolder}` | `{...}` | §6 |
| `{testFolder}` | `{...}` | §6 |
| `{stylingSystem}` | `{...}` | §8 |
| `{tokenFile}` | `{...}` | §8 |
| `{localeFiles}` | `{...}` | §9 |
| `{keyFormat}` | `{...}` | §9 |
| `{formatCmd}` | `{...}` | §10 |
| `{lintCmd}` | `{...}` | §10 |
| `{testCmd}` | `{...}` | §2 |
| `{startCmd}` | `{...}` | §2 |
| `{e2ePath}` | `{...}` | §11 |
| `{tcPath}` | `{...}` | §12 |

> Kalau sebuah placeholder tidak berlaku, tulis `TIDAK ADA` — jangan dikosongkan.

---

## 1. App mobile di project ini

Verifikasi: `ls -d */ apps/*/ 2>/dev/null` lalu cek mana yang punya `app.json`/`app.config.js`

| Label app | Root path | Peran |
|---|---|---|
| `{app-1}` | `{path/ke/app}` | `{customer / agent / dst}` |

> Kalau cuma ada satu app mobile, satu baris saja sudah cukup. Di seluruh SKILL.md,
> `{appRoot}` berarti kolom **Root path** di tabel ini.

## 2. Package manager & perintah dasar

Verifikasi: `ls | grep -E 'bun.lock|package-lock.json|yarn.lock|pnpm-lock.yaml'`

| Hal | Nilai |
|---|---|
| Package manager | `{bun / npm / yarn / pnpm}` |
| Install | `{bun install}` |
| Start Metro | `{cd {appRoot} && bun start --clear}` |
| Unit test | `{cd {appRoot} && bun run test}` |
| Typecheck | `{cd {appRoot} && bun run typecheck}` |

## 3. Routing / navigasi

Verifikasi: `grep -E '"(expo-router|@react-navigation/native)"' {appRoot}/package.json; ls -d {appRoot}/app {appRoot}/src/navigation 2>/dev/null`

| Hal | Nilai |
|---|---|
| Router | `{expo-router (file-based) / @react-navigation (stack-based)}` |
| Di mana route didefinisikan | `{path}` |
| Cara menambah screen baru | `{1–3 langkah konkret}` |
| Hook/helper navigasi | `{useRouter() / useAppNavigation()}` |
| Typed params? | `{ya — di {path} / tidak}` |

## 4. State management

Verifikasi: `grep -E '"(zustand|@reduxjs/toolkit|jotai|mobx|@tanstack/react-query)"' {appRoot}/package.json`

| Kebutuhan | Yang dipakai project ini | Lokasi |
|---|---|---|
| Auth/session state | `{...}` | `{path}` |
| Server/async state | `{...}` | `{path}` |
| Local persistence | `{...}` | `{path wrapper}` |

> **Ini yang sudah dipilih project ini, dan itu keputusan yang mengikat.**
> Skill tidak punya preferensi; mencampur dua state manager yang menangani hal
> sama = ditolak review. Mau ganti → keputusan arsitektur, tanya user dulu.

## 5. HTTP layer

Verifikasi: `grep -rl "fetch(\|axios" {appRoot}/src | head`

| Hal | Nilai |
|---|---|
| Wrapper HTTP | `{path — mis. src/services/api.ts}` |
| Signature | `{api<T>(endpoint, options)}` |
| Sudah menangani | `{timeout / refresh 401 / error toast / mock mode}` |
| Helper kode error | `{getApiErrorCode(e) dari ...}` |
| Casing payload API | `{camelCase / snake_case}` — **konsisten di seluruh payload** |

## 6. Struktur folder feature

Verifikasi: `ls {featuresRoot}; ls -R {featuresRoot}/$(ls {featuresRoot} | head -1)`

| Hal | Nilai |
|---|---|
| `{featuresRoot}` | `{path — mis. apps/mobile/src/features}` |
| Subfolder UI | `{screens / presentation / ...}` |
| Subfolder logic | `{hooks / logic / ...}` |
| Subfolder data/API | `{services / data / ...}` |
| Subfolder test | `{__tests__ / __test__ / ...}` |
| Path alias | `{@/ → {appRoot}/src/}` |

## 7. Komponen bersama

Verifikasi: `ls {appRoot}/src/components/ 2>/dev/null; grep '"@{scope}/' {appRoot}/package.json`

| Tingkat | Ada? | Lokasi | Cara melihat isinya |
|---|---|---|---|
| Lintas app (package) | `{ya/TIDAK ADA}` | `{path}` | `{perintah}` |
| Dalam satu app | `{ya/TIDAK ADA}` | `{path}` | `{perintah}` |

| Pola UI | Yang dipakai project ini | Catatan |
|---|---|---|
| Bottom sheet | `{library — mis. @gorhom/bottom-sheet}` | `{provider dipasang di mana · mock test di mana}` |
| Daftar berbasis data | `{FlatList / SectionList / FlashList}` | `{kalau ada komponen list bersama, di mana}` |
| Root wrapper screen wajib | `{nama komponen / TIDAK ADA}` | `{import path}` | |

## 8. Styling & design token

Verifikasi: `ls {appRoot}/tailwind.config.js; grep -n "colors" -A 30 {appRoot}/tailwind.config.js`

| Hal | Nilai |
|---|---|
| Sistem styling | `{NativeWind / StyleSheet / unistyles}` |
| File token | `{path}` |
| Konstanta warna non-class | `{path / TIDAK ADA}` |
| Prototype desainer | `{path / TIDAK ADA}` |

## 9. i18n

Verifikasi: `ls {appRoot}/src/i18n/ 2>/dev/null; grep -E '"(i18next|react-i18next)"' {appRoot}/package.json`

| Hal | Nilai |
|---|---|
| Library | `{i18next + react-i18next / TIDAK ADA}` |
| File locale | `{path/{id,en}.json}` |
| Locale wajib lengkap | `{id, en}` |
| Format key | `{feature.screen.element}` |

> Kalau `TIDAK ADA`: hardcoded string **tetap** bukan jawaban yang benar untuk
> project yang sudah punya user berbahasa campuran. Angkat ke user sebagai
> keputusan, jangan diputuskan sendiri di tengah task.

## 10. Lint & format

Verifikasi: `ls {appRoot}/eslint.config.* biome.json .prettierrc* 2>/dev/null; grep -n "lint-staged" -A 8 package.json`

| Tool | Memiliki | Perintah |
|---|---|---|
| `{Biome / Prettier}` | format + import order | `{bun fix}` |
| `{ESLint}` | aturan RN/hooks | `{cd {appRoot} && bun run lint}` |

| Hal | Nilai |
|---|---|
| Formatter yang **tidak** dipakai | `{mis. Prettier — dimatikan di eslint config}` |
| Pre-commit hook | `{apa yang dijalankan}` |

> **Satu formatter saja.** Menjalankan formatter yang bukan milik project ini
> membuat diff berisik yang akan berubah lagi saat commit.

## 11. Testing

Verifikasi: `grep -n "coverageThreshold" {appRoot}/jest.config.js; ls -d {appRoot}/maestro {appRoot}/e2e 2>/dev/null`

| Hal | Nilai |
|---|---|
| Unit test runner | `{jest + preset}` |
| Penempatan test | `{__tests__/ di samping kode / colocated}` |
| Coverage gate otomatis | `{ada — angka X / TIDAK ADA}` |
| E2E tool | `{Maestro / Detox / Appium / TIDAK ADA}` |
| Lokasi flow E2E | `{path}` |
| Locator E2E | `{testID / accessibilityLabel}` |

## 12. Dokumen & proses

Verifikasi: `ls docs/ apps/docs/ 2>/dev/null`

| Dokumen | Path | Dipakai untuk |
|---|---|---|
| Impl plan | `{path / TIDAK ADA}` | sumber kebenaran Tier 2/3 |
| Test case / STD | `{path / TIDAK ADA}` | assertion + testID |
| API contract | `{path / TIDAK ADA}` | nama field, status code |
| Bug report | `{path / TIDAK ADA}` | alur fix |
| ADR | `{path / TIDAK ADA}` | keputusan arsitektur |

| Hal | Nilai |
|---|---|
| Ada alur triage bug formal? | `{ya — status: ... / tidak}` |
| Ke mana bug backend di-route | `{path / TIDAK ADA}` |

## 13. Larangan khusus project ini

Hal yang **spesifik** project ini dan tidak tertangkap aturan umum. Kosongkan kalau tidak ada.

- `{mis. jangan pakai AsyncStorage untuk token — pakai wrapper SecureStore di ...}`
- `{mis. jangan jalankan Metro dua app bersamaan — cache NativeWind bentrok}`
