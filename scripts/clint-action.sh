#!/usr/bin/env bash
# Aksi menu bar clint (dipanggil aplikasi menu bar). Pakai: clint-action.sh <aksi> [arg...]
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
root="$(cd "$(dirname "$0")/.." && pwd)"; cfg="$HOME/.config/clint"; log="$HOME/Library/Logs/clint"
mkdir -p "$cfg"
lang="$(jq -r '.language // "en"' "$cfg/user.json" 2>/dev/null)"
t(){ if [ "$lang" = "id" ]; then printf '%s' "$1"; else printf '%s' "$2"; fi; }
kabar(){ bash "$root/hooks/notify.sh" "$1"; }
diam(){ CLINT_SUARA=0 bash "$root/hooks/notify.sh" "$1"; }   # notifikasi saja
case "$1" in
  salin)  printf '%s' "$2" | pbcopy; diam "$(t "Perintah disalin. Tempel di Claude Code, project $3." "Command copied. Paste it in Claude Code, project $3.")" ;;
  laporan) f="$(ls -t "$log"/*.html 2>/dev/null | head -1)"
           [ -n "$f" ] && open "$f" || diam "$(t "Belum ada laporan. Klik Cek semua project." "No report yet. Click Check all projects.")" ;;
  cek-semua) nohup bash "$root/scripts/morning-greeting.sh" >/dev/null 2>&1 &
           kabar "$(t "Siap, saya periksa semua project yang aktif. Laporannya menyusul." "OK, checking all active projects. The report will follow.")" ;;
  cek)    nohup bash "$root/scripts/morning-greeting.sh" "$2" >/dev/null 2>&1 &
           kabar "$(t "Siap, saya periksa $(basename "$2"). Laporannya menyusul." "OK, checking $(basename "$2"). The report will follow.")" ;;
  halo)   if shortcuts list 2>/dev/null | grep -qx "Halo Clint"; then shortcuts run "Halo Clint" >/dev/null 2>&1 &
           else kabar "$(t "Halo. Untuk perintah suara, buat dulu pintasan Halo Clint. Langkahnya ada di README clint." "Hello. For voice commands, first create the Halo Clint shortcut. The steps are in the clint README.")"; fi ;;
  suara)  if [ -f "$cfg/diam" ]; then rm -f "$cfg/diam"; kabar "$(t "Suara aktif lagi." "Voice is on again.")"
          else touch "$cfg/diam"; diam "$(t "Suara dimatikan. Kabar hanya lewat notifikasi." "Voice muted. Updates come as notifications only.")"; fi ;;
  bisu)   date -v+1d +%F > "$cfg/bisu-sampai"; CLINT_PAKSA=1 diam "$(t "Dibisukan sampai besok pagi." "Muted until tomorrow morning.")" ;;
  bunyikan) rm -f "$cfg/bisu-sampai"; kabar "$(t "Kabar dinyalakan lagi." "Updates are on again.")" ;;
  sapaan-mati)  jq -n '{aktif:false}' > "$cfg/sapaan.json"; diam "$(t "Sapaan pagi dimatikan." "Morning greeting turned off.")" ;;
  sapaan-nyala) jq -n '{aktif:true}' > "$cfg/sapaan.json"; diam "$(t "Sapaan pagi dinyalakan, Senin sampai Jumat jam 08.00." "Morning greeting on, Monday to Friday at 08.00.")" ;;
  vscode) if [ -n "$2" ]; then open -a "Visual Studio Code" "$2"; else open -a "Visual Studio Code"; fi ;;
  buka)   open "$2" ;;
  bersihkan) rm -f "$log/terakhir.json" "$log/terakhir.json.lock" "$log"/kerja/*.json "$cfg/proyek-aktif.txt"
           diam "$(t "Menu dibersihkan." "Menu cleared.")" ;;
  selesai) python3 "$root/scripts/update-report.py" selesai "$2" ${3:+--proyek "$3"}; diam "$(t "Ditandai selesai." "Marked as done.")" ;;
esac
