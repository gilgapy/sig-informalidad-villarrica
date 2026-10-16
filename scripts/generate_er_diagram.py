"""
Generador del Diagrama Entidad-Relación imprimible (UNVES 2026).
Lee el catálogo de PostgreSQL (tablas, claves primarias y foráneas) y produce
docs/img/diagrama_er_impresion.png con Graphviz, en fondo blanco para el informe escrito.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

import psycopg2

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DOT = BASE_DIR / "docs" / "img" / "diagrama_er_impresion.dot"
OUTPUT_PNG = BASE_DIR / "docs" / "img" / "diagrama_er_impresion.png"

CATALOGOS = {"barrios", "oficios", "rubros_mypes", "medios_pago", "canales_marketing", "programas_formalizacion"}
ASOCIATIVAS = {"trabajadores_medios_pago", "unidades_medios_pago"}
COLOR_CATALOGO = "#E0E7FF"
COLOR_ASOCIATIVA = "#FEF3C7"
COLOR_MAESTRA = "#D1FAE5"

SQL_COLUMNAS = """
    SELECT c.table_name, c.column_name, c.data_type
    FROM information_schema.columns c
    JOIN information_schema.tables t
      ON t.table_name = c.table_name AND t.table_schema = c.table_schema
    WHERE c.table_schema = 'public' AND t.table_type = 'BASE TABLE'
    ORDER BY c.table_name, c.ordinal_position;
"""

SQL_CLAVES = """
    SELECT tc.constraint_type, kcu.table_name, kcu.column_name,
           ccu.table_name AS ref_table, ccu.column_name AS ref_column
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
    LEFT JOIN information_schema.constraint_column_usage ccu
      ON tc.constraint_name = ccu.constraint_name AND tc.constraint_type = 'FOREIGN KEY'
    WHERE tc.table_schema = 'public' AND tc.constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY');
"""


def get_connection() -> psycopg2.extensions.connection:
    """Retorna conexión a PostgreSQL usando las variables de entorno estándar."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE", "unves_sig_2026"),
        user=os.getenv("PGUSER", os.getenv("USER", "postgres")),
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        password=os.getenv("PGPASSWORD", ""),
    )


def leer_catalogo() -> Tuple[Dict[str, List[Tuple[str, str]]], Dict[str, Set[str]], List[Tuple[str, str, str, str]]]:
    """Devuelve columnas por tabla, claves primarias por tabla y lista de claves foráneas."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(SQL_COLUMNAS)
        columnas: Dict[str, List[Tuple[str, str]]] = {}
        for tabla, columna, tipo in cur.fetchall():
            columnas.setdefault(tabla, []).append((columna, tipo))
        cur.execute(SQL_CLAVES)
        pks: Dict[str, Set[str]] = {}
        fks: List[Tuple[str, str, str, str]] = []
        for tipo, tabla, columna, ref_tabla, ref_columna in cur.fetchall():
            if tipo == "PRIMARY KEY":
                pks.setdefault(tabla, set()).add(columna)
            else:
                fks.append((tabla, columna, ref_tabla, ref_columna))
    return columnas, pks, fks


def color_tabla(tabla: str) -> str:
    if tabla in CATALOGOS:
        return COLOR_CATALOGO
    if tabla in ASOCIATIVAS:
        return COLOR_ASOCIATIVA
    return COLOR_MAESTRA


TIPOS_CORTOS = {"character varying": "varchar", "timestamp with time zone": "timestamptz"}


def nodo_tabla(tabla: str, columnas: List[Tuple[str, str]], pk: Set[str], fk_cols: Set[str], ref_cols: Set[str]) -> str:
    """Construye la etiqueta HTML de Graphviz con PK, FK y conteo de atributos restantes."""
    filas = []
    otros = 0
    for columna, tipo in columnas:
        if columna in pk or columna in fk_cols or columna in ref_cols:
            marca = " ".join(m for m, cond in (("PK", columna in pk), ("FK", columna in fk_cols), ("UQ", columna in ref_cols and columna not in pk)) if cond)
            tipo = TIPOS_CORTOS.get(tipo, tipo)
            estilo = "<B>{}</B>" if columna in pk else "{}"
            filas.append(
                f'<TR><TD ALIGN="LEFT" PORT="{columna}_in">{estilo.format(columna)}</TD>'
                f'<TD ALIGN="LEFT"><FONT COLOR="#475569">{tipo}</FONT></TD>'
                f'<TD ALIGN="LEFT" PORT="{columna}_out"><B>{marca}</B></TD></TR>'
            )
        else:
            otros += 1
    if otros:
        filas.append(f'<TR><TD COLSPAN="3" ALIGN="LEFT"><I>+ {otros} atributos</I></TD></TR>')
    return (
        f'  {tabla} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">'
        f'<TR><TD COLSPAN="3" BGCOLOR="{color_tabla(tabla)}"><B>{tabla}</B></TD></TR>'
        f'{"".join(filas)}</TABLE>>];'
    )


def construir_dot(columnas, pks, fks) -> str:
    fk_por_tabla: Dict[str, Set[str]] = {}
    ref_por_tabla: Dict[str, Set[str]] = {}
    for tabla, columna, ref_tabla, ref_columna in fks:
        fk_por_tabla.setdefault(tabla, set()).add(columna)
        ref_por_tabla.setdefault(ref_tabla, set()).add(ref_columna)
    lineas = [
        "digraph ER {",
        '  graph [rankdir=LR, bgcolor="white", nodesep=0.5, ranksep=1.1, fontname="Helvetica", dpi=200];',
        '  node [shape=plaintext, fontname="Helvetica", fontsize=11];',
        '  edge [color="#334155", arrowhead=crow, arrowtail=tee, dir=both, penwidth=1.2];',
    ]
    for tabla in sorted(columnas):
        lineas.append(nodo_tabla(tabla, columnas[tabla], pks.get(tabla, set()), fk_por_tabla.get(tabla, set()), ref_por_tabla.get(tabla, set())))
    for tabla, columna, ref_tabla, ref_columna in fks:
        lineas.append(f"  {ref_tabla}:{ref_columna}_out:e -> {tabla}:{columna}_in:w;")
    lineas.append("}")
    return "\n".join(lineas)


def main() -> int:
    try:
        columnas, pks, fks = leer_catalogo()
    except psycopg2.Error as error:
        print(f"Error al leer el catálogo de PostgreSQL: {error}", file=sys.stderr)
        return 1
    OUTPUT_DOT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DOT.write_text(construir_dot(columnas, pks, fks), encoding="utf-8")
    try:
        subprocess.run(["dot", "-Tpng", str(OUTPUT_DOT), "-o", str(OUTPUT_PNG)], check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Error al ejecutar Graphviz (dot): {error}", file=sys.stderr)
        return 1
    print(f"Diagrama ER generado: {OUTPUT_PNG} ({len(columnas)} tablas, {len(fks)} claves foráneas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
