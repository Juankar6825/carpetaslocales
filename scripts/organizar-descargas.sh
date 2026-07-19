#!/usr/bin/env bash
#
# Organiza la carpeta de Descargas en macOS / Linux.
#   - No borra de forma permanente: temporales y duplicados van a la Papelera.
#   - Clasifica el resto por tipo en subcarpetas.
#   - Registra cada accion en un log.
#
# Uso:
#   bash organizar-descargas.sh --dry-run     # simula, no mueve nada
#   bash organizar-descargas.sh               # ejecuta
#   bash organizar-descargas.sh --path ~/Descargas
#
set -euo pipefail

DIR="$HOME/Downloads"
[ -d "$HOME/Descargas" ] && DIR="$HOME/Descargas"
DRYRUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRYRUN=1; shift ;;
    --path)    DIR="$2"; shift 2 ;;
    *) echo "Opcion desconocida: $1"; exit 1 ;;
  esac
done

[ -d "$DIR" ] || { echo "No existe la carpeta: $DIR"; exit 1; }

TS="$(date +%Y%m%d_%H%M%S)"
LOG="$DIR/_organizacion_${TS}.log"
PREFIJO=""; [ "$DRYRUN" -eq 1 ] && PREFIJO="[SIMULACION] "

registrar() {
  echo "${PREFIJO}$1"
  [ "$DRYRUN" -eq 0 ] && echo "${PREFIJO}$1" >> "$LOG" || true
}

# Papelera: macOS usa ~/.Trash; Linux XDG usa ~/.local/share/Trash/files
papelera() {
  local f="$1"
  [ "$DRYRUN" -eq 1 ] && return 0
  local trash
  if [ "$(uname)" = "Darwin" ]; then
    trash="$HOME/.Trash"
  else
    trash="${XDG_DATA_HOME:-$HOME/.local/share}/Trash/files"
  fi
  mkdir -p "$trash"
  mv -f -- "$f" "$trash/$(basename "$f")" 2>/dev/null || rm -f -- "$f"
}

# Clasificacion extension -> carpeta
destino_de() {
  case "$1" in
    pdf|doc|docx|odt|txt|rtf|xls|xlsx|csv|ppt|pptx) echo "Documentos" ;;
    jpg|jpeg|png|gif|heic|webp|svg|bmp|tiff)        echo "Imagenes" ;;
    mp4|mov|mkv|avi|wmv)                            echo "Videos" ;;
    mp3|wav|m4a|flac|aac)                           echo "Audio" ;;
    dmg|pkg|deb|rpm|appimage)                       echo "Instaladores" ;;
    zip|rar|7z|tar|gz|bz2|xz)                       echo "Comprimidos" ;;
    py|js|ts|sql|json|html|css|sh)                  echo "Codigo" ;;
    *)                                              echo "_Para_revisar" ;;
  esac
}

es_temporal() {
  case "$1" in
    tmp|crdownload|part|partial|download) return 0 ;;
    *) return 1 ;;
  esac
}

registrar "=== Organizando $DIR ==="

# 1) Temporales y basura -> Papelera
find "$DIR" -maxdepth 1 -type f | while IFS= read -r f; do
  base="$(basename "$f")"
  ext="${base##*.}"; ext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
  case "$base" in _organizacion_*.log) continue ;; .DS_Store|Thumbs.db|desktop.ini)
    registrar "Papelera (basura): $base"; papelera "$f"; continue ;;
  esac
  if es_temporal "$ext"; then registrar "Papelera (temporal): $base"; papelera "$f"; fi
done

# 2) Duplicados exactos por hash -> Papelera (conserva la primera copia)
HASHTMP="$(mktemp)"
if command -v sha256sum >/dev/null 2>&1; then HASHER="sha256sum"; else HASHER="shasum -a 256"; fi
find "$DIR" -maxdepth 1 -type f ! -name '_organizacion_*.log' | while IFS= read -r f; do
  h="$($HASHER "$f" | awk '{print $1}')"
  if grep -q "^$h " "$HASHTMP" 2>/dev/null; then
    orig="$(grep "^$h " "$HASHTMP" | head -1 | cut -d' ' -f2-)"
    registrar "Papelera (duplicado de '$orig'): $(basename "$f")"; papelera "$f"
  else
    echo "$h $(basename "$f")" >> "$HASHTMP"
  fi
done
rm -f "$HASHTMP"

# 3) Clasificar el resto por tipo
find "$DIR" -maxdepth 1 -type f ! -name '_organizacion_*.log' | while IFS= read -r f; do
  base="$(basename "$f")"
  ext="${base##*.}"; ext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
  sub="$(destino_de "$ext")"
  dst="$DIR/$sub"
  [ "$DRYRUN" -eq 0 ] && mkdir -p "$dst"
  final="$dst/$base"
  i=1
  while [ -e "$final" ] && [ "$DRYRUN" -eq 0 ]; do
    final="$dst/${base%.*}_$i.${base##*.}"; i=$((i+1))
  done
  registrar "Mover -> $sub/: $base"
  [ "$DRYRUN" -eq 0 ] && mv -f -- "$f" "$final" || true
done

registrar "=== Hecho. Revisa _Para_revisar y vacia la Papelera cuando estes seguro. ==="
[ "$DRYRUN" -eq 0 ] && echo "Log guardado en: $LOG" || true
