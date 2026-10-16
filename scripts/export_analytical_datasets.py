"""
Exportador de Datasets Analíticos - Proyecto Interdisciplinario UNVES 2026
Cátedras: Sistema de Información Gerencial | Realidad Social | Marketing Social
Extrae métricas normalizadas de vistas PostgreSQL hacia r-analysis/data/ y docs/
"""

import csv
import json
import logging
import os
import sys
from decimal import Decimal
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de Logging Estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [UNVES-EXPORT] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("unves.export")

# Rutas de Salida
BASE_DIR = Path(__file__).resolve().parent.parent
R_DATA_DIR = BASE_DIR / "r-analysis" / "data"
DOCS_DIR = BASE_DIR / "docs"

# Configuración de Base de Datos PostgreSQL
DB_NAME = os.getenv("PGDATABASE", "unves_sig_2026")
DB_USER = os.getenv("PGUSER", os.getenv("USER", "johnnyoviedo"))
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = int(os.getenv("PGPORT", "5432"))
DB_PASS = os.getenv("PGPASSWORD", "")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Establece conexión con PostgreSQL con manejo de excepciones."""
    try:
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST,
            port=DB_PORT,
            password=DB_PASS
        )
    except psycopg2.Error as err:
        logger.error(f"Error de conexión a PostgreSQL: {err}")
        raise


def json_serial(obj: Any) -> Any:
    """Serializador para tipos especiales de datos (Decimal, date, datetime)."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Tipo {type(obj)} no es serializable en JSON")


def fetch_query(cursor, query: str) -> List[Dict[str, Any]]:
    """Ejecuta consulta SELECT y retorna lista de diccionarios inmutables."""
    cursor.execute(query)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def save_csv(data: List[Dict[str, Any]], filepath: Path) -> None:
    """Guarda una lista de diccionarios en archivo CSV de manera atómica."""
    if not data:
        logger.warning(f"No hay registros para guardar en {filepath}")
        return
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(data[0].keys())
    
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            formatted_row = {}
            for k, v in row.items():
                if isinstance(v, (datetime, date)):
                    formatted_row[k] = v.isoformat()
                elif isinstance(v, Decimal):
                    formatted_row[k] = float(v)
                else:
                    formatted_row[k] = v
            writer.writerow(formatted_row)
            
    logger.info(f"Guardado CSV exitoso: {filepath} ({len(data)} registros)")


def export_all() -> Dict[str, Any]:
    """Extrae las 4 vistas analíticas y series temporales desde PostgreSQL."""
    R_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. Vista vw_trabajadores_consolidado
            logger.info("Consultando vw_trabajadores_consolidado...")
            trabajadores = fetch_query(cur, "SELECT * FROM vw_trabajadores_consolidado ORDER BY id_trabajador;")
            save_csv(trabajadores, R_DATA_DIR / "vw_trabajadores_consolidado.csv")
            
            # 2. Vista vw_unidades_productivas_consolidado
            logger.info("Consultando vw_unidades_productivas_consolidado...")
            unidades = fetch_query(cur, "SELECT * FROM vw_unidades_productivas_consolidado ORDER BY id_unidad;")
            save_csv(unidades, R_DATA_DIR / "vw_unidades_productivas_consolidado.csv")
            
            # 3. Vista vw_marketing_resumen_canales
            logger.info("Consultando vw_marketing_resumen_canales...")
            marketing_resumen = fetch_query(cur, "SELECT * FROM vw_marketing_resumen_canales ORDER BY codigo_canal;")
            save_csv(marketing_resumen, R_DATA_DIR / "vw_marketing_resumen_canales.csv")
            
            # 4. Vista vw_articulacion_programas_formalizacion
            logger.info("Consultando vw_articulacion_programas_formalizacion...")
            programas = fetch_query(cur, "SELECT * FROM vw_articulacion_programas_formalizacion ORDER BY id_programa;")
            save_csv(programas, R_DATA_DIR / "vw_articulacion_programas_formalizacion.csv")
            
            # 5. Serie diaria de marketing
            logger.info("Consultando serie diaria de marketing_kpis...")
            marketing_diario_query = """
                SELECT 
                    m.id_kpi,
                    m.fecha,
                    c.codigo AS codigo_canal,
                    c.nombre AS canal_nombre,
                    c.tipo AS tipo_canal,
                    m.impresiones_alcance,
                    m.clics_interacciones,
                    m.ctr_interaccion_pct,
                    m.consultas_iniciadas,
                    m.consultas_tema_resimple,
                    m.consultas_tema_ips,
                    m.derivaciones_suace_villarrica,
                    m.derivaciones_ips_regional,
                    m.derivaciones_totales_formalizacion,
                    m.presupuesto_invertido_pyg
                FROM marketing_kpis m
                JOIN canales_marketing c ON m.canal_id = c.id_canal
                ORDER BY m.fecha, c.codigo;
            """
            marketing_diario = fetch_query(cur, marketing_diario_query)
            save_csv(marketing_diario, R_DATA_DIR / "marketing_kpis_diario.csv")
            
            # 6. Catálogo de Barrios con coordenadas y límites
            logger.info("Consultando catálogo de barrios...")
            barrios = fetch_query(cur, "SELECT * FROM barrios ORDER BY id;")
            save_csv(barrios, R_DATA_DIR / "barrios_villarrica.csv")
            
            # 7. Compilar JSON consolidado para el dashboard web
            logger.info("Compilando dashboard_data.json para tableros gerenciales...")
            dashboard_data = {
                "generated_at": datetime.now().isoformat(),
                "salario_minimo_legal": 3044000,
                "totales": {
                    "trabajadores": len(trabajadores),
                    "unidades_productivas": len(unidades),
                    "canales_marketing": len(marketing_resumen),
                    "programas_formalizacion": len(programas),
                    "dias_campana": len(set(row["fecha"] for row in marketing_diario))
                },
                "barrios": barrios,
                "trabajadores": trabajadores,
                "unidades_productivas": unidades,
                "marketing_resumen": marketing_resumen,
                "marketing_diario": marketing_diario,
                "programas": programas
            }
            
            # Guardar en r-analysis/data/ y docs/
            json_str = json.dumps(dashboard_data, default=json_serial, ensure_ascii=False, indent=2)
            js_str = f"window.UNVES_DASHBOARD_DATA = {json_str};\n"
            
            with open(R_DATA_DIR / "dashboard_data.json", "w", encoding="utf-8") as f:
                f.write(json_str)
            logger.info(f"Guardado exitoso: {R_DATA_DIR / 'dashboard_data.json'}")
            
            with open(DOCS_DIR / "dashboard_data.json", "w", encoding="utf-8") as f:
                f.write(json_str)
            logger.info(f"Guardado exitoso: {DOCS_DIR / 'dashboard_data.json'}")

            with open(DOCS_DIR / "dashboard_data.js", "w", encoding="utf-8") as f:
                f.write(js_str)
            logger.info(f"Guardado exitoso: {DOCS_DIR / 'dashboard_data.js'}")
            
            return dashboard_data
    finally:
        conn.close()


if __name__ == "__main__":
    export_all()
    logger.info("Exportación analítica completada con éxito.")
