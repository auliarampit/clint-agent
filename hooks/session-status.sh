#!/usr/bin/env bash
# Catat status setiap sesi Claude Code untuk menu bar (tanpa token):
# ~/.config/clint/sesi/<session_id>.json = {cwd, status, tugas, mulai, agents{id:tipe}, langkah, tahap}
input="$(cat)"
dir="$HOME/.config/clint/sesi"

# Tahap kerja untuk bilah progres menu bar (0 worktree, 1 implementasi, 2 tinjau, 3 test, 4 MR), dari
# jenis agent dan perintah Bash; tanpa token.
tahap_set(){
  local t; t="$(mktemp "$1.tmp.XXXXXX")" || return
  if jq --argjson l "$2" --arg t "$3" '.langkah=$l | .tahap=$t' "$1" > "$t"; then mv "$t" "$1"; else rm -f "$t"; fi
}

# Dipanggil di setiap tool call: cukup tandai sesi masih hidup, tanpa jq (kecuali perintah penanda tahap).
if [[ $input =~ \"hook_event_name\"[[:space:]]*:[[:space:]]*\"PostToolUse\" ]]; then
  [[ $input =~ \"session_id\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]] || exit 0
  f="$dir/${BASH_REMATCH[1]}.json"
  [ -f "$f" ] || exit 0
  touch "$f"
  # Notification (izin/pertanyaan) menandai sesi "menunggu"; tool sesi utama yang selesai berarti sudah dijawab
  # dan sesi bekerja lagi. Tool milik agent latar (ada agent_id) tidak dihitung.
  if [[ ! $input =~ \"agent_id\" ]] && grep -q '"status": *"menunggu"' "$f"; then
    t="$(mktemp "$f.tmp.XXXXXX")" &&
      { jq --argjson t "$(date +%s)" '.status="bekerja" | .update=$t' "$f" > "$t" && mv "$t" "$f" || rm -f "$t"; }
  fi
  pola='"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)"'
  if [[ $input =~ \"tool_name\"[[:space:]]*:[[:space:]]*\"Bash\" ]] && [[ $input =~ $pola ]]; then
    c="${BASH_REMATCH[1]}"
    # Hanya perintah yang benar-benar dijalankan (awal baris atau setelah && ; |), bukan teks di dalam skrip.
    awal='(^|&&|;|\|\||\\n)[[:space:]]*'
    if [[ $c =~ ${awal}(glab\ mr\ create|gh\ pr\ create|git(\ -C\ [^ ]+)?\ push) ]]; then tahap_set "$f" 4 "MR"
    elif [[ $c =~ ${awal}git(\ -C\ [^ ]+)?\ worktree\ add ]]; then tahap_set "$f" 0 "worktree"; fi
  fi
  exit 0
fi

mkdir -p "$dir"
log="$HOME/.config/clint/debug.log"
if [ -f "$HOME/.config/clint/debug" ]; then
  printf '%s\n' "$input" >> "$log"
  if [ "$(wc -c < "$log")" -gt 5242880 ]; then
    t="$(mktemp "$log.tmp.XXXXXX")" && tail -c 1048576 "$log" > "$t" && mv "$t" "$log"
  fi
fi

IFS=$'\x1f' read -r ev sid cwd tp aid atype bg p < <(jq -r '[.hook_event_name // "", .session_id // "", .cwd // "",
  .transcript_path // "", (.agent_id // .tool_use_id // "?"), (.agent_type // .subagent_type // "agent"),
  (.background_tasks // [] | length | tostring), ((.prompt // "") | gsub("[\n\r\u001f]"; " ") | .[0:90])] | join("\u001f")' <<<"$input")
[ -n "$sid" ] || exit 0
f="$dir/$sid.json"; now="$(date +%s)"
ubah(){
  local t; t="$(mktemp "$f.tmp.XXXXXX")" || return
  if jq "$@" "$f" > "$t"; then mv "$t" "$f"; else rm -f "$t"; fi
}
if [ ! -f "$f" ]; then
  t="$(mktemp "$f.tmp.XXXXXX")" &&
    jq -n --arg c "$cwd" --argjson t "$now" '{cwd:$c,status:"siap",tugas:"",mulai:$t,update:$t,agents:{}}' > "$t" &&
    mv "$t" "$f"
fi
# Simpan path transkrip sekali: menu bar memakai waktu ubahnya sebagai tanda sesi masih hidup.
[ -n "$tp" ] && [ "$(jq -r '.transkrip // empty' "$f")" != "$tp" ] && ubah --arg t "$tp" '.transkrip=$t'
case "$ev" in
  UserPromptSubmit)
    # Pesan sistem/agent (diawali "<") bukan tugas baru: status saja, tugas lama dipertahankan.
    if [[ "$p" == \<* ]]; then ubah --argjson t "$now" '.status="bekerja" | .update=$t'
    else ubah --arg p "$p" --argjson t "$now" '.status="bekerja" | .tugas=$p | .mulai=$t | .update=$t | del(.langkah, .tahap)'; fi ;;
  SubagentStart)
    ubah --arg i "$aid" --arg a "$atype" --argjson t "$now" '.agents[$i]=$a | .update=$t'
    a="${atype#clint:}"
    case "$a" in
      planner|solution-architect|bug-investigator) tahap_set "$f" 0 "rencana · $a" ;;
      developer|pipeline-fixer) tahap_set "$f" 1 "implementasi · $a" ;;
      code-reviewer|conformance-reviewer|*-auditor) tahap_set "$f" 2 "tinjau · $a" ;;
      e2e-tester) tahap_set "$f" 3 "test · $a" ;;
    esac ;;
  SubagentStop) ubah --arg i "$aid" --argjson t "$now" 'del(.agents[$i]) | .update=$t' ;;
  Notification) ubah --argjson t "$now" '.status="menunggu" | .update=$t' ;;
  # background_tasks juga berisi tugas yang bukan agent (mis. pemantauan artifact), jadi tidak dipakai
  # untuk menahan status "bekerja". Agent latar yang sungguhan tetap tercatat di .agents lewat
  # SubagentStart/SubagentStop; yang lain dikosongkan.
  # Giliran selesai: perbarui butir laporan dari status MR (merged hilang, MR baru pindah ke review), maks 1x/mnt.
  Stop) cap="$HOME/.config/clint/mr-dicek"
        if [ -z "$(find "$cap" -mmin -1 2>/dev/null)" ]; then
          touch "$cap"; ( python3 "$(dirname "$0")/../scripts/update-report.py" periksa-mr >/dev/null 2>&1 & )
        fi
        if [ "${bg:-0}" -gt 0 ]; then ubah --argjson t "$now" '.status="selesai" | .update=$t'
        else ubah --argjson t "$now" '.status="selesai" | .agents={} | .update=$t'; fi ;;
  SessionEnd) rm -f "$f" ;;
esac
find "$dir" \( -name '*.json' -o -name '*.tmp*' \) -mtime +1 -delete 2>/dev/null
exit 0
