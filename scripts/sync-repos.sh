#!/usr/bin/env bash
# Tarik repo kerja dan semua relatedRepos (docs, design, api) dalam SATU panggilan, tanpa token. Dipakai status,
# review, dan develop (lewat preflight) sebelum membaca apa pun, supaya semua repo terbaru.
# Pakai: sync-repos.sh <dir-project>
# Pull --ff-only hanya bila working tree bersih dan sedang di branch target; selain itu cukup fetch (dibandingkan
# dengan origin/<branch>). Hasil disimpan 2 menit (.git/clint-sync): pemanggilan berikutnya, mis. dari
# collect-changes/collect-status yang jalan paralel, tidak menarik ulang dan tidak berebut lock git.
# Keluaran: repo=<nama> status=<terbaru|fetch-saja|gagal-tarik|tidak-ada> [alasan=…] [commit=…]
dir="${1:-$PWD}"; cfg="$dir/.claude/clint.json"
[ -f "$cfg" ] || { echo "error=.claude/clint.json tidak ada di $dir"; exit 0; }
cd "$dir" || exit 0
tanda="$(git rev-parse --git-common-dir 2>/dev/null)/clint-sync"
if [ -f "$tanda" ] && [ -z "$(find "$tanda" -mmin +2 2>/dev/null)" ]; then cat "$tanda"; exit 0; fi

tarik() {  # $1 nama, $2 path, $3 branch
  local p
  p="$(cd "$dir" && cd "$2" 2>/dev/null && pwd)" || { echo "repo=$1 status=tidak-ada path=$2"; return; }
  git -C "$p" rev-parse --git-dir >/dev/null 2>&1 || { echo "repo=$1 status=tidak-ada alasan=bukan-repo-git"; return; }
  git -C "$p" fetch -q --prune origin 2>/dev/null || { echo "repo=$1 status=gagal-tarik alasan=fetch-gagal"; return; }
  if [ -n "$(git -C "$p" status --porcelain 2>/dev/null | head -1)" ]; then
    echo "repo=$1 status=fetch-saja alasan=working-tree-kotor"
  elif [ "$(git -C "$p" branch --show-current)" != "$3" ]; then
    echo "repo=$1 status=fetch-saja alasan=bukan-di-$3"
  elif git -C "$p" merge -q --ff-only "origin/$3" 2>/dev/null; then
    echo "repo=$1 status=terbaru commit=$(git -C "$p" log -1 --format='%h %cs')"
  else
    echo "repo=$1 status=gagal-tarik alasan=tidak-bisa-fast-forward"
  fi
}

hasil="$(
  tarik "kerja" "." "$(jq -r '.baseBranch // "dev"' "$cfg")" &
  while IFS=$'\t' read -r nama path branch; do
    [ -n "$nama" ] && tarik "$nama" "$path" "$branch" &
  done < <(jq -r '.relatedRepos[]? | [.name, .path, (.branch // "main")] | @tsv' "$cfg")
  wait
)"
printf '%s\n' "$hasil" | tee "$tanda"
