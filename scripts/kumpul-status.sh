#!/usr/bin/env bash
# Kumpulkan bahan penjaga dalam SATU panggilan: MR milik user, pipeline, branch tertinggal, worktree, disk.
# Pakai: kumpul-status.sh <dir-project>
dir="$1"; cfg="$dir/.claude/clint.json"; cd "$dir" || exit 0
base="$(jq -r '.baseBranch // "dev"' "$cfg" 2>/dev/null)"; cli="$(jq -r '.mr.cli // "glab"' "$cfg" 2>/dev/null)"
git fetch -q origin --prune 2>/dev/null
echo "### MR/PR milik Anda yang open"
if [ "$cli" = "gh" ]; then gh pr list --author @me --json number,title,url,statusCheckRollup,reviewDecision --limit 20 2>&1 | head -c 4000
else glab mr list --author=@me -F json 2>&1 | jq -r '.[]? | "!\(.iid) \(.title[0:70]) | pipeline=\(.head_pipeline.status // .pipeline.status // "-") | komentar=\(.user_notes_count) | \(.web_url)"' 2>/dev/null || echo "(glab gagal; lihat manual)"; fi
echo "### Branch lokal tertinggal dari origin/$base"
for b in $(git for-each-ref --format='%(refname:short)' refs/heads/ | head -30); do
  n="$(git rev-list --count "$b..origin/$base" 2>/dev/null)"; [ "${n:-0}" -gt 0 ] && echo "$b tertinggal $n"
done
echo "### Worktree"; git worktree list 2>/dev/null
echo "### Disk"; df -h ~ | tail -1
