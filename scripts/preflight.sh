#!/usr/bin/env bash
# Prasyarat develop dalam SATU panggilan: tarik repo kerja dan relatedRepos (sync-repos.sh), sisa disk → paralelisme, surfaces.
# Pakai: preflight.sh <repo>   Keluaran key=value; exit 1 bila clint.json tidak ada, exit 2 bila disk < 5 GB.
sini="$(cd "$(dirname "$0")" && pwd)"
dir="${1:-$PWD}"; cfg="$dir/.claude/clint.json"
[ -f "$cfg" ] || { echo "error=.claude/clint.json tidak ada; jalankan /clint:setup"; exit 1; }
cd "$dir" || exit 1
echo "base=$(jq -r '.baseBranch // "dev"' "$cfg")"
echo "mr_mode=$(jq -r '.mr.mode // "mr"' "$cfg")"
echo "mr_cli=$(jq -r '.mr.cli // "glab"' "$cfg")"
echo "mr_target=$(jq -r '.mr.targetBranch // .baseBranch // "dev"' "$cfg")"
echo "worktree_root=$(jq -r '.worktreeRoot // empty' "$cfg")"
jq -r '.surfaces[]? | "surface=\(.name) root=\(.root // ".")"' "$cfg"
# Adapter > 25 KB dibaca utuh oleh setiap developer: tandai supaya isi jurnalnya dipindah lewat /clint:setup sync.
jq -r '.surfaces[]?.adapter // empty' "$cfg" | while read -r ad; do
  [ -f "$ad" ] && kb=$(( $(wc -c <"$ad") / 1024 )) && [ "$kb" -gt 25 ] && echo "adapter_besar=$ad ${kb}KB"
done
bash "$sini/sync-repos.sh" "$dir" | sed 's/^repo=/related=/'
gb="$(df -g ~ | awk 'NR==2 {print $4}')"
if [ "$gb" -ge 20 ]; then par=3; elif [ "$gb" -ge 5 ]; then par=1; else par=0; fi
echo "disk_gb=$gb paralel=$par"
[ "$par" -gt 0 ] || { echo "error=sisa disk < 5 GB"; exit 2; }
