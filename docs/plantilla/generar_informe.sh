#!/usr/bin/env bash
# Genera docs/informe_final_unves_2026.docx a partir del Markdown (formato APA 7.ª ed.).
# Uso: bash docs/plantilla/generar_informe.sh
set -euo pipefail

DOCS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLANTILLA="$DOCS_DIR/plantilla"
PYTHON="${PYTHON:-/usr/bin/python3}"

cd "$DOCS_DIR"
pandoc informe_final_unves_2026.md \
  -f markdown+hard_line_breaks \
  -t docx \
  --reference-doc="$PLANTILLA/reference_apa.docx" \
  --lua-filter="$PLANTILLA/apa.lua" \
  --resource-path=".:.." \
  -o informe_final_unves_2026.docx

"$PYTHON" "$PLANTILLA/postprocesar_docx.py" informe_final_unves_2026.docx
echo "Informe generado: $DOCS_DIR/informe_final_unves_2026.docx"
echo "Al abrirlo en Word, aceptar 'Actualizar campos' para generar el índice."
