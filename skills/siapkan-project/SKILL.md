---
name: siapkan-project
description: Memasang clint di sebuah project — menyalin prinsip kerja, skill, dan rules platform (mobile/web/backend) ke .claude/, membuat adapter stack dari template dengan nilai hasil verifikasi, dan membuat .claude/clint.json untuk alur PR otomatis. Juga untuk memeriksa apakah salinan di project tertinggal dari master kit. Pakai saat memulai project baru atau saat user meminta setup/sinkron clint.
argument-hint: [mobile|web|backend ...] | sinkron
---

# Siapkan project untuk clint

Master ada di `${CLAUDE_PLUGIN_ROOT}/kit/`:

```
kit/working-principles.md         → .claude/rules/working-principles.md
kit/clint.TEMPLATE.json           → .claude/clint.json              (diisi)
kit/mobile/SKILL.md               → .claude/skills/skill-mobile/SKILL.md
kit/mobile/mobile-e2e.md          → .claude/rules/mobile-e2e.md
kit/mobile/adapters/TEMPLATE.md   → .claude/mobile-stack.md         (diisi)
kit/web/SKILL.md                  → .claude/skills/skill-web/SKILL.md
kit/web/referensi/*.md            → .claude/skills/skill-web/referensi/
kit/web/web-e2e.md                → .claude/rules/web-e2e.md
kit/web/adapters/TEMPLATE.md      → .claude/web-stack.md            (diisi)
```

Skill dan rules platform **disalin** ke project (bukan dirujuk dari plugin) supaya rekan tim
yang tidak memasang plugin tetap mendapat aturan yang sama lewat repo.

## Mode setup

1. Deteksi surface yang ada (`app.json`/`app.config.*` → mobile; `next.config.*`/`vite.config.*`
   → web; server/API framework → backend). Konfirmasi ke user kalau ragu.
2. Surface yang belum punya master di `kit/` (cek `ls ${CLAUDE_PLUGIN_ROOT}/kit`) → beri tahu
   user bahwa kit untuk platform itu belum tersedia; pasang core saja.
3. Salin file master. **Jangan menimpa** file yang sudah ada di project; kalau berbeda,
   tampilkan `diff` dan tanya.
4. Isi adapter: jalankan perintah verifikasi di setiap baris template dan tempel hasilnya.
   Jangan mengisi dari ingatan. Baris yang tidak berlaku ditulis `TIDAK ADA`.
5. Isi `.claude/clint.json` dari template: base branch (`git remote show origin`), CLI MR
   (`glab`/`gh` sesuai host remote), `mr.mode` (`"mr"` default; tanya user bila tim biasa
   push langsung ke base → `"push-base"`), perintah lint/typecheck/test/e2e dari `package.json`,
   `formatFile` dari formatter yang benar-benar dipakai project.
   `docs.feedback`: folder feedback/bug QA (cari `ls -d ../docs/qa/feedback docs/qa 2>/dev/null`
   atau tanya); `TIDAK ADA` bila project tidak punya.
   `docs.pic`: dokumen pembagian tugas (sprint tracker/backlog berkolom nama PIC); `TIDAK ADA` bila
   satu orang mengerjakan semuanya.
   `relatedRepos`: repo git lain di folder induk yang menjadi sumber kerja (mis. `docs`,
   `designs`, `api`); cek dengan `ls ..` lalu `git -C ../<nama> rev-parse` dan tanyakan perannya
   bila tidak jelas dari nama. Monorepo tanpa repo pendamping → `[]`.
6. Tambahkan rujukan ke `CLAUDE.md` project (buat kalau belum ada): prinsip kerja, skill
   platform, dan adapter.
7. Tampilkan ringkasan file yang dibuat. **Jangan commit**; user yang memutuskan.

## Mode `sinkron`

Bandingkan setiap file salinan di project dengan masternya (`diff`). Laporkan yang berbeda.
Perbedaan di project bisa jadi perbaikan yang belum naik ke master. Tanya per file: tarik
dari master, naikkan ke master, atau biarkan.
