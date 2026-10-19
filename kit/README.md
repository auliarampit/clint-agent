# kit/ — master yang disalin ke project

Isi folder ini **tidak aktif** dari plugin. `/clint:setup` menyalinnya ke `.claude/`
project, supaya rekan tim yang tidak memasang plugin tetap mendapat aturan yang sama lewat repo.

| Master | Tujuan di project | Catatan |
|---|---|---|
| `working-principles.md` | `.claude/rules/` | 4 prinsip kerja; juga disuntikkan hook di setiap sesi |
| `sonarqube.md` | `.claude/rules/` | standar quality gate SonarQube Badr; disalin bila project memakai SonarQube |
| `no-ai-slop.md` | `.claude/rules/` | tulisan dan kode tanpa AI slop; selalu disalin, juga disuntikkan hook bila belum ada |
| `clint.TEMPLATE.json` | `.claude/clint.json` | diisi dari hasil verifikasi |
| `mobile/SKILL.md` | `.claude/skills/skill-mobile/` | jangan diedit per project |
| `mobile/references/*.md` | `.claude/skills/skill-mobile/references/` | performa (target ketat), aksesibilitas, keamanan, pola feature |
| `mobile/mobile-e2e.md` | `.claude/rules/` | aturan flow E2E |
| `mobile/adapters/TEMPLATE.md` | `.claude/mobile-stack.md` | diisi per project; adapter terisi tinggal di project masing-masing, bukan di kit |
| `web/SKILL.md` | `.claude/skills/skill-web/` | konvensi inti web, jangan diedit per project |
| `web/references/*.md` | `.claude/skills/skill-web/references/` | aksesibilitas, performa (target ketat), keamanan, pola UI |
| `web/web-e2e.md` | `.claude/rules/` | aturan test E2E browser |
| `web/adapters/TEMPLATE.md` | `.claude/web-stack.md` | diisi per project |
| `backend/SKILL.md` | `.claude/skills/skill-backend/` | konvensi inti backend/API, jangan diedit per project |
| `backend/references/*.md` | `.claude/skills/skill-backend/references/` | kontrak API, data & migrasi, keamanan API, keandalan, performa (target ketat) |
| `backend/backend-test.md` | `.claude/rules/` | aturan test integrasi dan kontrak |
| `backend/adapters/TEMPLATE.md` | `.claude/backend-stack.md` | diisi per project |

Alasan pemisahan konvensi (skill) dan inventaris (adapter) ada di `mobile/README.md`.
Panduan pemakaian agent dan skill ada di README utama repo.
