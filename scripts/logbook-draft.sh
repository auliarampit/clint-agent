#!/usr/bin/env bash
# Bahan satu entri logbook harian: commit dan MR milik user pada tanggal itu di repo project + relatedRepos,
# path file logbook bulan itu, dan apakah entri tanggal itu sudah ada. Ringkasan ditulis model, bukan skrip.
# Pakai: logbook-draft.sh <dir-project> [YYYY-MM-DD]
dir="$1"; tgl="${2:-$(date +%F)}"; cfg="$dir/.claude/clint.json"; cd "$dir" || exit 1
email="$(git config user.email)"; nama="$(git config user.name)"
cli="$(jq -r '.mr.cli // "glab"' "$cfg" 2>/dev/null)"
log="$(jq -r '.docs.logbook // empty' "$cfg" 2>/dev/null)"
lang="$(jq -r '.docs.language // "en"' "$cfg" 2>/dev/null)"

echo "### Entri"
echo "tanggal=$tgl penulis=$nama <$email> bahasa=$lang"
if [ -z "$log" ] || [ "$log" = "TIDAK ADA" ]; then
  echo "file=(docs.logbook belum diisi di .claude/clint.json)"
else
  f="$log/${tgl:0:7}.md"
  echo "file=$f"
  if grep -q "^## $tgl · $nama\$" "$f" 2>/dev/null; then echo "sudah ada: entri $tgl untuk $nama (perbarui, jangan dobel)"; fi
fi

echo "### Commit $tgl"
repos=("$dir")
while IFS= read -r p; do [ -n "$p" ] && repos+=("$dir/$p"); done < <(jq -r '.relatedRepos[]?.path' "$cfg" 2>/dev/null)
for r in "${repos[@]}"; do
  git -C "$r" rev-parse --git-dir >/dev/null 2>&1 || continue
  out="$(git -C "$r" log --all --no-merges --author="$email" --since="$tgl 00:00" --until="$tgl 23:59:59" \
    --format='%h %s' 2>/dev/null | head -40)"
  [ -n "$out" ] && printf '[%s]\n%s\n' "$(basename "$(git -C "$r" rev-parse --show-toplevel)")" "$out"
done

echo "### MR/PR dibuat atau di-merge $tgl"
# Waktu API dalam UTC; dibandingkan dalam tanggal lokal supaya MR pagi hari WIB tidak jatuh ke kemarin.
hari='def hari: if . then sub("\\.[0-9]+"; "") | fromdateiso8601 | localtime | strftime("%Y-%m-%d") else "" end;'
if [ "$cli" = "gh" ]; then
  gh pr list --author @me --state all --limit 50 --json number,title,state,createdAt,mergedAt,url 2>/dev/null |
    jq -r --arg d "$tgl" "$hari"' .[] | select((.createdAt | hari) == $d or (.mergedAt | hari) == $d)
      | "#\(.number) \(.state) \(.title[0:70]) | \(.url)"'
else
  glab mr list --author=@me --all -F json 2>/dev/null |
    jq -r --arg d "$tgl" "$hari"' .[]? | select((.created_at | hari) == $d or (.merged_at | hari) == $d)
      | "!\(.iid) \(.state)\(if .draft then " [DRAFT]" else "" end) \(.title[0:70]) | \(.web_url)"'
fi
