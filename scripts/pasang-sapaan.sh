#!/usr/bin/env bash
# Atur sapaan pagi (dijalankan oleh plugin menu bar clint, Senin–Jumat). Tanpa SwiftBar, sapaan tidak jalan.
# Pakai: pasang-sapaan.sh <jam> <menit>   |   pasang-sapaan.sh --cabut
# (Jadwal launchd lama dicabut: macOS melarang launchd membuka folder Desktop.)
cfg="$HOME/.config/clint"; mkdir -p "$cfg"
launchctl bootout "gui/$(id -u)/com.clint.sapaan-pagi" 2>/dev/null; rm -f "$HOME/Library/LaunchAgents/com.clint.sapaan-pagi.plist"
if [ "$1" = "--cabut" ]; then jq -n '{aktif:false}' > "$cfg/sapaan.json"; echo "sapaan pagi dimatikan"; exit 0; fi
jq -n --argjson j "${1:-8}" --argjson m "${2:-0}" '{aktif:true, jam:$j, menit:$m, sampai:13}' > "$cfg/sapaan.json"
echo "sapaan pagi: Senin–Jumat $(printf %02d "${1:-8}").$(printf %02d "${2:-0}") (sebelum 13.00, sekali per hari)"
