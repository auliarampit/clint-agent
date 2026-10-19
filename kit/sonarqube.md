# SonarQube — tulis kode yang lolos quality gate sejak awal

> **Portable.** Berlaku untuk setiap project yang dianalisis SonarQube (ada `sonar-project.properties`
> atau job `sonar` di CI). Standar Badr: quality gate memblokir merge, jadi kode yang tidak lolos sama
> dengan kode yang belum selesai.

## 1. Quality gate (kode baru)

Ambang diambil dari quality gate project (tanya admin Sonar bila perlu). Tidak diketahui → pakai
default **Sonar way** di bawah, yang juga dipakai project Badr:

| Syarat | Ambang | Cara memenuhi |
|---|---|---|
| Bug & vulnerability baru | 0 (rating A) | ikuti bagian 2–4 |
| Security hotspot | 100% ditinjau | jangan menambah hotspot tanpa alasan (bagian 4); yang memang perlu → sebut di laporan |
| Code smell (maintainability) | rating A | ikuti bagian 2–3 |
| Coverage kode baru | ≥ 80% | test untuk setiap logika baru (bagian 5) |
| Duplikasi kode baru | ≤ 3% | pakai ulang yang sudah ada; jangan menyalin blok |

## 2. Aturan umum (semua bahasa)

- **Cognitive complexity ≤ 15 per fungsi** (S3776). Lewat → early return, ekstrak helper, lookup map.
  Jangan dibungkam; ubah strukturnya dan pertahankan perilaku.
- Tanpa `TODO`/`FIXME` (S1135) dan kode yang dikomentari (S125) saat merge.
- Tanpa import, variabel, parameter, atau fungsi yang tidak dipakai.
- Tanpa blok/fungsi kosong dan `catch` yang menelan error; tangani atau teruskan.
- Maksimal 7 parameter per fungsi (S107); lebih → satu objek parameter.
- Tanpa kredensial, token, atau URL rahasia di kode (S2068); ambil dari konfigurasi/env.
- Tanpa nilai ajaib berulang; jadikan konstanta bernama.

## 3. TypeScript / JavaScript / React

Diurutkan dari yang paling sering gagal di project Badr (🔴 = tidak ditangkap linter biasa, wajib
diingat):

| Rule | Salah | Benar |
|---|---|---|
| 🔴 S6759 props read-only | `type Props = { id: string }` | `type Props = Readonly<{ id: string }>` |
| S3358 ternary bertingkat | `a ? b : c ? d : e` | lookup map / early return di helper |
| S6478 komponen di dalam komponen | `function Row()` di badan `Page` | pindah ke level modul |
| 🔴 S7781 `replaceAll` | `s.replace(/-/g, '_')` | `s.replaceAll('-', '_')` |
| 🔴 S7764 `globalThis` | `window.location` | `globalThis.location` |
| S6479 index sebagai `key` | `key={i}` | `key={item.id}` |
| 🔴 S6564 / `any` | `type Raw = any`, `x: any` | tipe sebenarnya, atau `unknown` + narrowing |
| 🔴 S4325 assertion tidak perlu | `value as string` (sudah string), `!` | hapus |
| S6582 optional chaining | `a && a.b()` | `a?.b()` |
| 🔴 S4624 template bertingkat | `` `${a} ${`${b}`}` `` | ekstrak ke variabel |
| 🔴 S7776 `Set` untuk keanggotaan | `ARR.includes(x)` (konstanta) | `new Set([...]).has(x)` |
| 🔴 S6754 destructure `useState` | `const s = useState(0)` | `const [count, setCount] = useState(0)` |
| 🔴 promise mengambang | `save()` tanpa `await`/`.catch` | `await save()` atau tangani error-nya |
| 🔴 S6557 / S6594 | `s.indexOf(p) === 0`, `s.match(re)` | `s.startsWith(p)`, `re.exec(s)` |
| 🔴 S7763 re-export | import lalu export | `export { x } from './x'` |

## 4. Security hotspot yang sering muncul

- `Math.random()` untuk token/ID keamanan → pakai crypto (`crypto.randomUUID()`, `getRandomValues`).
- URL `http://` ke layanan nyata → `https://` (kecuali localhost/dev yang memang dikonfigurasi).
- Regex rawan backtracking (`(a+)+`, `.*.*` pada input pengguna) → sederhanakan atau batasi panjang input.
- Data sensitif (token, PII) di log atau penyimpanan tanpa enkripsi → ikuti skill platform (storage aman).

## 5. Coverage kode baru

- Setiap logika baru (service, hook, util, use case, handler, validasi) punya test; UI murni dan wrapper
  native dicakup E2E.
- Ukur, jangan mengklaim: jalankan perintah test project dengan coverage (`test` di `surfaces[]`, atau
  varian coverage di `package.json`) dan laporkan angka untuk **file yang diubah PR**. Tidak bisa diukur
  lokal → tulis "coverage belum terukur", jangan "≥ 80%".
- Path yang dikecualikan Sonar (`sonar.exclusions` dan `sonar.coverage.exclusions` di
  `sonar-project.properties`) tidak perlu dikejar coverage-nya.

## 6. Penegakan

1. **Saat menulis kode**: ikuti dokumen ini. Rule 🔴 tidak punya linter; hanya disiplin ini yang mencegahnya.
2. **Sebelum melapor selesai**: jalankan `lint` project (banyak project memasang `eslint-plugin-sonarjs`).
   Jangan menambah plugin atau dependency tanpa bertanya.
3. **Dilarang** `// NOSONAR`, menonaktifkan rule, atau menambah exclusion untuk meloloskan gate tanpa
   persetujuan user; perbaiki kodenya.
4. **CI** adalah penjaga terakhir. Gate gagal di pipeline → `pipeline-fixer` membaca issue Sonar-nya
   dan memperbaiki dengan aturan ini.

Project punya konvensi Sonar sendiri (mis. `docs/sonar-conventions.md`) → ikuti juga; bila bertentangan
dengan dokumen ini, tanya user.
