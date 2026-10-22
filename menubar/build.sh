#!/usr/bin/env bash
# Bangun aplikasi menu bar clint dan pasang ke ~/Applications, jalan otomatis saat login.
# Pakai: bash menubar/build.sh            (bangun + pasang + jalankan)
#        bash menubar/build.sh --bangun   (bangun saja, ke menubar/build/)
set -euo pipefail
akar="$(cd "$(dirname "$0")/.." && pwd)"
app="$akar/menubar/build/Clint.app"
rm -rf "$app" && mkdir -p "$app/Contents/MacOS"
swiftc -O "$akar/menubar/ClintBar.swift" -o "$app/Contents/MacOS/Clint" -framework Cocoa -framework WebKit
cat > "$app/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleIdentifier</key><string>com.clint.menubar</string>
  <key>CFBundleName</key><string>Clint</string>
  <key>CFBundleExecutable</key><string>Clint</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>LSUIElement</key><true/>
  <key>ClintRoot</key><string>$akar</string>
</dict></plist>
PLIST
codesign --force -s - "$app" >/dev/null
[ "${1:-}" = "--bangun" ] && { echo "dibangun: $app"; exit 0; }

tujuan="$HOME/Applications/Clint.app"
pkill -x Clint 2>/dev/null && sleep 1 || true
mkdir -p "$HOME/Applications" && rm -rf "$tujuan" && cp -R "$app" "$tujuan"
agen="$HOME/Library/LaunchAgents/com.clint.menubar.plist"
cat > "$agen" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.clint.menubar</string>
  <key>ProgramArguments</key><array><string>/usr/bin/open</string><string>-a</string><string>$tujuan</string></array>
  <key>RunAtLoad</key><true/>
</dict></plist>
PLIST
open -a "$tujuan"
echo "terpasang: $tujuan (jalan otomatis saat login lewat $agen)"
