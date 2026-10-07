# kit/ — master yang disalin ke project

Isi folder ini **tidak aktif** dari plugin. `/clint:siapkan-project` menyalinnya ke `.claude/`
project, supaya rekan tim yang tidak memasang plugin tetap mendapat aturan yang sama lewat repo.

| Master | Tujuan di project | Catatan |
|---|---|---|
| `working-principles.md` | `.claude/rules/` | 4 prinsip kerja; juga disuntikkan hook di setiap sesi |
| `clint.TEMPLATE.json` | `.claude/clint.json` | diisi dari hasil verifikasi |
| `mobile/SKILL.md` | `.claude/skills/skill-mobile/` | jangan diedit per project |
| `mobile/mobile-e2e.md` | `.claude/rules/` | aturan flow E2E |
| `mobile/adapters/TEMPLATE.md` | `.claude/mobile-stack.md` | diisi per project; adapter terisi tinggal di project masing-masing, bukan di kit |
| `web/SKILL.md` | `.claude/skills/skill-web/` | konvensi inti web, jangan diedit per project |
| `web/referensi/*.md` | `.claude/skills/skill-web/referensi/` | aksesibilitas, performa, keamanan, pola UI |
| `web/web-e2e.md` | `.claude/rules/` | aturan test E2E browser |
| `web/adapters/TEMPLATE.md` | `.claude/web-stack.md` | diisi per project |
| `backend/` | — | Fase 3 |

Alasan pemisahan konvensi (skill) dan inventaris (adapter) ada di `mobile/README.md`.
Panduan pemakaian agent dan skill ada di README utama repo.
