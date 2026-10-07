#!/usr/bin/env bash
# Catat status setiap sesi Claude Code untuk menu bar (tanpa token):
# ~/.config/clint/sesi/<session_id>.json = {cwd, status, tugas, mulai, agents{id:tipe}}
input="$(cat)"
dir="$HOME/.config/clint/sesi"; mkdir -p "$dir"
[ -f "$HOME/.config/clint/debug" ] && printf '%s\n' "$input" >> "$HOME/.config/clint/debug.log"
ev="$(jq -r '.hook_event_name // empty' <<<"$input")"
sid="$(jq -r '.session_id // empty' <<<"$input")"; [ -n "$sid" ] || exit 0
f="$dir/$sid.json"; now="$(date +%s)"
[ -f "$f" ] || jq -n --arg c "$(jq -r '.cwd // empty' <<<"$input")" --argjson t "$now" \
  '{cwd:$c,status:"siap",tugas:"",mulai:$t,update:$t,agents:{}}' > "$f"
ubah(){ jq "$@" "$f" > "$f.tmp" && mv "$f.tmp" "$f"; }
case "$ev" in
  UserPromptSubmit) ubah --arg p "$(jq -r '.prompt // ""' <<<"$input" | tr '\n' ' ' | cut -c1-90)" --argjson t "$now" \
                      '.status="bekerja" | .tugas=$p | .mulai=$t | .update=$t' ;;
  SubagentStart) ubah --arg i "$(jq -r '.agent_id // .tool_use_id // "?"' <<<"$input")" \
                      --arg a "$(jq -r '.agent_type // .subagent_type // "agent"' <<<"$input")" --argjson t "$now" \
                      '.agents[$i]=$a | .update=$t' ;;
  SubagentStop) ubah --arg i "$(jq -r '.agent_id // .tool_use_id // "?"' <<<"$input")" --argjson t "$now" \
                      'del(.agents[$i]) | .update=$t' ;;
  PostToolUse) touch "$f" ;;
  Notification) ubah --argjson t "$now" '.status="menunggu" | .update=$t' ;;
  Stop) bg="$(jq '.background_tasks // [] | length' <<<"$input")"
        if [ "$bg" -gt 0 ]; then ubah --argjson t "$now" '.status="latar" | .update=$t'
        else ubah --argjson t "$now" '.status="selesai" | .agents={} | .update=$t'; fi ;;
  SessionEnd) rm -f "$f" ;;
esac
find "$dir" -name '*.json' -mtime +1 -delete 2>/dev/null
exit 0
