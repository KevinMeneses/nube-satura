#!/bin/zsh
# Instala Nube Satura en REAPER (macOS) como enlace: los cambios del repo se ven al volver a insertar el FX.
set -e
DST="$HOME/Library/Application Support/REAPER/Effects/Nube Satura"
cd "$(dirname "$0")"
mkdir -p "$DST"
ln -sf "$PWD/nube_satura.jsfx" "$DST/nube_satura.jsfx"
echo "Listo: en REAPER busca \"Nube Satura\" en el navegador de FX (JS: Nube Satura)."
