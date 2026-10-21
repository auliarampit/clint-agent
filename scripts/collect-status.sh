#!/usr/bin/env bash
# Kumpulkan bahan status-reporter dalam SATU panggilan: MR milik user, pipeline, MR Draft, branch tertinggal, worktree, disk.
# Pakai: collect-status.sh <dir-project>
dir="$1"; cfg="$dir/.claude/clint.json"; cd "$dir" || exit 0
base="$(jq -r '.baseBranch // "dev"' "$cfg" 2>/dev/null)"; cli="$(jq -r '.mr.cli // "glab"' "$cfg" 2>/dev/null)"
git fetch -q origin --prune 2>/dev/null
echo "### MR/PR milik Anda yang open"
if [ "$cli" = "gh" ]; then
  gh pr list --author @me --json number,title,url,isDraft,statusCheckRollup,reviewDecision --limit 20 2>&1 | head -c 4000
  draft="$(gh pr list --author @me --draft --json number --jq '.[].number' 2>/dev/null | sed 's/^/#/')"
else
  # `glab mr list` tidak memuat status pipeline; `glab mr view` memuat head_pipeline.
  mrs="$(glab mr list --author=@me -F json 2>/dev/null)"
  if [ -z "$mrs" ] || ! jq -e 'type == "array"' <<<"$mrs" >/dev/null 2>&1; then
    echo "(glab gagal; lihat manual)"
  else
    for iid in $(jq -r '.[0:20][].iid' <<<"$mrs"); do
      glab mr view "$iid" -F json 2>/dev/null | jq -r '"!\(.iid) \(if .draft then "[DRAFT] " else "" end)\(.title[0:70]) | pipeline=\(.head_pipeline.status // "-") | komentar=\(.user_notes_count) | \(.web_url)"'
    done
  fi
  draft="$(jq -r '.[]? | select(.draft) | "!\(.iid)"' <<<"$mrs" 2>/dev/null)"
fi
echo "### Menunggu peer review (standar Badr: > 3 jam eskalasi ke SA, > 5 jam ke engineer lead; dihitung sejak MR dibuat)"
umur='def jam: ((now - (sub("\\.[0-9]+"; "") | fromdateiso8601)) / 3600 * 10 | floor) / 10;
  def tanda(j): if j >= 5 then "🔴 > 5 jam: eskalasi ke engineer lead" elif j >= 3 then "⚠ > 3 jam: eskalasi ke SA" else "baru" end;'
if [ "$cli" = "gh" ]; then
  for peran in "--author @me" "--search review-requested:@me"; do
    gh pr list $peran --json number,title,createdAt,isDraft,reviewDecision,url --limit 20 2>/dev/null |
      jq -r "$umur"' .[] | select((.isDraft | not) and .reviewDecision != "APPROVED")
        | (.createdAt | jam) as $j | "#\(.number) \(.title[0:60]) | menunggu \($j) jam | \(tanda($j)) | \(.url)"' |
      sed "s/^/$( [ "$peran" = "--author @me" ] && echo "[MR Anda] " || echo "[Anda reviewer] ")/"
  done
else
  for peran in "--author=@me" "--reviewer=@me"; do
    glab mr list "$peran" -F json 2>/dev/null | jq -c '.[0:20][]? | select(.draft | not)' 2>/dev/null |
    while read -r mr; do
      iid="$(jq -r .iid <<<"$mr")"
      n="$(glab api "projects/:id/merge_requests/$iid/approvals" 2>/dev/null | jq '[.approved_by[]?] | length' 2>/dev/null)"
      [ "${n:-0}" -gt 0 ] && continue
      label="[MR Anda]"; [ "$peran" = "--reviewer=@me" ] && label="[Anda reviewer]"
      jq -r --arg l "$label" "$umur"' (.created_at | jam) as $j
        | "\($l) !\(.iid) \(.title[0:60]) | menunggu \($j) jam | \(tanda($j)) | \(.web_url)"' <<<"$mr"
    done
  done
fi
echo "### MR/PR Draft milik Anda (E2E mungkin tertunda: /clint:test e2e <nomor>)"
[ -n "$draft" ] && echo "$draft" | paste -sd' ' - || echo "(tidak ada)"
echo "### Branch lokal tertinggal dari origin/$base"
for b in $(git for-each-ref --format='%(refname:short)' refs/heads/ | head -30); do
  n="$(git rev-list --count "$b..origin/$base" 2>/dev/null)"; [ "${n:-0}" -gt 0 ] && echo "$b tertinggal $n"
done
echo "### Worktree"; git worktree list 2>/dev/null
echo "### Disk"; df -h ~ | tail -1
