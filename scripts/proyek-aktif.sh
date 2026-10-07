#!/usr/bin/env bash
# Daftar project aktif: dibuka di Claude Code dalam N hari terakhir (default 3) dan punya
# .claude/clint.json (di folder sesi itu sendiri atau satu tingkat di bawahnya).
hari="${1:-3}"
find "$HOME/.claude/projects" -maxdepth 2 -name '*.jsonl' -mtime "-$hari" 2>/dev/null \
  | while read -r f; do grep -m1 -o '"cwd":"[^"]*"' "$f" | sed 's/"cwd":"\(.*\)"/\1/'; done \
  | sort -u | while read -r d; do
      [ -f "$d/.claude/clint.json" ] && echo "$d"
      for c in "$d"/*/.claude/clint.json; do [ -f "$c" ] && dirname "$(dirname "$c")"; done
    done | sort -u
