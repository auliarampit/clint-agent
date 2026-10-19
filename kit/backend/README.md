# kit/backend

Skill, aturan, dan adapter untuk service backend/API. Portable: satu `SKILL.md` dipakai apa adanya di
semua project backend; fakta stack tiap project ada di adapter.

```
backend/
  SKILL.md              → .claude/skills/skill-backend/SKILL.md     (konvensi inti, jangan diedit per project)
  references/            → .claude/skills/skill-backend/references/   (dibaca hanya bila task menyentuhnya)
    kontrak-api.md      REST, envelope error, paginasi, idempotensi, perubahan merusak
    data.md             migrasi aman tanpa downtime, integritas, transaksi, query
    keamanan-api.md     OWASP API Security Top 10 (2023)
    keandalan.md        panggilan keluar, job, event/outbox, cache, observability
  backend-test.md       → .claude/rules/backend-test.md
  adapters/TEMPLATE.md  → .claude/backend-stack.md                  (diisi per project)
```

Pasang otomatis: `/clint:setup backend`.

Prinsip sama dengan kit mobile dan web: konvensi di skill, inventaris di adapter; larangan berbentuk
konsistensi, bukan pilihan library; inti ringkas, pengetahuan mendalam di `references/`. Cek sebelum
menambah ke `SKILL.md`:
`grep -inE "express|nest|fastify|hono|prisma|drizzle|typeorm|sequelize|postgres|mysql|mongo|redis|kafka|rabbit|bull|apps/" SKILL.md`
idealnya tanpa hasil.
