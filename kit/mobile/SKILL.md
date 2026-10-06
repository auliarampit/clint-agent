---
name: skill-mobile
description: >
  Use this skill whenever implementing any feature in a React Native / Expo app in
  this repo. Trigger when: building screens, components, services, hooks, navigation,
  state, or tests for a mobile app. Covers: feature-folder architecture, separation of
  UI and logic, styling discipline, testID convention, i18n discipline, error-handling
  patterns, shared-component extraction, clean code, and testing. Stack-agnostic: reads
  the project's own stack facts from `.claude/mobile-stack.md` and verifies inventory
  against the filesystem rather than assuming a library, router, or folder layout.
  Do NOT trigger for: backend, web frontends, or docs-only changes.
---

# Mobile Implementation Skill (portable core)

**Announce at start:** "I'm using the skill-mobile skill."

> ## ⭐ Prioritas mutlak — 4 prinsip kerja (jangan dilewati)
>
> Baca `.claude/rules/working-principles.md` sebelum mengerjakan task apa pun:
>
> 1. Logika sederhana → jangan over code.
> 2. Bingung → tanya, jangan berasumsi.
> 3. Selalu ikuti semua aturan yang ada (`CLAUDE.md`, `.claude/rules/`, skill, adapter).
> 4. Review hasil terhadap docs atau permintaan sebelum menyatakan selesai.

> ## 🔎 Aturan nomor satu: inventaris diverifikasi, konvensi diikuti
>
> Skill ini memuat dua jenis isi, dan keduanya diperlakukan berbeda:
>
> | Jenis | Contoh | Cara pakai |
> |---|---|---|
> | **Konvensi** | layering UI/logic/data, error mapping, larangan inline style, format testID, disiplin scope | Ikuti. Stabil lintas sprint dan lintas project. |
> | **Inventaris** | route, feature, dependency, komponen yang diekspor, isi config | **Jangan percaya teks mana pun.** Jalankan perintah verifikasinya. |
>
> Kesimpulan negatif dari ingatan ("package X tidak terpasang", "feature Y belum ada",
> "route Z tidak ada") adalah sumber kesalahan termahal di skill ini: hasilnya tipe
> duplikat, komponen tandingan, dan feature tandingan di atas kode yang sudah jalan.
>
> **File ini sengaja tidak menyebut satu pun nama library, package, atau path project.**
> Semua itu ada di adapter (Step 0). Kalau kamu menemukan nama konkret di file ini,
> itu bug — laporkan, jangan ikuti.

---

## Step 0 — Baca adapter stack (WAJIB, sebelum apa pun)

```bash
cat .claude/mobile-stack.md
```

File itu berisi fakta yang **tidak bisa** diturunkan dari konvensi: app mana yang ada,
router apa, state manager apa, di mana wrapper HTTP, nama subfolder feature, toolchain
lint, path dokumen.

**Kalau file itu tidak ada → berhenti.** Jangan menebak stack dari nama folder. Bilang ke
user: adapter belum ada, dan tawarkan mengisinya dari template
(`/clint:siapkan-project`, atau salin `kit/mobile/adapters/TEMPLATE.md` dari clint). Mengisinya ~10 menit; menebaknya bisa
menghasilkan refactor arsitektur yang salah.

**Kalau adapter ada tapi bertentangan dengan filesystem** (menyebut folder yang sudah
tidak ada, library yang sudah diganti) → **filesystem menang**. Beri tahu user bahwa
adapter perlu di-update, lalu lanjut berdasarkan yang nyata.

Sepanjang file ini, notasi `{...}` berarti "ambil dari adapter":
`{appRoot}`, `{featuresRoot}`, `{uiFolder}`, `{logicFolder}`, `{dataFolder}`,
`{testFolder}`, `{lintCmd}`, `{testCmd}`, `{localeFiles}`, dan seterusnya.

---

## ⚡ Fast Path — task sederhana

Cek apakah task **hanya** salah satu dari ini:

| Sinyal | Contoh |
|---|---|
| Styling saja | hapus border, ganti padding, ubah warna, tambah shadow |
| i18n saja | ganti hardcoded text ke `t()`, tambah/ubah key terjemahan |
| testID saja | tambah `testID` di elemen yang sudah ada |
| Prop tweak | tambah/ubah satu prop di komponen yang ada, tanpa logika baru |

**Kalau ya → ikuti Fast Path saja. Lewati Step 1–13.**

**Tiga pengecualian — Fast Path TIDAK berlaku meski perubahannya terlihat sepele:**

1. **Task berasal dari bug report formal.** Sekecil apa pun, triage root-cause dan
   routing status tetap wajib → [Fixing Bug Reports](#fixing-bug-reports).
2. **Menyentuh testID yang sudah dipakai flow E2E.** Rename testID memutus E2E.
   Grep dulu di `{e2ePath}` dan `{tcPath}`.
3. **Adapter belum dibaca.** Fast Path tetap butuh Step 0 — path locale dan perintah
   lint diambil dari sana.

### Fast Path rules

1. **Styling**: ikuti sistem styling di `{stylingSystem}`. **Dilarang `style={{ ... }}`
   inline statis** — inline hanya untuk satu nilai runtime (safe-area inset / animated),
   dikomposisi ke base StyleSheet + komentar satu baris. Warna dari token; kalau tidak
   ada tokennya, hex di StyleSheet, bukan inline.
2. **i18n**: string baru/ubah wajib di **semua** locale di `{localeFiles}`. Jangan pernah
   meninggalkan satu locale kosong. Format key `{keyFormat}`.
3. **testID**: format `{feature}-{component}-{element}[-{modifier}]`. **Jangan rename
   testID yang sudah ada.**
4. **Jangan buka** dokumen requirement/arsitektur — tidak diperlukan untuk perubahan ini.

### Fast Path checklist

- [ ] Bukan task dari bug report, dan tidak me-rename testID yang sudah ada
- [ ] Tidak ada logika baru / API call / navigasi baru
- [ ] Tidak ada `style={{ ... }}` inline statis (inline hanya nilai runtime, dikomentari)
- [ ] Tidak ada hex di class styling — nama token diverifikasi ada di `{tokenFile}`
- [ ] Semua locale diupdate
- [ ] `{lintCmd}` passes
- [ ] Commit: `style(scope): ...` / `fix(scope): ...` / `chore(scope): ...`

**Kalau ternyata lebih kompleks dari yang terlihat → stop, kembali ke Step 1.**

---

## Step 0c — Gaya kode (konvensi, berlaku untuk SEMUA task)

Aturan di bawah berlaku sejak baris pertama yang kamu tulis, bukan sebagai
pembersihan di akhir. Nilai numeriknya diambil dari adapter (§10); yang di sini
adalah aturannya, bukan angkanya.

### 1. Kode berbahasa Inggris, teks pengguna dari file locale

| Yang ditulis                                              | Bahasa                       |
| --------------------------------------------------------- | ---------------------------- |
| Nama file, folder, fungsi, variabel, tipe, konstanta        | **Inggris**                  |
| Nama `testID`                                              | **Inggris**                  |
| Key i18n (`feature.screen.element`)                        | **Inggris**                  |
| Nilai string yang dilihat pengguna                         | bahasa produk, di `{localeFiles}` |
| Path route yang menjadi URL / deep link                    | ikut prototype & PRD         |

Satu-satunya pengecualian yang disengaja adalah baris terakhir: path route dilihat
pengguna dan dipatok dokumen desain, jadi ia mengikuti dokumen — bukan bahasa kode.
Kunci pada objek `routes` tetap Inggris.

### 2. Tanpa komentar di kode

Kode yang butuh paragraf penjelas biasanya butuh nama yang lebih baik atau fungsi
yang lebih kecil — perbaiki itu lebih dulu. Kalau sebuah fakta **benar-benar** harus
berada di file kode, tulis **satu baris pendek**, bukan blok JSDoc.

Yang tetap boleh, dan tidak dihitung sebagai komentar:

- Direktif: `eslint-disable`, `@ts-expect-error`, `@type`, `prettier-ignore`.
- Penanda pasal di sebelah konstanta, mis. `// FR-06` pada ambang rate limit.
- Satu baris penanda ketika sebuah berkas berisi data tiruan, bukan panggilan nyata.

Penjelasan panjang — alasan sebuah keputusan diambil, kontrak yang ditiru, konflik
yang belum selesai — tempatnya di adapter atau di `docs/`, di mana ia bisa dibaca
tanpa membuka kode dan tidak ikut basi saat kodenya berubah.

### 3. Batas ukuran ditegakkan linter, bukan selera

Ambangnya di adapter §10 (`max-lines` per berkas, `max-len` per baris,
`max-lines-per-function`). Ketika sebuah berkas melewati batas, **pecah berdasarkan
tanggung jawab** — daftar kolom form ke berkasnya sendiri, blok tampilan ke
komponennya sendiri — jangan menaikkan ambangnya dan jangan memampatkan baris.

Menaikkan ambang adalah keputusan user, bukan jalan keluar dari task.

### 4. Baris panjang dipecah di kode, bukan disembunyikan

String kelas yang panjang jadi konstanta bernama di atas komponen; kondisi panjang
jadi variabel bernama. Keduanya membuat baris muat **dan** membuat maksudnya
terbaca — dua manfaat dari satu perubahan.

### 5. Tanpa arrow function inline di prop JSX

```tsx
// ❌
<Button onPress={() => router.push(routes.auth.login)} />
<Row onPress={() => choose(city.id)} />

// ✅
function toLogin() {
  router.push(routes.auth.login);
}

<Button onPress={toLogin} />
```

- Handler didefinisikan **bernama, di atas `return`**, dengan nama yang menyatakan maksud:
  navigasi `toLogin` / `goBack`, aksi `handleSubmit` / `confirmReset`.
- Fungsi yang sudah ada dan tidak butuh argumen dioper referensinya langsung:
  `onPress={submit}`, bukan `onPress={() => submit()}`.
- **Butuh argumen dari item daftar** (`choose(city.id)`)? Ekstrak komponen item. Komponen
  itu menerima item dan callback, lalu mendefinisikan handler bernamanya sendiri. Jangan
  membuat closure di dalam `map` maupun di dalam JSX `renderItem`.
- Berlaku untuk semua prop fungsi: `onPress`, `onChangeText`, `onBack`, `renderItem`,
  `keyExtractor`.

JSX yang hanya berisi referensi terbaca sekali lintas seperti daftar deklaratif. Logika di
handler bernama bisa dicari, diberi nama yang jujur, dan tidak menyelinap menjadi logika
bisnis di tengah markup.

### 6. Render kondisional tanpa ternary JSX multi-baris

```tsx
// ❌
{options.length === 0 ? (
  <Text>…</Text>
) : (
  <RowGroup>…</RowGroup>
)}
{error === null ? null : (
  <Banner … />
)}

// ✅ daftar kosong → ListEmptyComponent
<FlatList data={options} ListEmptyComponent={EmptyCities} … />

// ✅ satu cabang → && dengan kondisi boolean
{hasError && <Banner … />}

// ✅ dua cabang berisi markup → komponen bernama yang memilih sendiri
<NextPrayerContent next={next} />
```

- **Satu cabang:** `{kondisi && <X />}`, dan kondisinya **wajib boolean** (`!== null`,
  `> 0`, variabel `isX` / `hasX`). `{items.length && <X />}` merender angka `0` — di
  React Native itu crash bila jatuh di luar `<Text>`.
- **Dua cabang yang masing-masing JSX:** ekstrak ke komponen bernama yang memakai early
  return, atau early return di komponen itu sendiri.
- **Daftar kosong:** `ListEmptyComponent`, bukan ternary yang membungkus list.
- Ternary **satu baris untuk nilai** (string, class, prop) tetap boleh. Ternary bersarang
  tetap dilarang (Step 9).

### 7. Pemilihan komponen dinamis: resolusi inline, bukan fungsi pembungkus

Saat memilih salah satu dari beberapa komponen yang **sudah ada** berdasarkan kondisi
runtime (mis. ikon per jenis item), jangan membungkus pemilihannya dalam fungsi terpisah
yang me-`return` referensi komponen itu:

```tsx
// ❌ — linter React Compiler (react-hooks/static-components) menandai ini "component
// dibuat saat render", meski iconFor() selalu mengembalikan salah satu komponen
// top-level yang sudah ada, tidak pernah komponen baru.
function iconFor(kind: Kind) {
  switch (kind) {
    case 'a': return IconA;
    case 'b': return IconB;
  }
}
function Row({ kind }: Props) {
  const Icon = iconFor(kind);
  return <Icon />;
}

// ✅ — resolusi langsung di body komponen: ternary antar identifier top-level
// (varian sedikit), atau index Record langsung di titik render (varian banyak).
const ICON_BY_KIND: Record<Kind, IconComponent> = { a: IconA, b: IconB };
function Row({ kind }: Props) {
  const Icon = ICON_BY_KIND[kind];
  return <Icon />;
}
```

Kalau variannya butuh lebih dari satu diskriminan (mis. `kind` ditambah sub-varian
sekunder), normalisasi dulu ke satu kunci datar lewat fungsi biasa yang **mengembalikan
string/enum, bukan komponen** (fungsi yang me-return string aman dari aturan ini), baru
index Record sekali di titik render. Bonusnya bukan cuma lolos linter: `Record<Union, T>`
memaksa compiler menolak build begitu `Union` bertambah varian tapi tabelnya belum diisi
— beda dari rantai `if/else`/`switch` yang mengembalikan komponen, yang diam-diam jatuh
ke cabang default saat varian baru muncul.

---

## Step 1 — Klasifikasi task

### A. Tipe task — pilih jalur dulu

| Tipe | Kapan | Jalur |
|---|---|---|
| **feat** | Screen, komponen, hook, service, atau flow navigasi baru | Skill penuh — tentukan Tier (§B), Step 2–12, checklist Tier 2/3 |
| **fix** | Bug report, mismatch implementasi, feedback QA | Jalur Tier 1 — Step 2 + checklist Tier 1. Dari bug report formal → [Fixing Bug Reports](#fixing-bug-reports) |
| **refactor** | Pecah file besar, ekstrak hook/komponen, hapus duplikasi | Langsung ke [Refactor Guidelines](#refactor-guidelines) |
| **chore** | Config, dep, tooling, build script | Langsung ke [Chore Guidelines](#chore-guidelines) |

Umumkan tipe task sebelum lanjut:
> "This is a **[feat|fix|refactor|chore]** task."

### B. Tier task (feat & fix saja)

- **Tier 1 — perubahan di file yang sudah ada**, di feature yang foldernya sudah ada.
- **Tier 2 — file baru** di dalam feature yang foldernya sudah ada.
- **Tier 3 — feature baru**: folder feature-nya belum ada.

### Aturan klasifikasi

1. **Jalankan `ls {featuresRoot}`** — jangan mengklasifikasi dari ingatan atau dari daftar
   di dokumen mana pun. Kalau folder yang dicari tidak ada di output → **Tier 3**.
2. File baru di feature yang sudah ada → **Tier 2**.
3. Hanya mengedit → **Tier 1**.
4. Ambigu → pilih tier yang lebih tinggi.

> Salah-klasifikasi Tier 3 padahal foldernya sudah ada adalah kesalahan termahal di skill
> ini: hasilnya feature tandingan di atas kode yang sudah jalan. Satu `ls` mencegahnya.

**Umumkan tier sebelum lanjut:**
> "This is a **Tier N** task. I'll follow the Tier N checklist."

---

## When to Stop and Ask

Sebelum melanjutkan pada salah satu dari ini, berhenti dan tanya — **jangan menebak,
mengarang, atau menyelesaikannya diam-diam**:

| Situasi | Kenapa berhenti |
|---|---|
| Adapter (`.claude/mobile-stack.md`) tidak ada atau kosong di bagian yang kamu butuhkan | Menebak stack bisa menghasilkan refactor arsitektur yang salah |
| Tier 2/3 tapi tidak ada impl plan (padahal project punya alurnya) | Plan adalah sumber kebenaran — mengarang arsitektur = rework |
| Plan bertentangan dengan desain atau API contract | Hanya user yang boleh menyelesaikan konflik dokumen |
| Butuh dependency baru | Menambah dep punya implikasi CI/bundle di luar task ini |
| Butuh mengganti/menambah state manager atau router | Itu keputusan arsitektur, bukan detail implementasi |
| Screen/flow tidak ada di desain mana pun | Gap desain — lanjut = risiko rework visual total |
| Aturan bisnis ambigu setelah baca plan + test case | Salah tafsir = perilaku salah yang lolos diam-diam |
| Scope membengkak di tengah jalan | Scope creep harus disetujui dulu |
| Dua pendekatan valid dengan trade-off nyata | User punya konteks yang kamu tidak punya |

Satu pertanyaan satu kalimat jauh lebih murah daripada satu implementasi yang salah.

---

## Fixing Bug Reports

> Berlaku untuk setiap task **fix** yang berasal dari bug report formal.
> Path laporannya ada di adapter §12. Kalau project tidak punya alur bug formal,
> lewati bagian ini dan perlakukan sebagai fix Tier 1 biasa.

**Triage root cause dulu — apakah ini benar-benar bug mobile?** Sebelum menulis fix,
pastikan defect-nya memang di app mobile. Baca service/hook terkait dan API contract atau
response yang teramati. Kalau root cause-nya di hulu (API mengembalikan status code salah,
field hilang, aturan server yang tidak bisa dipenuhi client, gap DB/migrasi/template), itu
**bukan bug mobile** — jangan menambal mobile untuk menutupinya.

Selesaikan tiap bug **sesuai sifatnya** — jangan pernah diam-diam mengambil keputusan
produk atau spesifikasi yang laporannya biarkan terbuka:

| Sifat bug | Tindakan |
|---|---|
| Defect kode / i18n / styling yang jelas di mobile | Perbaiki. Set status **Fixed** + catatan resolusi dengan referensi kode. |
| Perubahan visual/copy milik desainer, jelas dan tidak ambigu | Terapkan. Set baris Design Feedback **Fixed**. |
| **Root cause di API/backend** | Set status mobile **Invalid** + catatan bertanggal kenapa ini bukan bug mobile. **File ulang** ke laporan backend (path di adapter §12). **Jangan** ubah kode mobile. |
| **Butuh keputusan PM/SA** — gap spec/PRD, deviasi implementasi vs test case, aturan bisnis ambigu, dua pendekatan valid | **Jangan putuskan sendiri.** Set **Blocked**, pindahkan ke bagian feedback PM/SA di laporan, biarkan kode apa adanya, dan berhenti di item itu. |

Sebuah bug **Blocked** ketika mengirim fix berarti memilih perilaku yang tidak dipatok
dokumen; memperbaikinya sepihak berisiko mengirim maksud yang salah.

**Bentuk temuan yang layak `Blocked`:** dua perilaku sama-sama masuk akal dan dokumen tidak
memilih salah satunya. Misalnya: setelah hapus akun, app mendarat di layar A sementara
dokumen menyebut layar B; "memperbaikinya" berarti membuat cabang khusus pada perilaku
logout bersama, jadi keputusannya milik PM, bukan Dev.

> ⚠️ **Jangan pernah memakai ID bug di dokumen mana pun sebagai status terkini.** Contoh di
> skill selalu mengilustrasikan **pola penalaran**, bukan status bug. Selalu baca laporan
> dan kode terkait sebelum menyimpulkan sebuah bug masih terbuka.

---

## Step 2 — Baca sebelum menulis

### Pohon keputusan dokumen — ikuti ketat supaya tidak boros token

```
Impl plan untuk modul/sprint ini ada?
  └─ YA  → Baca plan-nya SAJA. Jangan buka dokumen requirement/arsitektur —
            plan sudah mensintesisnya.
            Kecuali: task menyentuh endpoint API → baca endpoint itu di API contract.
  └─ TIDAK → Ini fix Tier 1 atau hotfix tanpa plan. Baca selektif:
            Bug report menyebut ID test case? → baca baris TC itu saja.
            Task menyentuh endpoint API?       → baca endpoint itu saja.
            Aturan bisnis ambigu?              → baca bagian requirement itu saja.
            Selain itu                         → jangan buka dokumen apa pun.

Hasil implementasi tidak sesuai harapan (belum ada bug report)?
  └─ Mismatch UI        → baca desain/prototype untuk screen itu dulu (ringan).
  └─ Mismatch fungsional → baca ulang bagian plan yang relevan.
                           Plan ambigu? → baca baris test case yang menutup flow itu.
  └─ Keduanya           → desain dulu (cepat), lalu bagian plan kalau masih tidak jelas.
  └─ JANGAN             → membuka dokumen requirement/arsitektur untuk menyelesaikan
                          mismatch implementasi. Kalau plan sendiri bertentangan dengan
                          requirement, angkat ke user — jangan diam-diam baca dan putuskan.
```

**Aturan:** dokumen requirement dan arsitektur adalah sumber untuk arsitek dan penulis plan,
bukan untuk sesi coding. Membukanya untuk bug fix rutin adalah pemborosan token. Plan atau
test case spesifik adalah pintu masuk yang benar.

### Checklist — apa yang dibaca sebelum menulis

1. **Adapter** (`.claude/mobile-stack.md`) — selalu, sebelum apa pun (Step 0).
2. **Impl plan** — kalau ada, ini sumber kebenaran utama. Ikuti; jangan menggantinya dengan
   desainmu sendiri. Untuk Tier 2/3 plan diharapkan ada; kalau tidak ada, tanya dulu.
3. **Baris test case** — hanya saat memperbaiki bug yang menyebut ID TC. Baca baris persisnya
   untuk memverifikasi testID, prakondisi, dan assertion yang diharapkan.
4. **API contract** — hanya saat task menambah/mengubah panggilan API. Cocokkan path, method,
   nama field, dan kode error **verbatim**. Perhatikan casing payload (adapter §5).
5. **Folder feature target** — selalu. Pahami pola yang ada, hindari duplikasi.
6. **File sejenis terdekat** — saat membuat hook/service baru, baca padanan terdekatnya dulu.
7. **Desain/prototype** — saat membangun atau mengubah layout/copy sebuah screen.
   **Tarik ulang repo desain dan cek tanggal commit terakhir prototype** tepat sebelum mulai
   membangun, dan sekali lagi sebelum meminta user memvalidasi. Prototype bisa dirombak di hari
   yang sama; membangun dari versi yang sudah dibaca pagi hari menghasilkan layar yang
   "sangat berbeda" padahal kodenya rapi. Bandingkan hasilnya **berdampingan secara visual**
   (potret prototype dan potret simulator pada lebar layar yang sama), bukan dari ingatan.
8. **Jumlah baris file** — catat sebelum mengubah. Aturan batas baris berlaku **asimetris**
   (lihat Step 9): file baru wajib di bawah batas; file lama yang sudah melewatinya bukan
   urusan task fix.

---

## Step 3 — Reuse hierarchy: cek yang sudah ada sebelum membuat

Sebelum menambah apa pun yang baru, cek apakah ia sudah ada atau seharusnya hidup di tingkat
yang lebih tinggi. Tingkatan konkretnya ada di adapter §7; yang portable adalah urutannya:

```
1. Package bersama lintas app        ← kalau project punya (adapter §7)
2. Package bersama dengan web        ← types, validators, i18n, utils, tokens
3. Komponen bersama dalam satu app   ← dipakai ≥ 2 feature
4. Komponen milik satu feature       ← default
```

**Keputusan:** tanya "apakah app/target lain juga butuh ini?" → ya → naik satu tingkat.
"Sudah dipakai ≥ 2 feature di app ini?" → ya → tingkat 3. Selain itu → feature-local.

**Verifikasi sebelum menyimpulkan sesuatu belum ada:**

```bash
# apa yang diekspor package bersama (perintah persisnya di adapter §7)
# apa yang sudah ada sebagai komponen app-local
# apa saja shared package yang benar-benar terpasang
```

Aturan yang berlaku di semua project:

- Package/komponen yang **sudah** ada → wajib dipakai, jangan bikin duplikat lokal.
- Package yang **belum** terpasang → jangan diam-diam menambah dep. Tanya user dulu.
- Ketiadaan sebuah package **bukan izin** untuk melanggar aturan lain. Tidak ada package
  token bukan alasan menulis hex inline; tidak ada package i18n bukan alasan hardcode string.
  Cari padanan app-local-nya dulu (adapter §8, §9).

---

## Step 4 — Arsitektur folder feature

Semua kode feature baru hidup di `{featuresRoot}/{feature}/`. Jangan menaruh file milik satu
feature di folder top-level bersama — itu untuk kode lintas-feature.

Nama subfolder **berbeda antar project** (adapter §6). Yang portable adalah pemisahannya:

```
{featuresRoot}/{feature}/
  {uiFolder}/       ← UI saja — tanpa logika bisnis
  {logicFolder}/    ← logika bisnis; dikonsumsi UI
  {dataFolder}/     ← panggilan API, mapper
  {testFolder}/     ← test, di samping kode yang diuji
```

Cek pola yang berlaku di area yang kamu sentuh sebelum menaruh file baru:

```bash
ls -R {featuresRoot}/{feature-terdekat}
```

### Navigasi

Cara menambah screen dan cara berpindah screen **sangat berbeda** antara router file-based
dan stack-based — adapter §3 menyimpan yang benar untuk project ini. Yang portable:

- **Jangan pernah mencampur dua sistem routing** dalam satu app.
- Route/param baru didaftarkan di tempat yang ditunjuk adapter, bukan di tempat baru.
- Jangan menghardcode string path yang tersebar; pakai helper/typed param kalau project punya.
- Baca komentar di file definisi route — di banyak project, komentar itu membawa keputusan
  navigasi yang tidak terekam di dokumen mana pun.

---

## Step 5 — Pisahkan logika dari UI

**Komponen merender. Hook dan service memutuskan.**

| Layer | Boleh | Dilarang |
|---|---|---|
| UI (`{uiFolder}`) | JSX, layout, terjemahan, memanggil hook | Panggilan API, mutasi store, kondisi bisnis |
| Komponen | JSX, state UI lokal (toggle/focus) | Panggilan API, mutasi store, navigasi |
| Logic (`{logicFolder}`) | Selector store, panggilan API, derived state, navigasi | JSX |
| Data (`{dataFolder}`) | Wrapper HTTP, pemetaan data, persistence | JSX, hook, store |
| Store | State + action | JSX, panggilan API langsung |

### Ekstrak kondisi kompleks — wajib

Jangan menaruh logika rumit inline di dalam JSX. Kalau sebuah kondisi butuh lebih dari satu
operator, ekstrak ke variabel bernama.

**Salah:**
```tsx
{!wizard.step2.complete || isSubmitting || wizard.step1.uri === null
  ? <ActivityIndicator />
  : <SubmitButton />}
```

**Benar:**
```tsx
const isReadyToSubmit =
  wizard.step1.uri !== null && wizard.step2.complete && !isSubmitting

return isReadyToSubmit ? <SubmitButton /> : <ActivityIndicator />
```

**Patokan:** kalau kondisinya tidak bisa dibaca lantang dalam satu tarikan napas, ekstrak.

---

## Step 6 — Styling: token dulu, StyleSheet untuk sisanya, tidak pernah inline statis

Sistem styling project ini ada di adapter §8. Aturannya sama apa pun sistemnya:

1. **Class/token utility dulu** — layout, spacing, sizing, radius, flex, dan semua warna yang
   punya token.
2. **`StyleSheet.create()`** — untuk yang tidak bisa diekspresikan class dengan bersih:
   shadow/`elevation`, warna tanpa token, tinggi persen, `textAlignVertical`, dan objek
   `contentContainerStyle`.

> **`StyleSheet.create()` bukan "fallback" — ia partner normal.** Dipakai di mana pun
> class kurang; itu wajar dan diharapkan.

**Jangan pernah menulis objek `style={{ ... }}` statis di JSX.** Ini satu-satunya aturan keras.
Objek inline hanya boleh untuk satu nilai yang benar-benar **runtime** (safe-area inset, nilai
animasi/terukur), dan itu pun harus dikomposisi ke base `StyleSheet` serta diberi komentar satu
baris yang menjelaskan sumber runtime-nya.

### Benar
```tsx
<View className="flex-1 items-center justify-center px-5">
<View className="rounded-2xl border p-5" style={styles.card}>

<View
  className="overflow-hidden rounded-b-3xl px-5"
  // paddingTop runtime (safe-area inset)
  style={[styles.hero, { paddingTop: insets.top + 18 }]}
>
```

### Dilarang
```tsx
<View style={{ flex: 1, padding: 16 }}>        // ❌ statis — pakai class
<View style={{ backgroundColor: '#EFF6FF' }}>  // ❌ statis — pakai StyleSheet
<Text className="text-[#0ED400]">              // ❌ hex arbitrer di class — pakai token
```

### Warna

**Nama token berbeda antar project, dan banyak engine styling membuang class yang tidak
dikenal tanpa error** — memakai nama token project lain menghasilkan elemen tanpa warna,
bukan crash. Jadi verifikasi dulu ke `{tokenFile}` (adapter §8).

Urutannya:

1. **Class token** dari file token project ini. Tidak pernah hex arbitrer di class.
2. Warna tanpa token → hex di `StyleSheet.create()`, lewat konstanta warna app-local kalau ada.
3. **Props** warna non-style (mis. `color={...}` pada ikon) → konstanta, bukan literal hex.
4. Warna yang dipakai lintas screen → tambahkan **sekali** ke file token supaya jadi nama class.

### Kelas kondisional
Pakai template literal. Jangan menambah dependency helper class hanya untuk ini.
```tsx
const boxClass = `h-5 w-5 rounded border ${checked ? 'border-primary bg-primary' : 'border-muted'}`
```

### Urutan module-load
Kalau blok `StyleSheet.create()` ada di bawah file, jangan mereferensikan `styles.*` dari
`const` module-level di atasnya (temporal dead zone → crash). Pilih style di dalam komponen
atau lewat `function` yang ter-hoist.

### Gambar dengan `aspectRatio` dinamis — jangan pakai `Image` bawaan React Native

`Image` bawaan React Native **tidak reliabel** menghormati `style={{ aspectRatio }}` ketika
lebarnya datang dari persentase/className (`w-full`) alih-alih angka literal — hasilnya
kotak bisa jauh lebih tinggi dari yang dihitung, dan `resizeMode="cover"` lalu memotong sisi
gambar secara tak terduga. Ini baru kelihatan di device/simulator sungguhan, bukan di test
Jest (RTL me-mock layout, tidak menghitung ukuran nyata).

Pakai komponen gambar yang ditunjuk adapter (§7, pola UI "Gambar") untuk **semua** gambar
yang rasionya dihitung dari dimensi berkas (prop fit-nya + `style={{ aspectRatio }}` bekerja
benar). Kalau adapter belum menunjuk komponen gambar, tanya user. Untuk gambar lokal yang di-`require()`, dimensi aslinya didapat sinkron lewat
`Image.resolveAssetSource(source)` dari `react-native` (impor terpisah, hanya untuk fungsi
ini) — jangan hardcode angka rasio, hitung dari berkas supaya foto potret tetap potret dan
lanskap tidak dipaksa jadi kotak potret. Beri ambang `Math.max(rasio, MIN_RATIO)` supaya foto
ekstrem tidak membuat kartu jadi sangat panjang.

### Verifikasi kesetiaan visual terhadap prototype — kutip CSS literal, jangan menebak

Saat membandingkan implementasi dengan prototype (HTML/CSS statis), **baca nilai CSS-nya
langsung** (`font-weight`, warna token, `object-position`, struktur pembungkus kartu) —
jangan menyimpulkan gaya dari screenshot, dari nama variabel JSX, atau dari isi mock data
yang "kelihatannya masuk akal". Kesalahan yang baru ketahuan lewat pembandingan literal:
label vs value tertukar bold/muted-nya, ikon warna seragam padahal prototype membedakan per
jenis baris, kartu pembungkus (`.naskah`) hilang di beberapa section, banner status
(offline/online/kosong) dipakai dengan warna dan skeleton generik padahal prototype
mendefinisikan varian (info/warn) dan salinan teks yang berbeda per konteks, serta ikon
`empty state` yang diganti dengan ikon generik alih-alih ikon spesifik yang didefinisikan
prototype.

Checklist sebelum bilang "sudah sama": untuk setiap komponen kutip pasangan CSS-nya, cek
**semua** varian state (bukan hanya happy path — juga banner offline, empty/belum-tayang,
error) karena ini yang paling sering luput, dan cek elemen navigasi/CTA yang berdiri sendiri
di bagian akhir section (tombol "kembali", disclaimer legal) yang mudah terlewat karena tidak
ada di viewport pertama saat membandingkan screenshot.

---

## Step 7 — Konvensi testID

Setiap elemen interaktif, container utama, dan elemen status yang terlihat user **wajib**
punya `testID` (atau atribut locator yang dipakai project ini — adapter §11).

### Format
```
{feature}-{component}-{element}[-{modifier}]
```

| Permukaan | Contoh |
|---|---|
| Root screen | `auth-login-screen` |
| Container seksi | `kyc-step2-container` |
| Input | `auth-login-email-input` |
| Tombol | `auth-login-submit-btn` |
| Link | `auth-login-forgot-link` |
| Error/banner | `auth-login-error` |

**Aturan suffix:** input `-input` · tombol `-btn` · link `-link` · container `-container` ·
root screen `-screen` untuk file baru.

> #### ⚠️ Konvensi lama biasanya hidup berdampingan — jangan "merapikan"
>
> Banyak project punya lebih dari satu konvensi root (mis. `-page` yang lebih lama dan
> `-screen` yang lebih baru). **Keduanya sah.** Aturannya:
>
> - **File baru** → ikuti konvensi terbaru project (adapter §11 kalau dicatat, kalau tidak:
>   lihat file yang paling baru diubah).
> - **File yang sudah ada** → biarkan. Rename adalah perubahan yang memutus flow E2E dan
>   assertion test case, dan **bukan** bagian dari task apa pun kecuali diminta eksplisit.
> - Sebelum mengubah testID apa pun: `grep -rn "<testid>" {e2ePath} {tcPath}`
>
> Kalau dokumen test case menyebut testID spesifik, **dokumen menang** — testID adalah
> kontrak dengan QA, bukan preferensi gaya.

### Wajib ada di
Semua elemen yang bisa ditekan · semua input teks · scroll view yang dipakai pull-to-refresh ·
elemen teks error/status · container seksi utama · loading indicator yang mewakili state bernama.

### Dilarang
Membuat testID di dalam loop tanpa suffix unik (pakai id item) · melewatkan testID karena
"sudah jelas".

---

## Step 8 — Aturan stack: ikuti yang sudah dipilih project

Skill ini **tidak punya preferensi library.** Yang dipakai project ini ada di adapter §4–§5.
Yang portable adalah disiplinnya, dan disiplin ini mengikat di semua project:

| Aturan | Kenapa |
|---|---|
| **Satu state manager untuk satu kebutuhan.** Auth/session pakai yang ditunjuk adapter; server state pakai yang ditunjuk adapter. Jangan mencampur dua library untuk kebutuhan yang sama. | Dua sumber kebenaran = bug sinkronisasi yang sulit dilacak |
| **Nol panggilan HTTP telanjang di kode feature.** Semua lewat wrapper di adapter §5. | Wrapper memegang timeout, refresh token, mock mode, dan error toast. Melewatinya = perilaku tidak konsisten |
| **Nol akses storage mentah di kode feature.** Lewat wrapper yang ditunjuk adapter. | Token sensitif butuh storage yang benar; wrapper yang menegakkannya |
| **Satu sistem routing.** Jangan mencampur file-based dan stack-based. | Dua model navigasi = back-stack yang tidak terprediksi |
| **Satu formatter.** Yang ditunjuk adapter §10. | Formatter kedua menghasilkan diff berisik yang berubah lagi saat commit |
| **Import lintas feature selalu lewat path alias**, tidak pernah `../../`. | Relative path lintas feature mengunci struktur folder |

> **Mau menyimpang dari pilihan project?** Itu keputusan arsitektur, bukan detail
> implementasi. Angkat ke user (lihat [When to Stop and Ask](#when-to-stop-and-ask)).
> **Jangan pernah "memperbaiki" state manager atau router yang sudah dipakai project
> menjadi yang kamu kira lebih baik** — di project yang memilihnya secara sadar, itu
> merusak, bukan membersihkan.

### Casing payload API

Adapter §5 mencatat casing yang dipakai project ini. Ikuti **verbatim** dan konsisten di
seluruh payload — request, response, dan nested object. Salah casing pada satu field
menghasilkan `undefined` diam-diam, bukan error: flag tidak pernah menyala, cabang tidak
pernah jalan, dan tidak ada yang gagal sampai QA menemukannya.

### Store yang sudah ada — baca file-nya, jangan salin bentuk dari dokumen

Bentuk state auth bertambah tiap sprint (routing pasca-login, teardown sesi, flag). Menyalin
bentuknya dari dokumen mana pun akan salah. Sebelum menyentuh auth state, **baca file store
yang ditunjuk adapter §4**. Store itu biasanya sudah terimplementasi penuh — jangan menulis
ulang. Komentar di dalamnya sering menjelaskan kenapa sebuah field ada; baca sebelum
mengasumsikan sesuatu belum didukung.

### Pola error handling — pemetaan standar

Semua error API dipetakan ke **tepat satu** dari tiga respons UI:

| Respons | Kapan | Bagaimana |
|---|---|---|
| **Inline error state** | Error setingkat validasi yang terikat ke screen saat itu | State di hook; render banner atau error per-field |
| **Toast** | Error latar/jaringan yang bukan akibat langsung aksi user | Panggil toast di blok catch |
| **Navigasi** | Error yang butuh screen lain untuk diselesaikan | Panggil aksi navigasi dari catch di hook |

**Aturan:**
- Satu error → satu respons. Jangan pernah toast **dan** banner untuk kode yang sama.
- Kode yang tidak dikenal selalu jatuh ke toast + state generik — jangan pernah ditelan diam-diam.
- Kalau hook menangani error dengan state inline-nya sendiri, matikan toast otomatis dari
  wrapper HTTP (opsinya di adapter §5); kalau tidak, user melihat umpan balik ganda.
- Tipe error state selalu union literal string, bukan `string | null` generik.

```ts
const [error, setError] = useState<'credentials' | 'locked' | 'network' | null>(null)

} catch (e) {
  const code = getApiErrorCode(e)          // helper di adapter §5
  if (code === 'INVALID_CREDENTIALS') setError('credentials')
  else if (code === 'ACCOUNT_LOCKED')  setError('locked')
  else { setError('network'); toast.error(t('errors.network')) }
}
```

### Mock handler

Kalau endpoint backend untuk feature baru belum ada dan project punya mode mock, tambahkan
handler-nya supaya app tetap jalan. Baca handler yang ada dulu untuk mencocokkan pola. Mock
**bukan pengganti** API contract — cocokkan nama field dan status code dengan contract.

---

## Step 8.5 — Pola feature yang berulang

Pola berikut portable lintas project; nama library-nya ambil dari adapter.

### Pagination / infinite scroll
Query bertingkat halaman + list yang memanggil halaman berikutnya saat mendekati ujung.
Selalu sertakan `keyExtractor` dengan id stabil, footer loading, dan `testID` pada list.

### Pull-to-refresh
Sambungkan `refreshControl` ke `refetch` + flag `isRefetching` dari query, bukan ke state
manual.

### Empty state
**Selalu** tampilkan setelah loading selesai dan data kosong — jangan pernah meninggalkan
layar kosong tanpa penjelasan. Beri `testID` sendiri. Berlaku juga saat "kosong" datang
dari respons yang **sukses** (200 dengan array/objek kosong), bukan cuma dari error atau
404 — jangan biarkan hasil kosong lolos begitu saja ke cabang "berhasil dimuat" tanpa
pengecekan panjang/isi eksplisit. Kalau ada lebih dari satu sumber data untuk halaman yang
sama (mis. jaringan dan salinan luring), cek kekosongan di **setiap** sumber, bukan cuma
yang paling sering dipakai.

### Skeleton / loading state
Skeleton saat load pertama; spinner refresh saat pull-to-refresh. **Jangan** memakai dialog
loading yang memblokir untuk data list — dialog blocking hanya untuk mutation (submit, hapus).

> Semua pembacaan dan mutation yang menunggu jaringan **wajib** punya indikator: skeleton,
> spinner inline, atau tombol dengan state disabled/loading. Tidak boleh ada request in-flight
> yang tidak terlihat user.

### Wizard multi-langkah
State ada di hook, **bukan** di parameter navigasi. Langkah dirender kondisional — jangan
bernavigasi antar langkah. Panggil navigasi hanya saat wizard selesai atau dibatalkan.
Bersihkan draft wizard saat sesi berakhir supaya data user sebelumnya tidak bocor.

### Optimistic UI
Untuk mutation yang butuh umpan balik instan: batalkan query terkait, simpan snapshot
sebelumnya, tulis optimistis, rollback di `onError`, invalidate di `onSettled`.

### Tap ganda pada aksi async yang bisa disusul

Saat sebuah handler async (panggilan native seperti `Linking`, atau efek samping lain di
luar manajer server-state project) bisa dipicu lagi sebelum panggilan sebelumnya selesai —
dua tap cepat ke item berbeda — dan hasilnya menyetel state UI (membuka modal, menyetel
pesan error) di blok `catch`/`then`, **jangan asumsikan urutan settle promise sama dengan
urutan tap user**. Promise dari tap pertama bisa selesai belakangan dan menimpa state yang
seharusnya milik tap kedua. Jaga dengan penghitung permintaan:

```tsx
const latestRequestId = useRef(0);

async function open(item: Item) {
  const requestId = (latestRequestId.current += 1);
  try {
    await doSomethingAsync(item);
  } catch {
    if (requestId === latestRequestId.current) {
      setFallback(item); // hanya tap TERAKHIR yang boleh menang
    }
  }
}
```

Manajer server-state modern (adapter §4/§5) biasanya sudah menangani ini sendiri untuk
query/mutation lewat library-nya (permintaan terbaru otomatis menang) — pola di atas untuk
efek samping async di **luar** lapisan itu, yang menyetel state lokal langsung dari hasil
promise.

---

### Daftar — FlatList untuk data, `map` hanya untuk grup tetap kecil

| Kasus | Pakai |
|---|---|
| Data dari API, hasil pencarian, konten yang panjangnya ditentukan data | `FlatList` / `SectionList` — **list-nya menjadi scroll container layar**. Konten lain masuk `ListHeaderComponent` / `ListFooterComponent`, keadaan kosong masuk `ListEmptyComponent` |
| Grup kecil yang panjangnya ditetapkan desain (±10 butir ke bawah, mis. 6 tile menu, baris jadwal harian) di dalam kartu atau di layar yang juga berisi konten lain | `map` di dalam `ScrollView` |

- **Jangan menaruh `FlatList` di dalam `ScrollView` searah.** Virtualisasi mati dan React
  Native memperingatkan nested VirtualizedList — kalau layar punya konten lain, jadikan
  konten itu header/footer list.
- `keyExtractor` dan `renderItem` didefinisikan bernama (Step 0c.5); `keyExtractor` boleh di
  level modul.
- Header yang berisi input teks dioper sebagai elemen dari komponen yang didefinisikan di
  level modul, **bukan** komponen inline — kalau tidak, input kehilangan fokus setiap render.
- Item yang dibingkai sebagai satu kartu di dalam `FlatList` menggambar tepinya sendiri
  (atas untuk item pertama, bawah untuk item terakhir), karena list tidak punya pembungkus
  kartu.

### Bottom sheet

Pakai library bottom sheet yang ditunjuk adapter §7. **Jangan merakit sheet sendiri** dari
`Modal` + scrim `Pressable` + animasi manual: swipe-to-close, keyboard, safe area, dan
aksesibilitas hampir selalu tertinggal. Kalau adapter belum menunjuk library, tanya user
sebelum menambah dependency.

---

## Step 9 — Clean code

**Struktur & ukuran:**

- **Maksimum ~250 baris per file — untuk file yang kamu *buat*.** Kalau file baru akan
  melewatinya, pecah: screen besar → sub-komponen; service besar → service + helper;
  hook besar → beberapa hook per concern.

  > **Carve-out untuk file yang sudah ada.** Hampir setiap project punya file yang sudah di
  > atas batas. Saat mengerjakan **fix Tier 1** di file seperti itu:
  > - Jangan memecahnya. Pemecahan file adalah task **refactor** tersendiri dengan baseline
  >   test hijau dan persetujuan scope.
  > - Cukup **jangan memperburuk**: kalau editmu menambah banyak baris ke file yang sudah
  >   lewat batas, taruh bagian barunya di komponen/helper baru.
  > - Sebutkan pelanggarannya di response supaya user yang memutuskan.

- **Maksimum ~50 baris per fungsi.** Ekstrak helper dengan nama deskriptif.
- **Kompleksitas kognitif rendah** per fungsi — sederhanakan kondisi, ekstrak sub-fungsi.

> ⚠️ **Angka di atas adalah default, bukan otoritas.** Kalau linter project menegakkan ambang
> sendiri (`max-lines-per-function`, `complexity`, `cognitive-complexity`, dst — lihat adapter
> §10), **angka linter yang menang** — itu yang benar-benar memblokir CI. Jangan memecah fungsi
> yang lolos linter project hanya untuk memenuhi angka di file ini.
- **Tidak ada kode mati.** Hapus import/variabel/blok komentar yang tidak terpakai.
- **Tidak ada duplikasi.** Blok 3+ baris yang sama muncul dua kali → ekstrak.

**Aturan yang paling sering dilanggar (kebanyakan tidak tertangkap linter):**

- **Props selalu `Readonly<…>`** — ini penyumbang temuan terbesar di static analysis.
- **Tidak ada ternary bersarang** — pakai lookup map atau helper dengan early return.
- **Tidak ada arrow function inline di prop JSX** — handler bernama di atas `return` (Step 0c.5).
- **Tidak ada ternary JSX multi-baris** — `&&` boolean, `ListEmptyComponent`, atau komponen bernama (Step 0c.6).
- **Tidak ada komponen yang didefinisikan di dalam komponen lain** — hoist ke module scope.
- **Tidak memakai index array sebagai `key`** — pakai id stabil.
- **Tidak ada `any`**, tidak ada cast/non-null assertion yang tidak perlu — beri tipe sebenarnya.

> Kalau project punya dokumen konvensi static-analysis sendiri, itu yang menang atas daftar
> di atas. Cek adapter §12.

### Penamaan
Komponen `PascalCase` · hook `camelCase` berawalan `use` · service: export `camelCase` pada
objek service · konstanta `SCREAMING_SNAKE_CASE` · tipe `PascalCase` · testID `kebab-case`.

---

## Refactor Guidelines

> Pintu masuk untuk task **refactor**. Lewati Step 2–8 — baca hanya file yang akan diubah.

### Kapan refactor — ambang pemicu

| Sinyal | Ambang | Tindakan |
|---|---|---|
| File terlalu panjang | > ~250 baris | Pecah ke sub-komponen atau hook terpisah |
| Fungsi terlalu panjang | > ~50 baris | Ekstrak helper bernama |
| Blok duplikat | 3+ baris sama di 2+ tempat | Ekstrak ke helper/komponen bersama |
| Logika bisnis di JSX | Berapa pun | Pindah ke hook |
| Panggilan API di komponen | Berapa pun | Pindah ke layer data |
| **Melanggar disiplin Step 8** | HTTP telanjang, storage mentah, dua state manager untuk hal yang sama | Ganti dengan pola yang benar |

> ⚠️ **"Pelanggaran arsitektur" berarti melanggar pilihan project ini — bukan melanggar
> selera kamu.** Sebelum menandai sesuatu sebagai pelanggaran, cek adapter §4–§5. Library
> state atau router yang dipakai project **secara konsisten** bukan pelanggaran, seberapa pun
> kamu lebih menyukai yang lain. Mengubahnya adalah keputusan arsitektur → tanya user.

### Aturan keselamatan — test adalah jaring pengaman

1. Jalankan `{testCmd}` — pastikan baseline hijau. Kalau sudah merah sebelum kamu mulai,
   **stop dan laporkan**; jangan refactor di atas baseline merah.
2. Lakukan perubahan.
3. Jalankan `{testCmd}` lagi — semua harus tetap lulus dengan perilaku identik.
4. Jalankan format + `{lintCmd}`.

**Refactor tidak boleh:**
- Mengubah perilaku yang teramati (input sama → output, navigasi, dan panggilan API sama)
- Menambah panggilan API, state, atau navigasi baru
- Mengubah key i18n atau testID (keduanya memutus test dan terjemahan secara diam-diam)

Kalau ternyata refactor butuh perubahan perilaku untuk "memperbaiki" sesuatu — stop, itu task
**fix** terpisah. Angkat ke user.

### Disiplin scope
Refactor hanya yang diminta. Jangan memperluas scope sambil jalan. Kalau melihat hal lain yang
perlu dirapikan, catat di response dan biarkan user yang memutuskan.

---

## Chore Guidelines

> Pintu masuk untuk task **chore**. Lewati Step 2–8.

### Scope
Config app mobile (Metro, Babel, app manifest, styling config, `package.json` app) → berlaku.
Config monorepo/root dan app non-mobile → di luar skill ini.

### Pemeriksaan setelah perubahan config

1. `{lintCmd}` — pastikan config tidak merusak lint.
2. Metro start bersih: `{startCmd}` — perhatikan error resolver.
3. `{testCmd}` — pastikan tidak ada test yang rusak.
4. Perubahan config styling/bundler: buka app, pastikan styling masih render.
5. Update dependency: baca changelog antara versi sekarang dan target sebelum update.
6. Perubahan manifest/build config: verifikasi build config masih valid.

> Kalau repo punya lebih dari satu app mobile, **jangan menjalankan dua Metro bersamaan**
> kecuali adapter menyatakan aman — cache bundler bersama adalah sumber bug styling yang
> hilang secara misterius.

### Aturan update dependency
Satu dep sekali jalan, jangan dibatch. Baca changelog dulu. Kalau breaking change butuh
perubahan kode, itu task **fix**/**refactor** terpisah. **Jangan pernah** menaikkan versi
framework/SDK sebagai chore rutin — itu butuh rencana migrasi tersendiri.

---

## Step 10 — Lint & format

Pembagian tugas tool ada di adapter §10. Yang portable:

- **Satu formatter memiliki formatting dan import order.** Jalankan yang itu; jangan
  menjalankan formatter lain "untuk berjaga-jaga".
- **Linter menangani aturan React Native / hooks**, bukan formatting.
- Kalau adapter menyebut sebuah formatter **tidak** dipakai (biasanya karena dimatikan di
  config supaya tidak bentrok), jangan menjalankannya. Diff-nya akan berubah lagi saat commit.

```bash
{formatCmd}     # format + import order
{lintCmd}       # lint app
```

Urutan import yang umum berlaku (verifikasi ke config project kalau ragu):
framework → library platform → package native/platform → third-party lain →
package internal/monorepo → absolute alias → relative.

---

### Lint sebelum commit, bukan setelah ditolak

Jalankan `{formatCmd}`, `{lintCmd}`, dan typecheck setelah setiap unit perubahan dan
**sebelum** commit. Hook pre-commit dan CI adalah jaring terakhir, bukan alat kerja: commit
yang ditolak hook berarti kode kotor sudah sempat dianggap selesai.

Formatter membungkus kode, **tidak membungkus string maupun komentar**. Class panjang, path
SVG, dan komentar yang melewati `max-len` harus dipecah manual — konstanta bernama atau
penggabungan string — atau dipindah ke berkas data (JSON) bila sebenarnya konten.

---

## Step 11 — Testing

### Coverage

Cek apakah project benar-benar menegakkan ambang coverage:

```bash
grep -n "coverageThreshold" {appRoot}/jest.config.*
```

**Kalau tidak ada `coverageThreshold`, jangan mengklaim memenuhi ambang apa pun** — tidak ada
perintah yang bisa membuktikannya dan tidak ada build yang gagal karenanya. Yang berlaku
sebagai gantinya, dan bisa dicek per-MR:

- Setiap **hook** dan **service** baru punya test. Di situlah keputusan berada; UI hanya merender.
- Setiap cabang error-mapping punya satu test (satu kode → satu respons).
- Jalankan `{testCmd}` sebelum menandai task selesai; laporkan angka coverage apa adanya.
- Yang wajar tidak di-unit-test: wrapper kamera, gesture handler, wrapper native module —
  cakup lewat E2E.

### Penempatan file test

Ikuti konvensi project (adapter §6 dan §11) — sebagian project memakai folder test di samping
kode, sebagian colocated. Cek pola yang berlaku sebelum menaruh file baru:

```bash
find {featuresRoot}/{feature-terdekat} -name '*.test.*' -o -name '*.spec.*'
```

### Yang diuji di tiap layer

- **Service/data** — mock wrapper HTTP; assert endpoint, method, dan pemetaan error.
- **Hook/logic** — render hook; assert tiap cabang error dan state hasil.
- **Komponen** — cari elemen lewat **testID, bukan string teks** (string berubah saat copy
  diperbarui atau locale berganti; testID adalah kontrak).

### E2E

Tool dan lokasi flow ada di adapter §11. Yang portable:

- Feature baru → tambah satu flow: happy path + satu error path utama.
- Locator = testID/accessibility id, bukan teks — alasan lain kenapa rename testID berbahaya.
- Kelompokkan flow mengikuti pengelompokan yang sudah ada; list dulu sebelum membuat folder baru.

---

## Step 12 — Konvensi commit

Format: `type(scope): deskripsi singkat`

`feat` screen/komponen/service/hook baru · `fix` perbaikan bug · `refactor` restrukturisasi
tanpa perubahan perilaku · `test` test · `chore` config/dep/tooling · `style` formatting saja ·
`docs` komentar/dokumen.

Scope = nama feature. Commit per unit logis, bukan sekali di akhir.

---

## Step 13 — Checklist sebelum menandai selesai

### Semua tier — 4 prinsip kerja

- [ ] Tidak ada kode, abstraksi, atau opsi di luar yang diminta
- [ ] Tidak ada asumsi yang diambil diam-diam — yang ambigu sudah ditanyakan
- [ ] Semua aturan yang berlaku (`CLAUDE.md`, `.claude/rules/`, skill, adapter) sudah dicek dan diikuti
- [ ] Hasil sudah dibandingkan satu per satu dengan permintaan dan docs yang berlaku

### Tier 1 — fix / edit satu file

- [ ] Adapter dibaca (Step 0)
- [ ] Pohon keputusan dokumen diikuti — tidak membuka dokumen yang tidak perlu
- [ ] Bug report: root cause di-triage (mobile vs backend) sebelum fix; tidak ada keputusan
      produk yang diambil diam-diam; tidak ada gejala backend yang ditambal di mobile
- [ ] File tidak melewati batas baris **karena perubahan ini**
- [ ] Tidak ada `style={{ ... }}` statis (inline hanya nilai runtime, dikomentari)
- [ ] Elemen interaktif yang disentuh tetap/mendapat `testID`; tidak ada testID yang di-rename
- [ ] Tidak ada logika bisnis yang ditambahkan di dalam JSX
- [ ] Tidak ada arrow function inline di prop JSX; tidak ada ternary JSX multi-baris
- [ ] Kode error dipetakan ke tepat satu respons (inline / toast / navigasi)
- [ ] Setiap request in-flight punya indikator loading
- [ ] `{formatCmd}` + `{lintCmd}` passes
- [ ] Commit `fix(scope): ...`

### Tier 2/3 — file baru / feature baru

- [ ] Adapter dibaca (Step 0)
- [ ] `ls {featuresRoot}` dijalankan sebelum mengklasifikasi tier
- [ ] Impl plan dibaca (kalau project punya alurnya); kalau tidak ada, user sudah ditanya
- [ ] "When to Stop and Ask" dilewati bersih — tidak ada ambiguitas yang diselesaikan diam-diam
- [ ] Komponen bersama dicek lebih dulu (perintah di adapter §7) sebelum membuat yang baru
- [ ] Screen baru memakai root wrapper wajib project (adapter §7) kalau ada
- [ ] Route baru didaftarkan sesuai cara project (adapter §3)
- [ ] Semua file baru di `{featuresRoot}/{feature}/` dengan subfolder sesuai adapter §6
- [ ] Tipe/validator/util diambil dari package bersama yang memang terpasang; tidak ada duplikat lokal
- [ ] String user-facing di semua locale; tidak ada hardcoded string
- [ ] Warna dari token; nama token diverifikasi ada di `{tokenFile}`
- [ ] Desain/prototype dicek untuk layout, copy, dan hierarki CTA
- [ ] Tidak ada file baru yang melewati batas baris
- [ ] Semua elemen interaktif punya `testID` dengan suffix yang benar
- [ ] Kondisi kompleks diekstrak ke variabel bernama
- [ ] Tidak ada arrow function inline di prop JSX — handler bernama di atas `return`
- [ ] Tidak ada ternary JSX multi-baris; daftar kosong lewat `ListEmptyComponent`
- [ ] Daftar berbasis data memakai `FlatList`/`SectionList` sebagai scroll container
- [ ] Bottom sheet memakai library yang ditunjuk adapter, bukan `Modal` rakitan
- [ ] `{formatCmd}` + `{lintCmd}` + typecheck dijalankan sebelum commit, bukan menunggu hook
- [ ] Tidak ada logika bisnis di UI — hanya di layer logic/data
- [ ] Error state berupa union literal; satu kode → satu respons
- [ ] Semua HTTP lewat wrapper; semua storage lewat wrapper
- [ ] Tidak ada state manager / router kedua yang diperkenalkan
- [ ] Test ditulis untuk tiap hook & service baru, termasuk tiap cabang error; `{testCmd}` hijau
- [ ] Flow E2E ditambahkan untuk screen baru (happy path + satu error path)
- [ ] `{formatCmd}` + `{lintCmd}` passes
- [ ] Commit konvensional

### Refactor

- [ ] `{testCmd}` dijalankan sebelum mulai — baseline hijau dikonfirmasi
- [ ] Tidak ada perubahan perilaku, API call, state, atau navigasi
- [ ] Key i18n dan testID tidak berubah
- [ ] Tidak ada pilihan arsitektur project yang diganti tanpa persetujuan user
- [ ] Scope terbatas pada yang diminta; temuan lain dilaporkan, bukan diperbaiki diam-diam
- [ ] `{testCmd}` + `{lintCmd}` passes
- [ ] Commit `refactor(scope): ...`

### Chore

- [ ] Hanya menyentuh config/dep yang jadi scope
- [ ] Changelog dibaca; breaking change dicatat; satu dep sekali jalan
- [ ] `{lintCmd}` + `{testCmd}` passes; Metro start bersih
- [ ] Commit `chore(scope): ...`

---

## Merawat skill ini

File ini portable dan **tidak boleh** diisi fakta project. Kalau kamu tergoda menambahkan nama
library, path, atau daftar apa pun ke sini — tempatnya di `.claude/mobile-stack.md`.

Aturan praktisnya: **kalau sebuah kalimat bisa menjadi salah karena orang lain mengubah kode,
kalimat itu tidak boleh ada di file ini.** Yang boleh tinggal di sini adalah aturan yang tetap
benar meski seluruh dependency project diganti.
