"""
Script de Verificación y Validación de Calidad - FASE 4 (UNVES 2026)
Cátedras: Sistema de Información Gerencial | Realidad Social | Marketing Social
Valida interoperabilidad, coherencia de datos entre PostgreSQL, R y Dashboard Web.
Sesión 12 - Indicador 3, 4 y 5 de Rúbrica
"""

import json
import logging
import os
import sys
from pathlib import Path
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [UNVES-VERIFY-P4] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("unves.verify.p4")

# Rutas Base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "r-analysis" / "data"
OUTPUT_DIR = BASE_DIR / "r-analysis" / "output"
DOCS_DIR = BASE_DIR / "docs"

# Base de Datos
DB_NAME = os.getenv("PGDATABASE", "unves_sig_2026")
DB_USER = os.getenv("PGUSER", os.getenv("USER", "johnnyoviedo"))
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = int(os.getenv("PGPORT", "5432"))
DB_PASS = os.getenv("PGPASSWORD", "")
DATABASE_URL = os.getenv("DATABASE_URL")


class Phase4Validator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_tests = 0

    def record_pass(self, test_name: str, message: str):
        self.passed_tests += 1
        logger.info(f"✔ [PASS] {test_name}: {message}")

    def record_fail(self, test_name: str, message: str):
        self.errors.append(f"{test_name}: {message}")
        logger.error(f"✖ [FAIL] {test_name}: {message}")

    def get_connection(self):
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST,
            port=DB_PORT,
            password=DB_PASS
        )

    def test_database_views(self):
        """1. Valida existencia y conteo exacto de las vistas PostgreSQL."""
        logger.info("--- 1. Verificando Vistas Analíticas en PostgreSQL ---")
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                # vw_trabajadores_consolidado
                cur.execute("SELECT count(*), avg(ingreso_mensual_pyg), avg(indice_vulnerabilidad_social) FROM vw_trabajadores_consolidado;")
                row_t = cur.fetchone()
                if row_t[0] == 420:
                    self.record_pass("DB-Vistas-Trabajadores", f"420 registros encontrados. Ingreso promedio: Gs. {float(row_t[1]):,.0f}")
                else:
                    self.record_fail("DB-Vistas-Trabajadores", f"Se esperaban 420 registros, se hallaron {row_t[0]}")

                # vw_unidades_productivas_consolidado
                cur.execute("SELECT count(*), avg(tasa_informalidad_laboral_pct) FROM vw_unidades_productivas_consolidado;")
                row_u = cur.fetchone()
                if row_u[0] == 135:
                    self.record_pass("DB-Vistas-Unidades", f"135 MYPEs encontradas. Informalidad patronal media: {float(row_u[1]):.1f}%")
                else:
                    self.record_fail("DB-Vistas-Unidades", f"Se esperaban 135 MYPEs, se hallaron {row_u[0]}")

                # vw_marketing_resumen_canales
                cur.execute("SELECT count(*), sum(total_derivaciones) FROM vw_marketing_resumen_canales;")
                row_m = cur.fetchone()
                if row_m[0] == 4:
                    self.record_pass("DB-Vistas-Marketing", f"4 canales encontrados. Total derivaciones: {row_m[1]}")
                else:
                    self.record_fail("DB-Vistas-Marketing", f"Se esperaban 4 canales, se hallaron {row_m[0]}")

                # vw_articulacion_programas_formalizacion
                cur.execute("SELECT count(*) FROM vw_articulacion_programas_formalizacion;")
                row_p = cur.fetchone()
                if row_p[0] == 3:
                    self.record_pass("DB-Vistas-Programas", "3 programas articulados encontrados (RESIMPLE, IPS, SUACE)")
                else:
                    self.record_fail("DB-Vistas-Programas", f"Se esperaban 3 programas, se hallaron {row_p[0]}")

            conn.close()
        except Exception as e:
            self.record_fail("DB-Connection", f"Fallo al conectar o consultar vistas: {e}")

    def test_exported_datasets(self):
        """2. Valida la exportación de datasets a r-analysis/data/ y docs/."""
        logger.info("--- 2. Verificando Datasets Exportados para R y Web ---")
        csv_files = [
            ("vw_trabajadores_consolidado.csv", 420),
            ("vw_unidades_productivas_consolidado.csv", 135),
            ("vw_marketing_resumen_canales.csv", 4),
            ("vw_articulacion_programas_formalizacion.csv", 3),
            ("marketing_kpis_diario.csv", 168),
            ("barrios_villarrica.csv", 7)
        ]

        for filename, expected_rows in csv_files:
            filepath = DATA_DIR / filename
            if not filepath.exists():
                self.record_fail("Export-CSV", f"Archivo inexistente: {filepath}")
                continue

            with open(filepath, "r", encoding="utf-8") as f:
                lines = [line for line in f if line.strip()]
                data_rows = len(lines) - 1 # Descontar encabezado

            if data_rows == expected_rows:
                self.record_pass("Export-CSV", f"{filename} tiene exactamente {expected_rows} registros.")
            else:
                self.record_fail("Export-CSV", f"{filename} tiene {data_rows} registros, se esperaban {expected_rows}")

        # JSON Consolidado
        json_paths = [DATA_DIR / "dashboard_data.json", DOCS_DIR / "dashboard_data.json", DOCS_DIR / "dashboard_data.js"]
        for p in json_paths:
            if p.exists() and p.stat().st_size > 100000:
                self.record_pass("Export-JSON", f"{p.name} generado con tamaño válido ({p.stat().st_size / 1024:.1f} KB)")
            else:
                self.record_fail("Export-JSON", f"Archivo ausente o corrupto: {p}")

    def test_r_econometric_outputs(self):
        """3. Valida los artefactos analíticos de R y figuras APA 7."""
        logger.info("--- 3. Verificando Resultados Econométricos y Figuras APA 7 ---")
        
        # JSON de Resultados Econométricos
        res_json_path = OUTPUT_DIR / "resultados_econometricos.json"
        if not res_json_path.exists():
            self.record_fail("R-JSON", f"No se encontró {res_json_path}")
            return

        with open(res_json_path, "r", encoding="utf-8") as f:
            res_data = json.load(f)

        # Validar N y métricas clave
        if res_data["metadatos"]["muestra_trabajadores"] == 420:
            self.record_pass("R-Metadatos", "Muestra de 420 trabajadores validada en JSON de R.")
        else:
            self.record_fail("R-Metadatos", "Muestra de trabajadores en JSON de R no es 420.")

        pearson = res_data["correlacion_escolaridad_ingreso"]["pearson"]
        if "r" in pearson and "p_value" in pearson:
            self.record_pass("R-Correlacion", f"Pearson r = {pearson['r']:.4f}, p = {pearson['p_value']:.4f}")
        else:
            self.record_fail("R-Correlacion", "Faltan métricas de correlación Pearson en JSON.")

        anova = res_data["vulnerabilidad_por_barrio"]["anova"]
        if "f_stat" in anova and "p_value" in anova:
            self.record_pass("R-ANOVA", f"ANOVA F = {anova['f_stat']:.3f}, p = {anova['p_value']:.4f}")
        else:
            self.record_fail("R-ANOVA", "Faltan métricas de ANOVA en JSON.")

        # Reporte escrito APA 7
        report_path = OUTPUT_DIR / "reporte_econometrico_apa7.txt"
        if report_path.exists() and report_path.stat().st_size > 2000:
            self.record_pass("R-Reporte", f"Reporte APA 7 generado exitosamente ({report_path.stat().st_size} bytes)")
        else:
            self.record_fail("R-Reporte", "Reporte APA 7 no generado o tamaño insuficiente.")

        # Figuras PNG (300 DPI) y SVG
        figuras = [
            "figura1_correlacion_escolaridad_ingreso",
            "figura2_vulnerabilidad_social_barrios",
            "figura3_brecha_ingreso_genero_minimo",
            "figura4_informalidad_mypes_rubro",
            "figura5_embudo_marketing_multicanal"
        ]

        for fig_name in figuras:
            png_file = OUTPUT_DIR / f"{fig_name}.png"
            svg_file = OUTPUT_DIR / f"{fig_name}.svg"

            if png_file.exists() and png_file.stat().st_size > 50000:
                self.record_pass("Figura-PNG", f"{png_file.name} presente en alta resolución ({png_file.stat().st_size / 1024:.1f} KB)")
            else:
                self.record_fail("Figura-PNG", f"Figura PNG ausente o corrupta: {png_file}")

            if svg_file.exists() and svg_file.stat().st_size > 5000:
                self.record_pass("Figura-SVG", f"{svg_file.name} presente en formato vectorial ({svg_file.stat().st_size / 1024:.1f} KB)")
            else:
                self.record_fail("Figura-SVG", f"Figura SVG ausente o corrupta: {svg_file}")

    def test_web_dashboard(self):
        """4. Valida la integridad del Dashboard Web docs/dashboard.html."""
        logger.info("--- 4. Verificando Dashboard Gerencial Web (docs/dashboard.html) ---")
        dash_file = DOCS_DIR / "dashboard.html"
        if not dash_file.exists():
            self.record_fail("Web-Dashboard", "No se encontró docs/dashboard.html")
            return

        with open(dash_file, "r", encoding="utf-8") as f:
            content = f.read()

        required_snippets = [
            ("Leaflet Map Container", 'id="villarricaMap"'),
            ("Leaflet CDN JS", 'leaflet@1.9.4'),
            ("Chart.js CDN", 'chart.umd.min.js'),
            ("Salario Mínimo Legal", '3.044.000'),
            ("Filtro Barrio", 'id="filterBarrio"'),
            ("Filtro Género", 'id="filterGenero"'),
            ("Filtro Rubro", 'id="filterRubro"'),
            ("Filtro Canal", 'id="filterCanal"'),
            ("Pestaña 1 Social", 'id="tab-social"'),
            ("Pestaña 2 MYPEs", 'id="tab-mypes"'),
            ("Pestaña 3 Marketing", 'id="tab-marketing"'),
            ("Pestaña 4 Explorador", 'id="tab-explorer"'),
            ("Gráfico Brecha Barrio", 'id="chartBrechaSalarialBarrio"'),
            ("Gráfico Embudo Marketing", 'id="chartEmbudoMarketing"'),
            ("Gráfico Informalidad Rubro", 'id="chartInformalidadRubro"')
        ]

        for name, snippet in required_snippets:
            if snippet in content:
                self.record_pass("Web-Component", f"{name} detectado en dashboard.html")
            else:
                self.record_fail("Web-Component", f"Falta componente en dashboard.html: {name} ('{snippet}')")

    def run_all(self):
        logger.info("==============================================================================")
        logger.info("INICIANDO PROTOCOLO DE VALIDACIÓN FASE 4 - PROYECTO INTERDISCIPLINARIO UNVES")
        logger.info("==============================================================================")
        self.test_database_views()
        self.test_exported_datasets()
        self.test_r_econometric_outputs()
        self.test_web_dashboard()

        logger.info("==============================================================================")
        logger.info(f"RESUMEN DE VALIDACIÓN: {self.passed_tests} pruebas superadas.")
        if self.errors:
            logger.error(f"Se encontraron {len(self.errors)} errores en la validación:")
            for e in self.errors:
                logger.error(f" - {e}")
            sys.exit(1)
        else:
            logger.info("✔ TODAS LAS PRUEBAS DE LA FASE 4 FUERON SUPERADAS CON ÉXITO (100% OK).")
            logger.info("==============================================================================")


if __name__ == "__main__":
    validator = Phase4Validator()
    validator.run_all()
