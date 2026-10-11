#!/bin/bash
set -e
variant="${1:-Future}"
here="$(cd "$(dirname "$0")" && pwd)"
dst="$HOME/config/settings/system/app_server"

[ -f "$here/$variant/appearance" ] || { echo "Bilinmeyen varyant: $variant"; exit 1; }

mkdir -p "$dst" "$HOME/Pictures"
[ -f "$dst/appearance" ] && cp "$dst/appearance" "$dst/appearance.bak"
cp "$here/$variant/appearance" "$dst/appearance"
cp "$here/wallpapers/$variant.png" "$HOME/Pictures/"

echo "Tamam. Renkler app_server acilisinda okunur: oturumu kapatip ac veya yeniden baslat."
echo "Duvar kagidi: Tercihler > Arka Plan > ~/Pictures/$variant.png"
echo "Geri almak icin: cp $dst/appearance.bak $dst/appearance"
