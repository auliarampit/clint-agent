#!/usr/bin/env bash
# Menyuntikkan 4 prinsip kerja + status setup project ke awal setiap sesi.
ROOT="${CLAUDE_PLUGIN_ROOT}"
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

# Project yang sudah menyalin prinsip kerja ke .claude/rules/ memuatnya sendiri; jangan dobel.
ctx=""
[ -f "$DIR/.claude/rules/working-principles.md" ] || ctx="$(cat "$ROOT/kit/working-principles.md")"

if [ -f "$DIR/.claude/clint.json" ]; then
  ctx+=$'\n\nclint aktif (`.claude/clint.json`). Satu modul/banyak PR: `/clint:jalankan`.'
else
  ctx+=$'\n\nclint belum disiapkan di project ini (`/clint:siapkan-project`).'
fi

jq -n --arg c "$ctx" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
