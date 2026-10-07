#!/usr/bin/env bash
# Aksi menu bar clint (dipanggil SwiftBar). Pakai: clint-aksi.sh <aksi> [arg...]
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
root="$(cd "$(dirname "$0")/.." && pwd)"; cfg="$HOME/.config/clint"; log="$HOME/Library/Logs/clint"
mkdir -p "$cfg"
kabar(){ bash "$root/hooks/kabar.sh" "$1"; }
diam(){ CLINT_SUARA=0 bash "$root/hooks/kabar.sh" "$1"; }   # notifikasi saja
segar(){ open -g "swiftbar://refreshplugin?name=clint.1m.py" 2>/dev/null; }
case "$1" in
  salin)  printf '%s' "$2" | pbcopy; diam "Perintah disalin. Tempel di Claude Code, project $3." ;;
  laporan) f="$(ls -t "$log"/*.html 2>/dev/null | head -1)"
           [ -n "$f" ] && open "$f" || diam "Belum ada laporan. Klik Cek semua project." ;;
  cek-semua) nohup bash "$root/scripts/sapaan-pagi.sh" >/dev/null 2>&1 &
           kabar "Siap, saya periksa semua project yang aktif. Laporannya menyusul." ;;
  cek)    nohup bash "$root/scripts/sapaan-pagi.sh" "$2" >/dev/null 2>&1 &
           kabar "Siap, saya periksa $(basename "$2"). Laporannya menyusul." ;;
  halo)   if shortcuts list 2>/dev/null | grep -qx "Halo Clint"; then shortcuts run "Halo Clint" >/dev/null 2>&1 &
           else kabar "Halo. Untuk perintah suara, buat dulu pintasan Halo Clint. Langkahnya ada di README clint."; fi ;;
  suara)  if [ -f "$cfg/diam" ]; then rm -f "$cfg/diam"; kabar "Suara aktif lagi."; else touch "$cfg/diam"; diam "Suara dimatikan. Kabar hanya lewat notifikasi."; fi ;;
  bisu)   date -v+1d +%F > "$cfg/bisu-sampai"; CLINT_PAKSA=1 diam "Dibisukan sampai besok pagi." ;;
  bunyikan) rm -f "$cfg/bisu-sampai"; kabar "Kabar dinyalakan lagi." ;;
  sapaan) diam "Sapaan pagi Senin sampai Jumat jam 08.00. Ubah lewat scripts/pasang-sapaan.sh." ;;
  vscode) if [ -n "$2" ]; then open -a "Visual Studio Code" "$2"; else open -a "Visual Studio Code"; fi ;;
  buka)   open "$2" ;;
esac
segar
