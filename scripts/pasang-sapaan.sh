#!/usr/bin/env bash
# Pasang sapaan pagi (Senin–Jumat) lewat launchd.
# Pakai: pasang-sapaan.sh <jam> <menit>   |   pasang-sapaan.sh --cabut   (project aktif dideteksi otomatis)
label="com.clint.sapaan-pagi"; plist="$HOME/Library/LaunchAgents/$label.plist"
launchctl bootout "gui/$(id -u)/$label" 2>/dev/null
if [ "$1" = "--cabut" ]; then rm -f "$plist"; echo "sapaan pagi dicabut"; exit 0; fi
jam="$1"; menit="$2"; shift 2
script="$(cd "$(dirname "$0")" && pwd)/sapaan-pagi.sh"
args=""; for d in "$@"; do args+="<string>$(cd "$d" && pwd)</string>"; done
hari=""; for w in 1 2 3 4 5; do hari+="<dict><key>Weekday</key><integer>$w</integer><key>Hour</key><integer>$jam</integer><key>Minute</key><integer>$menit</integer></dict>"; done
cat > "$plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>$label</string>
<key>ProgramArguments</key><array><string>/bin/bash</string><string>$script</string>$args</array>
<key>StartCalendarInterval</key><array>$hari</array>
<key>EnvironmentVariables</key><dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
<key>StandardErrorPath</key><string>$HOME/Library/Logs/clint/launchd.err</string>
</dict></plist>
PL
plutil -lint "$plist" >/dev/null && launchctl bootstrap "gui/$(id -u)" "$plist" && echo "sapaan pagi terpasang: Senin–Jumat $jam:$(printf %02d "$menit")"
