# kit/web

Skill, aturan, dan adapter untuk aplikasi web frontend. Portable: satu `SKILL.md` dipakai apa adanya di
semua project web; fakta stack tiap project ada di adapter.

```
web/
  SKILL.md              → .claude/skills/skill-web/SKILL.md      (konvensi inti, jangan diedit per project)
  referensi/            → .claude/skills/skill-web/referensi/    (dibaca hanya bila task menyentuhnya)
    aksesibilitas.md    WCAG 2.2 AA
    performa.md         Core Web Vitals dan bundle
    keamanan.md         keamanan sisi klien (OWASP)
    pola.md             form, tabel, dialog, upload, wizard, halaman terproteksi
  web-e2e.md            → .claude/rules/web-e2e.md
  adapters/TEMPLATE.md  → .claude/web-stack.md                   (diisi per project)
```

Pasang otomatis: `/clint:siapkan-project web`.

## Prinsip yang sama dengan kit mobile

- **Konvensi di skill, inventaris di adapter.** Kalimat yang bisa menjadi salah karena orang lain
  mengubah kode tidak boleh ada di `SKILL.md`. Cek sebelum menambah:
  `grep -nE "next|nuxt|vite|react-query|tanstack|tailwind|shadcn|redux|zustand|playwright|cypress|apps/" SKILL.md`
  idealnya tanpa hasil.
- **Larangan berbentuk konsistensi, bukan pilihan library.** "Satu mekanisme server state; yang dipakai
  project ini ada di adapter §4", bukan "pakai library X".
- **Hemat token.** Inti skill ringkas; pengetahuan mendalam dipisah ke `referensi/` dan hanya dibaca
  bila relevan.

Adapter yang sudah terisi milik project tetap tinggal di project masing-masing, tidak disimpan di kit.
