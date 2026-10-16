"""Ajusta las tablas del informe generado por pandoc al formato FCE-UNVES (APA 7.ª ed.).

- Ancho de tabla al 100 % del área de texto con ajuste automático de columnas.
- Letra de 10 pt en tablas (9 pt en tablas de 8 o más columnas).

Uso: python3 postprocesar_docx.py <archivo.docx>
"""

import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

FULL_WIDTH_PCT = "5000"  # 100 % expresado en cincuentavos de punto porcentual
WIDE_TABLE_COLUMNS = 8
FONT_SIZE_DEFAULT = Pt(10)
FONT_SIZE_WIDE = Pt(9)


def set_full_width(table) -> None:
    tbl_pr = table._tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        for existing in tbl_pr.findall(qn(tag)):
            tbl_pr.remove(existing)
    width = OxmlElement("w:tblW")
    width.set(qn("w:w"), FULL_WIDTH_PCT)
    width.set(qn("w:type"), "pct")
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "autofit")
    tbl_pr.append(width)
    tbl_pr.append(layout)


def set_font_size(table, size) -> None:
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = size


def main(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    document = Document(str(path))
    for table in document.tables:
        set_full_width(table)
        columns = len(table.columns)
        set_font_size(table, FONT_SIZE_WIDE if columns >= WIDE_TABLE_COLUMNS else FONT_SIZE_DEFAULT)
    document.save(str(path))
    print(f"Tablas ajustadas: {len(document.tables)} en {path.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 postprocesar_docx.py <archivo.docx>")
    main(Path(sys.argv[1]))
