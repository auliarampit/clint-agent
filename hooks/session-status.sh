#!/usr/bin/env bash
# Catat status setiap sesi Claude Code untuk menu bar (tanpa token):
# ~/.config/clint/sesi/<session_id>.json = {cwd, status, tugas, mulai, agents{id:tipe}}
input="$(cat)"
dir="$HOME/.config/clint/sesi"

# Dipanggil di setiap tool call: cukup tandai sesi masih hidup, tanpa jq.
if [[ $input =~ \"hook_event_name\"[[:space:]]*:[[:space:]]*\"PostToolUse\" ]]; then
  [[ $input =~ \"session_id\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]] &&
    [ -f "$dir/${BASH_REMATCH[1]}.json" ] && touch "$dir/${BASH_REMATCH[1]}.json"
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
    else ubah --arg p "$p" --argjson t "$now" '.status="bekerja" | .tugas=$p | .mulai=$t | .update=$t'; fi ;;
  SubagentStart) ubah --arg i "$aid" --arg a "$atype" --argjson t "$now" '.agents[$i]=$a | .update=$t' ;;
  SubagentStop) ubah --arg i "$aid" --argjson t "$now" 'del(.agents[$i]) | .update=$t' ;;
  Notification) ubah --argjson t "$now" '.status="menunggu" | .update=$t' ;;
  # background_tasks juga berisi tugas yang bukan agent (mis. pemantauan artifact), jadi tidak dipakai
  # untuk menahan status "bekerja". Agent latar yang sungguhan tetap tercatat di .agents lewat
  # SubagentStart/SubagentStop; yang lain dikosongkan.
  Stop) if [ "${bg:-0}" -gt 0 ]; then ubah --argjson t "$now" '.status="selesai" | .update=$t'
        else ubah --argjson t "$now" '.status="selesai" | .agents={} | .update=$t'; fi ;;
  SessionEnd) rm -f "$f" ;;
esac
find "$dir" \( -name '*.json' -o -name '*.tmp*' \) -mtime +1 -delete 2>/dev/null
exit 0
