#!/usr/bin/env bash
# SessionEnd: simpan transkrip sesi ke mempalace di wing project (memory.wing di .claude/clint.json).
# Mine embeddinggemma butuh menit untuk transkrip besar, jadi dijalankan terlepas dari sesi.
input="$(cat)"
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
wing="$(jq -r '.memory.wing // empty' "$DIR/.claude/clint.json" 2>/dev/null)"
tp="$(jq -r '.transcript_path // empty' <<<"$input" 2>/dev/null)"
[ -n "$wing" ] && [ "$wing" != "TIDAK ADA" ] && [ -f "$tp" ] || exit 0
command -v mempalace >/dev/null 2>&1 || exit 0
mkdir -p "$HOME/Library/Logs/clint"
nohup mempalace mine "$tp" --mode convos --wing "$wing" >>"$HOME/Library/Logs/clint/mempalace.log" 2>&1 </dev/null &
exit 0
