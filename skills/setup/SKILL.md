---
name: setup
description: Memasang clint di sebuah project — menyalin prinsip kerja, skill, dan rules platform (mobile/web/backend) serta standar SonarQube ke .claude/, membuat adapter stack dari template dengan nilai hasil verifikasi, dan membuat .claude/clint.json. Juga untuk menyinkronkan salinan di project dengan master kit (`sync`) dan mengganti bahasa pribadi (`language en|id`). Pakai saat memulai project baru, saat user meminta setup/sinkron clint, atau saat ingin ganti bahasa.
argument-hint: [mobile|web|backend ...] | sync | language <en|id>
---

# Setup clint di project

Master ada di `${CLAUDE_PLUGIN_ROOT}/kit/`:

```
kit/working-principles.md         → .claude/rules/working-principles.md
kit/sonarqube.md                  → .claude/rules/sonarqube.md       (bila project memakai SonarQube)
kit/clint.TEMPLATE.json           → .claude/clint.json              (diisi)
kit/mobile/SKILL.md               → .claude/skills/skill-mobile/SKILL.md
kit/mobile/references/*.md        → .claude/skills/skill-mobile/references/
kit/mobile/mobile-e2e.md          → .claude/rules/mobile-e2e.md
kit/mobile/adapters/TEMPLATE.md   → .claude/mobile-stack.md         (diisi)
kit/web/SKILL.md                  → .claude/skills/skill-web/SKILL.md
kit/web/references/*.md           → .claude/skills/skill-web/references/
kit/web/web-e2e.md                → .claude/rules/web-e2e.md
kit/web/adapters/TEMPLATE.md      → .claude/web-stack.md            (diisi)
kit/backend/SKILL.md              → .claude/skills/skill-backend/SKILL.md
kit/backend/references/*.md       → .claude/skills/skill-backend/references/
kit/backend/backend-test.md       → .claude/rules/backend-test.md
kit/backend/adapters/TEMPLATE.md  → .claude/backend-stack.md        (diisi)
```

Skill dan rules platform **disalin** ke project (bukan dirujuk dari plugin) supaya rekan tim
yang tidak memasang plugin tetap mendapat aturan yang sama lewat repo.

## Bahasa

Ada dua setelan yang berbeda:

| Setelan | Tempat | Mengatur | Default |
|---|---|---|---|
| Bahasa pribadi | `~/.config/clint/user.json` → `language` | tanya jawab, laporan, kabar suara, file rencana | `en` |
| Bahasa dokumen project | `.claude/clint.json` → `docs.language` | dokumen project baru (feedback QA, README, CHANGELOG, ADR, dokumen requirement) | `en` |

Isi file instruksi clint (skill, agent, rules) selalu bahasa Indonesia; yang berganti hanya keluarannya.

## Mode setup

1. Deteksi surface yang ada (`app.json`/`app.config.*` → mobile; `next.config.*`/`vite.config.*`
   → web; server/API framework → backend). Konfirmasi ke user kalau ragu.
2. Surface yang belum punya master di `kit/` (cek `ls ${CLAUDE_PLUGIN_ROOT}/kit`) → beri tahu
   user bahwa kit untuk platform itu belum tersedia; pasang core saja.
3. Salin file master. **Jangan menimpa** file yang sudah ada di project; kalau berbeda,
   tampilkan `diff` dan tanya. `sonarqube.md` disalin bila ada `sonar-project.properties` atau
   job sonar di CI (`grep -il sonar .gitlab-ci.yml ci/*.yml .github/workflows/* 2>/dev/null`); tidak
   ada → tanya user apakah project akan memakai SonarQube.
4. Isi adapter: jalankan perintah verifikasi di setiap baris template dan tempel hasilnya.
   Jangan mengisi dari ingatan. Baris yang tidak berlaku ditulis `TIDAK ADA`.
5. Isi `.claude/clint.json` dari template: base branch (`git remote show origin`), CLI MR
   (`glab`/`gh` sesuai host remote), `mr.mode` (`"mr"` default; tanya user bila tim biasa
   push langsung ke base → `"push-base"`), perintah lint/typecheck/test/e2e dari `package.json`,
   `formatFile` dari formatter yang benar-benar dipakai project.
   `ciOnMr`: cek yang benar-benar dijalankan CI pada MR (baca `.gitlab-ci.yml`/`ci/*.yml`/`.github/workflows/*`:
   job dan `rules`-nya); job yang hanya jalan terjadwal/di branch utama tidak dihitung. `surfaces[].testRelated`:
   perintah test untuk file yang berubah dari test runner project (jest `--findRelatedTests`, vitest `related --run`),
   `TIDAK ADA` bila runner tidak mendukung.
   `docs.language`: bahasa dokumen yang sudah ada di `docs.requirements` (`id` atau `en`); belum ada
   dokumen → `en`. Sebutkan nilainya di ringkasan supaya user bisa mengubahnya.
   `docs.feedback`: folder feedback/bug QA (cari `ls -d ../docs/qa/feedback docs/qa 2>/dev/null`
   atau tanya); `TIDAK ADA` bila project tidak punya.
   `docs.pic`: dokumen pembagian tugas (sprint tracker/backlog berkolom nama PIC); `TIDAK ADA` bila
   satu orang mengerjakan semuanya.
   `relatedRepos`: repo git lain di folder induk yang menjadi sumber kerja (mis. `docs`,
   `designs`, `api`); cek dengan `ls ..` lalu `git -C ../<nama> rev-parse` dan tanyakan perannya
   bila tidak jelas dari nama. Monorepo tanpa repo pendamping → `[]`.
6. Tambahkan rujukan ke `CLAUDE.md` project (buat kalau belum ada): prinsip kerja, skill
   platform, adapter, dan `sonarqube.md` bila disalin.
7. Belum ada `~/.config/clint/user.json` → tanya bahasa pribadi user sekali (English / Bahasa
   Indonesia) dan tulis `{"name": [], "language": "<en|id>"}`.
8. Tampilkan ringkasan file yang dibuat. **Jangan commit**; user yang memutuskan.

## Mode `sync`

1. **Nama lama clint v1** di project → tawarkan rename dengan `git mv` sebelum membandingkan:

   | Lama (v1) | Baru (v2) |
   |---|---|
   | `.claude/skills/skill-web/referensi/aksesibilitas.md` | `.claude/skills/skill-web/references/accessibility.md` |
   | `.claude/skills/skill-web/referensi/performa.md` | `.claude/skills/skill-web/references/performance.md` |
   | `.claude/skills/skill-web/referensi/keamanan.md` | `.claude/skills/skill-web/references/security.md` |
   | `.claude/skills/skill-web/referensi/pola.md` | `.claude/skills/skill-web/references/patterns.md` |
   | `.claude/skills/skill-backend/referensi/kontrak-api.md` | `.claude/skills/skill-backend/references/api-contract.md` |
   | `.claude/skills/skill-backend/referensi/data.md` | `.claude/skills/skill-backend/references/data.md` |
   | `.claude/skills/skill-backend/referensi/keamanan-api.md` | `.claude/skills/skill-backend/references/api-security.md` |
   | `.claude/skills/skill-backend/referensi/keandalan.md` | `.claude/skills/skill-backend/references/reliability.md` |

   Cari juga rujukan nama lama di file project (`grep -rnE "clint:(jalankan|cek|tinjau|siapkan-project)|referensi/" .claude CLAUDE.md`)
   dan tawarkan penggantinya: `jalankan` → `develop`, `cek` → `status`, `tinjau` → `review`,
   `siapkan-project` → `setup`.
2. **Ukuran adapter**: `wc -l -c .claude/*-stack.md`. Lebih dari 300 baris / 25 KB → tunjukkan bagian yang
   berupa jurnal (catatan keputusan per modul, riwayat, log selisih) dan tawarkan memindahkannya ke ADR atau
   file rencana dengan tautan dari adapter. Pindahkan hanya bagian yang disetujui user.
3. Bandingkan setiap file salinan di project dengan masternya (`diff`). Laporkan yang berbeda.
   Perbedaan di project bisa jadi perbaikan yang belum naik ke master. Tanya per file: tarik
   dari master, naikkan ke master, atau biarkan.
4. File master yang belum ada di project (mis. `sonarqube.md`, field `docs.language`, `ciOnMr`,
   `surfaces[].testRelated`) → tawarkan
   untuk ditambahkan.

## Mode `language <en|id>`

Tulis `language` ke `~/.config/clint/user.json` (buat bila belum ada; pertahankan field lain), lalu
beri tahu bahwa setelan berlaku mulai sesi berikutnya. Untuk sesi ini, langsung pakai bahasa baru.
Bahasa dokumen project diubah lewat `docs.language` di `.claude/clint.json`, bukan lewat mode ini.
