#!/usr/bin/env bash
# Penerjemah perintah suara (dipanggil Pintasan "Halo Clint").
# Pakai: clint-voice.sh sapa   |   clint-voice.sh "<teks hasil dikte>"
root="$(cd "$(dirname "$0")/.." && pwd)"
bicara(){ bash "$root/hooks/notify.sh" "$1"; }
[ "$1" = "sapa" ] && { say -v Damayanti "Halo, ada yang bisa saya bantu?"; exit 0; }

teks="$(printf '%s' "$*" | tr '[:upper:]' '[:lower:]')"
case "$teks" in
  *cek*|*periksa*|*ada\ update*|*laporan*)
    if [[ "$teks" == *semua* ]]; then
      bicara "Siap, saya periksa semua project yang aktif. Laporannya menyusul."
      nohup bash "$root/scripts/morning-greeting.sh" >/dev/null 2>&1 &
    else
      dir="$(bash "$root/scripts/find-project.sh" "$teks")"
      if [ -z "$dir" ]; then bicara "Maaf, project itu belum saya kenal. Pastikan clint sudah disiapkan di sana."; exit 0; fi
      bicara "Siap, saya periksa $(basename "$(dirname "$dir")") $(basename "$dir"). Laporannya menyusul."
      nohup bash "$root/scripts/morning-greeting.sh" "$dir" >/dev/null 2>&1 &
    fi ;;
  "") bicara "Saya tidak menangkap perintahnya. Coba lagi ya." ;;
  *) bicara "Lewat suara, saya baru bisa memeriksa project. Contohnya: cek project toko online." ;;
esac
