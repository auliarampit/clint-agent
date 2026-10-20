#!/usr/bin/env bash
# Penerjemah perintah suara (dipanggil Pintasan "Halo Clint").
# Pakai: clint-voice.sh sapa   |   clint-voice.sh "<teks hasil dikte>"
root="$(cd "$(dirname "$0")/.." && pwd)"
lang="$(jq -r '.language // "en"' "$HOME/.config/clint/user.json" 2>/dev/null)"
t(){ if [ "$lang" = "id" ]; then printf '%s' "$1"; else printf '%s' "$2"; fi; }
bicara(){ bash "$root/hooks/notify.sh" "$1"; }
if [ "$1" = "sapa" ]; then
  if [ "$lang" = "id" ]; then say -v Damayanti "Halo, ada yang bisa saya bantu?"; else say "Hi, how can I help?"; fi
  exit 0
fi

teks="$(printf '%s' "$*" | tr '[:upper:]' '[:lower:]')"
case "$teks" in
  *cek*|*periksa*|*ada\ update*|*laporan*|*check*|*status*|*report*)
    if [[ "$teks" == *semua* || " $teks " == *" all "* ]]; then
      bicara "$(t "Siap, saya periksa semua project yang aktif. Laporannya menyusul." "OK, checking all active projects. The report will follow.")"
      nohup bash "$root/scripts/morning-greeting.sh" >/dev/null 2>&1 &
    else
      dir="$(bash "$root/scripts/find-project.sh" "$teks")"
      if [ -z "$dir" ]; then bicara "$(t "Maaf, project itu belum saya kenal. Pastikan clint sudah disiapkan di sana." "Sorry, I don't know that project yet. Make sure clint is set up there.")"; exit 0; fi
      nama="$(basename "$(dirname "$dir")") $(basename "$dir")"
      bicara "$(t "Siap, saya periksa $nama. Laporannya menyusul." "OK, checking $nama. The report will follow.")"
      nohup bash "$root/scripts/morning-greeting.sh" "$dir" >/dev/null 2>&1 &
    fi ;;
  "") bicara "$(t "Saya tidak menangkap perintahnya. Coba lagi ya." "I didn't catch that. Please try again.")" ;;
  *) bicara "$(t "Lewat suara, saya baru bisa memeriksa project. Contohnya: cek project toko online." "By voice I can only check projects for now. For example: check project online store.")" ;;
esac
