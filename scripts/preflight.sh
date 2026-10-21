#!/usr/bin/env bash
# Prasyarat develop dalam SATU panggilan: fetch, tarik relatedRepos yang bersih, sisa disk → paralelisme, surfaces.
# Pakai: preflight.sh <repo>   Keluaran key=value; exit 1 bila clint.json tidak ada, exit 2 bila disk < 5 GB.
dir="${1:-$PWD}"; cfg="$dir/.claude/clint.json"
[ -f "$cfg" ] || { echo "error=.claude/clint.json tidak ada; jalankan /clint:setup"; exit 1; }
cd "$dir" || exit 1
git fetch -q origin --prune 2>&1 | sed 's/^/fetch_error=/'
echo "base=$(jq -r '.baseBranch // "dev"' "$cfg")"
echo "mr_mode=$(jq -r '.mr.mode // "mr"' "$cfg")"
echo "mr_cli=$(jq -r '.mr.cli // "glab"' "$cfg")"
echo "mr_target=$(jq -r '.mr.targetBranch // .baseBranch // "dev"' "$cfg")"
echo "worktree_root=$(jq -r '.worktreeRoot // empty' "$cfg")"
jq -r '.surfaces[]? | "surface=\(.name) root=\(.root // ".")"' "$cfg"
while IFS=$'\t' read -r name path branch; do
  [ -n "$name" ] || continue
  p="$(cd "$dir" && cd "$path" 2>/dev/null && pwd)" || { echo "related=$name status=tidak-ada path=$path"; continue; }
  if [ -n "$(git -C "$p" status --porcelain 2>/dev/null | head -1)" ]; then
    echo "related=$name status=kotor-tidak-ditarik"
  elif git -C "$p" pull -q --ff-only origin "$branch" 2>/dev/null; then
    echo "related=$name status=terbaru commit=$(git -C "$p" log -1 --format='%h %cs')"
  else
    echo "related=$name status=gagal-tarik"
  fi
done < <(jq -r '.relatedRepos[]? | [.name, .path, (.branch // "main")] | @tsv' "$cfg")
gb="$(df -g ~ | awk 'NR==2 {print $4}')"
if [ "$gb" -ge 20 ]; then par=3; elif [ "$gb" -ge 5 ]; then par=1; else par=0; fi
echo "disk_gb=$gb paralel=$par"
[ "$par" -gt 0 ] || { echo "error=sisa disk < 5 GB"; exit 2; }
