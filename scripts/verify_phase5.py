"""
Script de Verificación de Integridad y Coherencia Documental - FASE 5 (UNVES 2026)
Cátedras: Sistema de Información Gerencial | Realidad Social | Marketing Social
Valida coherencia de citas APA 7, numeración de tablas y figuras, enlaces a evidencias
digitales y consistencia matemática de los datos contra PostgreSQL y resultados de R.
Sesión 16 - Indicador 6 de Rúbrica Institucional
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de Logging Institucional UNVES
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [UNVES-VERIFY-P5] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("unves.verify.p5")

# Directorios Base
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
OUTPUT_DIR = BASE_DIR / "r-analysis" / "output"
KOBO_DIR = BASE_DIR / "kobo"
DB_DIR = BASE_DIR / "db"

# Base de Datos PostgreSQL
DB_NAME = os.getenv("PGDATABASE", "unves_sig_2026")
DB_USER = os.getenv("PGUSER", os.getenv("USER", "johnnyoviedo"))
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = int(os.getenv("PGPORT", "5432"))
DB_PASS = os.getenv("PGPASSWORD", "")
DATABASE_URL = os.getenv("DATABASE_URL")


class Phase5IntegrityValidator:
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

    def verify_document_deliverables_existence(self):
        """1. Valida que los 4 documentos principales de la Fase 5 existan y tengan contenido adecuado."""
        logger.info("--- 1. Verificando Existencia y Longitud de Documentos Entregables ---")
        deliverables = [
            ("capitulo_sig.md", 15000, "Capítulo de Cátedra SIG (Sesión 13 - Indicador 6)"),
            ("informe_final_unves_2026.md", 20000, "Informe Académico Interdisciplinario Final APA 7 (Sesión 14)"),
            ("dossier_evidencias_digitales.md", 10000, "Dossier Institucional de Evidencias Digitales (Sesión 15)"),
            ("guion_defensa_oral_y_diapositivas.md", 12000, "Guión de Defensa Oral y Diapositivas (Sesiones 16 y 17)")
        ]

        for filename, min_bytes, description in deliverables:
            filepath = DOCS_DIR / filename
            if not filepath.exists():
                self.record_fail("Doc-Existence", f"No se encontró el archivo obligatorio {filename}")
                continue

            size = filepath.stat().st_size
            if size >= min_bytes:
                self.record_pass("Doc-Existence", f"{filename} presente con tamaño válido ({size:,} bytes) - {description}")
            else:
                self.record_fail("Doc-Size", f"{filename} tiene contenido insuficiente ({size} bytes, se esperaban > {min_bytes})")

    def verify_institutional_headers(self):
        """2. Valida la presencia de portadas oficiales institucionales y nombres docentes de la UNVES."""
        logger.info("--- 2. Verificando Portada Oficial y Mesa Docente Evaluadora ---")
        required_terms = [
            "UNIVERSIDAD NACIONAL DE VILLARRICA DEL ESPÍRITU SANTO",
            "FACULTAD DE CIENCIAS ECONÓMICAS",
            "Clara Demattei",
            "Gerardo Ortiz",
            "Ramona Demattei",
            "Villarrica",
            "2026"
        ]

        for doc_name in ["capitulo_sig.md", "informe_final_unves_2026.md", "guion_defensa_oral_y_diapositivas.md"]:
            doc_path = DOCS_DIR / doc_name
            if not doc_path.exists():
                continue
            text = doc_path.read_text(encoding="utf-8")
            missing = [term for term in required_terms if term not in text]
            if not missing:
                self.record_pass("Doc-Headers", f"{doc_name} contiene todos los metadatos institucionales y mesa docente.")
            else:
                self.record_fail("Doc-Headers", f"{doc_name} carece de los siguientes términos obligatorios: {missing}")

    def verify_apa7_tables_and_figures(self):
        """3. Valida la correlación, numeración y estructura de Tablas y Figuras APA 7."""
        logger.info("--- 3. Verificando Numeración y Títulos de Tablas y Figuras APA 7 ---")
        report_path = DOCS_DIR / "informe_final_unves_2026.md"
        if not report_path.exists():
            self.record_fail("APA7-Check", "informe_final_unves_2026.md no encontrado.")
            return

        content = report_path.read_text(encoding="utf-8")

        # Tablas APA 7 esperadas (Tablas 1 a 5)
        expected_tables = [
            ("Tabla 1", "Estadísticas Descriptivas de las Variables Socioeconómicas"),
            ("Tabla 2", "Estimación del Modelo de Capital Humano de Mincer"),
            ("Tabla 3", "Índice de Vulnerabilidad Social e Ingresos por Barrio"),
            ("Tabla 4", "Brecha Salarial de Género"),
            ("Tabla 5", "Rendimiento Consolidado de la Campaña")
        ]

        for table_tag, table_title in expected_tables:
            if table_tag in content and table_title in content:
                self.record_pass("APA7-Table", f"{table_tag} documentada con formato y título APA 7: '{table_title}'")
            else:
                self.record_fail("APA7-Table", f"No se encontró {table_tag} o su título correspondiente en el informe.")

        # Figuras APA 7 esperadas (Figuras 1 a 15, en orden de aparición)
        expected_figures = [
            ("Figura 1", "Correlación entre Años de Escolaridad e Ingreso Mensual"),
            ("Figura 2", "Índice de Vulnerabilidad Social en los Siete Barrios"),
            ("Figura 3", "Distribución de Ingresos Mensuales por Género"),
            ("Figura 4", "Tasa Media de Informalidad Laboral en las MYPEs por Rubro"),
            ("Figura 5", "Situación Tributaria de las MYPEs"),
            ("Figura 6", "Barreras Patronales para la Inscripción"),
            ("Figura 7", "Motivos de No Aporte al IPS"),
            ("Figura 8", "Diagrama Entidad-Relación"),
            ("Figura 9", "Pestaña 1: Diagnóstico Social y Territorio"),
            ("Figura 10", "Pestaña 2: Gestión Productiva y MYPEs"),
            ("Figura 11", "Pestaña 3: Marketing Social"),
            ("Figura 12", "Pestaña 4: Explorador de Microdatos"),
            ("Figura 13", "Embudo de Conversión Multicanal"),
            ("Figura 14", "Evolución Diaria de Consultas y Derivaciones"),
            ("Figura 15", "Costo por Consulta y por Derivación según Canal")
        ]

        for fig_tag, fig_title in expected_figures:
            if re.search(rf"\*\*{fig_tag}\*\*\n\n\*[^*\n]*{re.escape(fig_title)}", content):
                self.record_pass("APA7-Figure", f"{fig_tag} documentada con formato y título APA 7: '{fig_title}'")
            else:
                self.record_fail("APA7-Figure", f"No se encontró {fig_tag} o su título en el informe.")

    def verify_apa7_references(self):
        """4. Valida citas y lista de referencias bibliográficas en APA 7.ª edición."""
        logger.info("--- 4. Verificando Referencias Bibliográficas APA 7 ---")
        report_path = DOCS_DIR / "informe_final_unves_2026.md"
        content = report_path.read_text(encoding="utf-8")

        required_refs = [
            "Banco Central del Paraguay",
            "Dirección Nacional de Ingresos Tributarios",
            "Instituto Nacional de Estadística",
            "Instituto de Previsión Social",
            "Lee, N. R., & Kotler, P.",
            "Mincer, J. (1974)",
            "Ministerio de Trabajo, Empleo y Seguridad Social",
            "Organización Internacional del Trabajo"
        ]

        found_all = True
        for ref in required_refs:
            if ref in content or ("Kotler" in ref and "Kotler" in content):
                self.record_pass("APA7-Ref", f"Referencia institucional validada: {ref}")
            else:
                self.record_fail("APA7-Ref", f"Falta referencia obligatoria: {ref}")
                found_all = False

    def verify_digital_evidences_links(self):
        """5. Valida que todos los archivos referenciados en el dossier y el informe existan físicamente."""
        logger.info("--- 5. Verificando Existencia Física de Enlaces de Evidencias Digitales ---")
        target_files = [
            DOCS_DIR / "dashboard.html",
            DOCS_DIR / "dashboard_data.js",
            DOCS_DIR / "dashboard_data.json",
            DOCS_DIR / "diagrama_er.html",
            DOCS_DIR / "diagrama_er.svg",
            OUTPUT_DIR / "figura1_correlacion_escolaridad_ingreso.png",
            OUTPUT_DIR / "figura1_correlacion_escolaridad_ingreso.svg",
            OUTPUT_DIR / "figura2_vulnerabilidad_social_barrios.png",
            OUTPUT_DIR / "figura2_vulnerabilidad_social_barrios.svg",
            OUTPUT_DIR / "figura3_brecha_ingreso_genero_minimo.png",
            OUTPUT_DIR / "figura3_brecha_ingreso_genero_minimo.svg",
            OUTPUT_DIR / "figura4_informalidad_mypes_rubro.png",
            OUTPUT_DIR / "figura4_informalidad_mypes_rubro.svg",
            OUTPUT_DIR / "figura5_embudo_marketing_multicanal.png",
            OUTPUT_DIR / "figura5_embudo_marketing_multicanal.svg",
            OUTPUT_DIR / "figura6_situacion_tributaria_ruc_mypes.png",
            OUTPUT_DIR / "figura7_barreras_patronales_ips.png",
            OUTPUT_DIR / "figura8_motivos_no_aporte_ips_trabajadores.png",
            OUTPUT_DIR / "figura9_costo_por_canal_marketing.png",
            OUTPUT_DIR / "figura10_evolucion_diaria_marketing.png",
            KOBO_DIR / "form_specification.md",
            KOBO_DIR / "survey_schema.json",
            DB_DIR / "schema.sql"
        ]

        for filepath in target_files:
            if filepath.exists() and filepath.stat().st_size > 0:
                self.record_pass("Evidence-Link", f"Artefacto verificado: {filepath.name} ({filepath.stat().st_size:,} bytes)")
            else:
                self.record_fail("Evidence-Link", f"Artefacto faltante o vacío: {filepath}")

    def verify_data_consistency_with_postgresql_and_r(self):
        """6. Valida consistencia matemática exacta entre los documentos y PostgreSQL / R."""
        logger.info("--- 6. Verificando Coherencia de Datos Numéricos entre Documentos, DB y R ---")
        # Cargar resultados de R
        r_json_path = OUTPUT_DIR / "resultados_econometricos.json"
        if not r_json_path.exists():
            self.record_fail("Data-Coherence", "resultados_econometricos.json no existe.")
            return

        with open(r_json_path, "r", encoding="utf-8") as f:
            r_data = json.load(f)

        # Consultar PostgreSQL
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                # 1. Total trabajadores e ingreso medio
                cur.execute("SELECT count(*), avg(ingreso_mensual_pyg) FROM trabajadores;")
                count_t, avg_ingreso = cur.fetchone()

                # 2. Total unidades productivas
                cur.execute("SELECT count(*) FROM unidades_productivas;")
                count_u = cur.fetchone()[0]

                # 3. Métricas de marketing
                cur.execute("SELECT sum(presupuesto_invertido_pyg), sum(derivaciones_totales_formalizacion) FROM marketing_kpis;")
                presupuesto_mkt, derivaciones_mkt = cur.fetchone()

            conn.close()

            # Contrastes de exactitud
            if count_t == 420 and r_data["metadatos"]["muestra_trabajadores"] == 420:
                self.record_pass("Consistency-Muestra", "Muestra de trabajadores N=420 consistente en DB y R")
            else:
                self.record_fail("Consistency-Muestra", f"Discrepancia en trabajadores: DB={count_t}, R={r_data['metadatos']['muestra_trabajadores']}")

            if count_u == 135 and r_data["metadatos"]["muestra_unidades"] == 135:
                self.record_pass("Consistency-MYPEs", "Muestra de unidades productivas N=135 consistente en DB y R")
            else:
                self.record_fail("Consistency-MYPEs", f"Discrepancia en MYPEs: DB={count_u}")

            # Ingreso medio
            media_r = r_data["descriptivos_trabajadores"]["ingreso"]["media"]
            if abs(float(avg_ingreso) - media_r) < 1.0:
                self.record_pass("Consistency-Ingreso", f"Ingreso medio consistente: Gs. {float(avg_ingreso):,.0f} (DB y R)")
            else:
                self.record_fail("Consistency-Ingreso", f"Discrepancia ingreso medio: DB={avg_ingreso}, R={media_r}")

            # Salario mínimo y brecha
            salario_min = r_data["metadatos"]["salario_minimo_legal"]
            if salario_min == 3044000:
                self.record_pass("Consistency-SalarioMinimo", "Salario mínimo de referencia validado en Gs. 3.044.000")
            else:
                self.record_fail("Consistency-SalarioMinimo", f"Salario mínimo inesperado: {salario_min}")

            # Correlación de Pearson
            pearson_r = r_data["correlacion_escolaridad_ingreso"]["pearson"]["r"]
            informe_text = (DOCS_DIR / "informe_final_unves_2026.md").read_text(encoding="utf-8")
            if f"r = {pearson_r:.4f}" in informe_text:
                self.record_pass("Consistency-Pearson", f"Correlación de Pearson validada: r = {pearson_r:.4f}")
            else:
                self.record_fail("Consistency-Pearson", f"El informe no reporta el r de Pearson calculado en R: {pearson_r:.4f}")

            # Marketing: Presupuesto y Derivaciones
            if int(derivaciones_mkt) == 2217:
                self.record_pass("Consistency-Marketing", "Total derivaciones de formalización consistente: 2.217 derivaciones")
            else:
                self.record_fail("Consistency-Marketing", f"Derivaciones inesperadas: {derivaciones_mkt}")

            if float(presupuesto_mkt) == 5504000.0:
                self.record_pass("Consistency-Presupuesto", "Presupuesto total de marketing social consistente: Gs. 5.504.000")
            else:
                self.record_fail("Consistency-Presupuesto", f"Presupuesto inesperado: {presupuesto_mkt}")

            # Verificar que el informe mencione exactamente los valores calculados
            ingreso_medio_txt = f"{round(media_r):,}".replace(",", ".")
            pct_bajo_minimo_txt = f"{r_data['descriptivos_trabajadores']['proporciones']['pct_bajo_minimo']:.2f}%"
            for term in [ingreso_medio_txt, "3.044.000", f"{pearson_r:.4f}", "2.217", "5.504.000", pct_bajo_minimo_txt]:
                if term in informe_text:
                    self.record_pass("Consistency-ReportText", f"Informe contiene valor matemático validado: '{term}'")
                else:
                    self.record_fail("Consistency-ReportText", f"Informe carece del valor exacto: '{term}'")

        except Exception as e:
            self.record_fail("Data-Coherence-DB", f"Fallo al conectar o verificar consistencia con PostgreSQL: {e}")

    def run_all_checks(self):
        logger.info("==============================================================================")
        logger.info("INICIANDO PROTOCOLO DE VALIDACIÓN FASE 5 - PROYECTO INTERDISCIPLINARIO UNVES")
        logger.info("==============================================================================")

        self.verify_document_deliverables_existence()
        self.verify_institutional_headers()
        self.verify_apa7_tables_and_figures()
        self.verify_apa7_references()
        self.verify_digital_evidences_links()
        self.verify_data_consistency_with_postgresql_and_r()

        logger.info("==============================================================================")
        logger.info(f"RESUMEN DE VALIDACIÓN FASE 5: {self.passed_tests} pruebas superadas.")
        if self.errors:
            logger.error(f"Se registraron {len(self.errors)} errores de validación:")
            for err in self.errors:
                logger.error(f"  -> {err}")
            return False
        else:
            logger.info("✔ TODAS LAS PRUEBAS DE LA FASE 5 FUERON SUPERADAS CON ÉXITO (100% OK).")
            logger.info("==============================================================================")
            return True


if __name__ == "__main__":
    validator = Phase5IntegrityValidator()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)
