#!/usr/bin/env bash
#
# Clasifica la carpeta de Descargas por el CONTENIDO del fichero, no solo por extension.
#
#   - Lee el texto dentro de PDFs (con pdftotext), TXT/CSV y nombres de fichero.
#   - Aplica reglas por palabras clave -> subcarpeta destino (facturas, actas, etc.).
#   - Si no reconoce el contenido, cae en la clasificacion por tipo.
#   - No borra nada. Modo simulacion con --dry-run.
#
# Requisito recomendado (para leer PDFs): poppler
#   macOS:  brew install poppler
#   Linux:  sudo apt install poppler-utils     (o el equivalente de tu distro)
#
# Uso:
#   bash clasificar-por-contenido.sh --dry-run
#   bash clasificar-por-contenido.sh
#   bash clasificar-por-contenido.sh --path ~/Descargas
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
LOG="$DIR/_clasificacion_${TS}.log"
PREFIJO=""; [ "$DRYRUN" -eq 1 ] && PREFIJO="[SIMULACION] "
registrar() { echo "${PREFIJO}$1"; [ "$DRYRUN" -eq 0 ] && echo "${PREFIJO}$1" >> "$LOG" || true; }

HAS_PDFTOTEXT=0
command -v pdftotext >/dev/null 2>&1 && HAS_PDFTOTEXT=1
[ "$HAS_PDFTOTEXT" -eq 0 ] && registrar "AVISO: no se encontro 'pdftotext'; los PDF se clasifican solo por su nombre. Instala poppler para leer su contenido."

# Extrae texto analizable (nombre + contenido) en minusculas, sin acentos.
texto_de() {
  local f="$1" base ext contenido=""
  base="$(basename "$f")"
  ext="${base##*.}"; ext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
  case "$ext" in
    pdf) [ "$HAS_PDFTOTEXT" -eq 1 ] && contenido="$(pdftotext -q -l 3 "$f" - 2>/dev/null || true)" ;;
    txt|csv|md|log|json) contenido="$(head -c 20000 "$f" 2>/dev/null || true)" ;;
  esac
  printf '%s\n%s' "$base" "$contenido" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -e 's/á/a/g' -e 's/é/e/g' -e 's/í/i/g' -e 's/ó/o/g' -e 's/ú/u/g' \
          -e 's/à/a/g' -e 's/è/e/g' -e 's/ì/i/g' -e 's/ò/o/g' -e 's/ù/u/g' \
          -e 's/ä/a/g' -e 's/ë/e/g' -e 's/ï/i/g' -e 's/ö/o/g' -e 's/ü/u/g' -e 's/ñ/n/g'
}

# Reglas de CONTENIDO: primera coincidencia gana. Formato: "palabras|clave|separadas::Carpeta/Destino"
# Ajusta y amplia libremente segun tus comunidades y proveedores.
REGLAS_CONTENIDO=(
  "factura|n. factura|nº factura|importe total|base imponible|iva::Documentos/Facturas"
  "acta|junta de propietarios|orden del dia|acta de la junta|se acuerda::Documentos/Actas"
  "presupuesto|oferta economica|partida|mediciones|coste estimado::Documentos/Presupuestos"
  "contrato|arrendamiento|clausula|clausulado|firmante|de comun acuerdo::Documentos/Contratos"
  "poliza|seguro|aseguradora|cobertura|siniestro|prima anual::Documentos/Seguros"
  "modelo 3|modelo 1|agencia tributaria|impuesto|declaracion|liquidacion|irpf|iva trimestral::Documentos/Impuestos"
  "nomina|salario|retribucion|seguridad social|cotizacion|liquido a percibir::Documentos/Nominas"
  "certificado|certificado energetico|itv|inspeccion tecnica::Documentos/Certificados"
  "recibo|domiciliacion|cargo en cuenta|adeudo::Documentos/Recibos"
  "extracto|movimientos|saldo|cuenta corriente|banco::Documentos/Bancos"
)

# Clasificacion por tipo (fallback)
destino_tipo() {
  case "$1" in
    pdf|doc|docx|odt|txt|rtf|xls|xlsx|csv|ppt|pptx) echo "Documentos/Otros" ;;
    jpg|jpeg|png|gif|heic|webp|svg|bmp|tiff)        echo "Imagenes" ;;
    mp4|mov|mkv|avi|wmv)                            echo "Videos" ;;
    mp3|wav|m4a|flac|aac)                           echo "Audio" ;;
    dmg|pkg|deb|rpm|appimage|exe|msi)               echo "Instaladores" ;;
    zip|rar|7z|tar|gz|bz2|xz)                       echo "Comprimidos" ;;
    py|js|ts|sql|json|html|css|sh)                  echo "Codigo" ;;
    *)                                              echo "_Para_revisar" ;;
  esac
}

# Devuelve la subcarpeta segun contenido, o vacio si no reconoce nada.
destino_contenido() {
  local txt="$1" regla claves carpeta clave
  for regla in "${REGLAS_CONTENIDO[@]}"; do
    claves="${regla%%::*}"; carpeta="${regla##*::}"
    IFS='|' read -ra arr <<< "$claves"
    for clave in "${arr[@]}"; do
      if printf '%s' "$txt" | grep -qF "$clave"; then echo "$carpeta"; return 0; fi
    done
  done
  return 1
}

registrar "=== Clasificando por contenido: $DIR ==="

find "$DIR" -maxdepth 1 -type f | while IFS= read -r f; do
  base="$(basename "$f")"
  case "$base" in _clasificacion_*.log|_organizacion_*.log) continue ;; esac
  ext="${base##*.}"; ext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"

  txt="$(texto_de "$f")"
  if sub="$(destino_contenido "$txt")"; then
    motivo="contenido"
  else
    sub="$(destino_tipo "$ext")"; motivo="tipo"
  fi

  dst="$DIR/$sub"
  [ "$DRYRUN" -eq 0 ] && mkdir -p "$dst"
  final="$dst/$base"
  i=1
  while [ -e "$final" ] && [ "$DRYRUN" -eq 0 ]; do
    final="$dst/${base%.*}_$i.${base##*.}"; i=$((i+1))
  done
  registrar "[$motivo] $base  ->  $sub/"
  [ "$DRYRUN" -eq 0 ] && mv -f -- "$f" "$final" || true
done

registrar "=== Hecho. Revisa las subcarpetas y _Para_revisar. Nada se ha borrado. ==="
[ "$DRYRUN" -eq 0 ] && echo "Log guardado en: $LOG" || true
