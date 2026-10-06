# kit/mobile

Skill + rules React Native/Expo yang **portable**: satu SKILL.md dipakai apa adanya di semua
project mobile, dan tiap project mengisi satu file adapter berisi fakta stack-nya sendiri.

```
kit/
  working-principles.md          ← 4 aturan prioritas, copy apa adanya, WAJIB
  mobile/
    SKILL.md                     ← copy apa adanya, JANGAN diedit per project
    mobile-e2e.md                ← copy apa adanya
  adapters/
    TEMPLATE.md                  ← isi saat setup project baru (~10 menit)
```

## Cara pakai di project baru

```bash
# Cara otomatis: /clint:siapkan-project mobile
# Cara manual:
KIT=~/Desktop/clint/kit
mkdir -p .claude/skills/skill-mobile .claude/rules
cp "$KIT/mobile/SKILL.md"               .claude/skills/skill-mobile/
cp "$KIT/working-principles.md"         .claude/rules/
cp "$KIT/mobile/mobile-e2e.md"          .claude/rules/
cp "$KIT/mobile/adapters/TEMPLATE.md"   .claude/mobile-stack.md
```

Lalu isi `.claude/mobile-stack.md`. Tiap baris punya perintah verifikasinya sendiri —
**jalankan perintahnya, tempel jawabannya**, jangan diisi dari ingatan. Adapter yang sudah
terisi milik project lain bisa dibuka sebagai contoh, tapi tidak disimpan di kit.

Sesudah itu skill langsung jalan. Agent membaca adapter di Step 0 dan berhenti kalau
adapternya belum ada.

## Kenapa dipisah begini

Audit skill mobile sebuah project (2026-09-01) menemukan 15 klaim yang salah atau basi. Sebarannya:

| Kategori | Temuan | Portable? |
|---|---|---|
| Inventaris (route, feature, dep, komponen, isi config) | 11 | tidak pernah |
| Toolchain (formatter, coverage, tree E2E) | 3 | hanya kalau diparameterkan |
| **Konvensi** (layering, error mapping, styling, testID, scope) | **0** | **ya** |

Bagian yang tidak pernah salah dalam ~6 bulan adalah konvensi. Itu yang jadi SKILL.md.
Sisanya jadi perintah verifikasi atau baris adapter.

## Aturan emas saat merawat kit ini

> **Kalau sebuah kalimat bisa menjadi salah karena orang lain mengubah kode, kalimat itu
> tidak boleh ada di SKILL.md.**

Tempatnya di adapter, atau diganti perintah verifikasi. Skill yang salah tapi terdengar yakin
lebih berbahaya daripada skill yang tidak ada — agent tidak punya alasan untuk cross-check.

Cek cepat sebelum menambah apa pun ke SKILL.md:

```bash
grep -nE "apps/|@[a-z-]+/|zustand|redux|biome|prettier|maestro|detox|nativewind|expo-router" \
  mobile/SKILL.md
```

Idealnya nol hit. Ada hit = fakta project bocor ke file portable.

## Kenapa larangannya berbentuk "konsistensi", bukan "pilihan"

Skill lama menulis `❌ redux — dilarang`. Itu benar di satu project dan **salah total** di project lain,
yang memang memakai Redux Toolkit sebagai arsitektur resminya. Karena skill juga memberi izin
refactor untuk "pelanggaran arsitektur", agent akan merombak arsitektur yang benar dengan
percaya diri.

Bentuk yang portable tanpa kehilangan ketegasan:

```
❌ tidak portable : "Zustand. No Redux."
✅ portable+tegas : "SATU state manager per kebutuhan. Yang dipakai project ini ada di
                     adapter §4. Mencampur dua = ditolak review. Mau ganti? Itu keputusan
                     arsitektur — tanya user."
```

Larangan yang **tetap absolut di semua project** karena tidak menyangkut pilihan library:
tidak ada `style={{}}` statis · tidak ada hardcoded string · tidak ada logika bisnis di JSX ·
satu error code satu respons · tidak ada rename testID sembarangan · props `Readonly<>` ·
tidak ada HTTP/storage telanjang di kode feature · tidak ada arrow function inline di prop JSX ·
tidak ada ternary JSX multi-baris · daftar berbasis data memakai FlatList, bukan `map` · bottom sheet
lewat library yang ditunjuk adapter, bukan `Modal` rakitan · lint sebelum commit, bukan menunggu hook.

## Merawat adapter

Adapter adalah satu-satunya tempat yang boleh basi, dan itu disengaja: cakupannya kecil dan
tiap baris punya perintah untuk mengeceknya. Update `Terakhir diverifikasi` setiap kali
diperiksa. Kalau adapter bertentangan dengan filesystem, **filesystem menang** dan adapter
diperbaiki.
