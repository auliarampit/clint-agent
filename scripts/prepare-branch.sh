#!/usr/bin/env bash
# Siapkan path kerja satu PR: repo utama bila bebas, worktree bila dipakai atau --worktree (PR paralel).
# Pakai: prepare-branch.sh <repo> <branch> <base-ref> [sid] [--worktree]
# Keluaran: path=<path kerja> mode=repo|worktree asal=<branch asal user> (asal hanya untuk mode repo).
repo="$1"; branch="$2"; base="$3"; sid="$4"; paksa=""; [ "$5" = "--worktree" ] || [ "$4" = "--worktree" ] && paksa=1
[ "$4" = "--worktree" ] && sid=""
[ -n "$repo" ] && [ -n "$branch" ] && [ -n "$base" ] || { echo "pakai: prepare-branch.sh <repo> <branch> <base-ref> [sid] [--worktree]"; exit 1; }
R="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo" || exit 1
git fetch -q origin --prune

if [ -z "$paksa" ] && sibuk="$(bash "$R/scripts/repo-busy.sh" . "$sid")"; then
  asal="$(git branch --show-current)"
  git switch -q -c "$branch" "$base" || exit 1
  echo "path=$(pwd) mode=repo asal=$asal"
  exit 0
fi
[ -n "$paksa" ] || echo "alasan_worktree=${sibuk#dipakai: }"

root="$(jq -r '.worktreeRoot // empty' .claude/clint.json 2>/dev/null)"
[ -n "$root" ] || root="../$(basename "$(pwd)")-worktrees"
wt="$root/${branch//\//-}"
git worktree add -q -b "$branch" "$wt" "$base" || exit 1
wt="$(cd "$wt" && pwd)"

for lock in bun.lock bun.lockb package-lock.json yarn.lock pnpm-lock.yaml; do
  [ -f "$lock" ] && cmp -s "$lock" "$wt/$lock" || continue
  find . -maxdepth 3 -name node_modules -type d -prune -not -path './.git/*' 2>/dev/null | while read -r nm; do
    [ -d "$wt/$(dirname "$nm")" ] && [ ! -e "$wt/$nm" ] && ln -s "$(pwd)/${nm#./}" "$wt/$nm"
  done
  echo "node_modules=ditautkan"
  break
done
echo "path=$wt mode=worktree"
