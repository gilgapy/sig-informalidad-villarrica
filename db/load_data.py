"""
Pipeline ETL Reproducible - Proyecto Interdisciplinario UNVES 2026
Cátedras: Sistema de Información Gerencial | Realidad Social | Marketing Social
Poblado de Base de Datos PostgreSQL en 3FN a partir de data/processed/
"""

import csv
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
import psycopg2
from psycopg2.extras import execute_batch

# Configuración de Logging Estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [UNVES-ETL] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("unves.etl")

# Configuración de Conexión a PostgreSQL (vía variables de entorno)
DB_NAME = os.getenv("PGDATABASE", "unves_sig_2026")
DB_USER = os.getenv("PGUSER", os.getenv("USER", "johnnyoviedo"))
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = int(os.getenv("PGPORT", "5432"))
DB_PASS = os.getenv("PGPASSWORD", "")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection() -> psycopg2.extensions.connection:
    """Establece y retorna conexión segura a PostgreSQL con manejo de errores."""
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
        logger.error(f"Fallo al conectar con la base de datos PostgreSQL: {err}")
        raise


def seed_catalogs(cursor: psycopg2.extensions.cursor) -> None:
    """Puebla las tablas maestras de catálogo y dimensiones (Normalización 3FN)."""
    logger.info("Poblando catálogos maestros de dimensiones...")

    # 1. Catálogo de Barrios de Villarrica
    barrios_data = [
        ("Centro", -25.7849, -25.7799, -56.4496, -56.4446, 140.0, 148.0, 0.22,
         "Zona comercial céntrica, comercios minoristas, trámites y servicios"),
        ("Ybaroty", -25.7723, -25.7673, -56.4480, -56.4430, 135.0, 144.0, 0.18,
         "Barrio tradicional histórico, talleres artesanales y negocios familiares"),
        ("San Miguel", -25.7790, -25.7740, -56.4403, -56.4353, 132.0, 140.0, 0.16,
         "Zona residencial y mixta, talleres mecánicos y despensas"),
        ("Santa Librada", -25.7942, -25.7892, -56.4518, -56.4468, 138.0, 146.0, 0.15,
         "Zona densa con puestos de comida, confección y transporte local"),
        ("Estación", -25.7962, -25.7912, -56.4630, -56.4580, 130.0, 139.0, 0.13,
         "Entorno del Parque M. Ortiz Guerrero y antigua estación, oficios diversos"),
        ("Lomas Valentinas", -25.7833, -25.7783, -56.4611, -56.4561, 142.0, 152.0, 0.09,
         "Zona oeste de la ciudad, comercio barrial y servicios independientes"),
        ("Tuyutimí", -25.7748, -25.7698, -56.4607, -56.4557, 128.0, 137.0, 0.07,
         "Sector periurbano noroeste, oficios de construcción y reciclaje")
    ]
    query_barrios = """
        INSERT INTO barrios (nombre, lat_min, lat_max, lon_min, lon_max, alt_min, alt_max, peso_muestral, descripcion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (nombre) DO UPDATE SET
            lat_min = EXCLUDED.lat_min,
            lat_max = EXCLUDED.lat_max,
            lon_min = EXCLUDED.lon_min,
            lon_max = EXCLUDED.lon_max,
            peso_muestral = EXCLUDED.peso_muestral,
            descripcion = EXCLUDED.descripcion;
    """
    execute_batch(cursor, query_barrios, barrios_data)

    # 2. Catálogo de Oficios Informales
    oficios_data = [
        ("Confección y bordado artesanal (Ao Po'i / Prendas)", "Manufactura Textil", 2250000,
         "Bordado artesanal tradicional, costura y confección de prendas típicas"),
        ("Comercio al paso / Copetín / Venta de alimentos", "Gastronomía Callejera", 2600000,
         "Puestos de comida al paso, copetines barriales y elaboración culinaria rápida"),
        ("Construcción / Albañilería / Pintura", "Construcción y Mantenimiento", 2900000,
         "Albañilería particular, jornaleros de obra civil menor y pintores de brocha"),
        ("Mototaxi / Reparto y delivery en motocicleta", "Transporte y Logística", 2450000,
         "Servicios de traslado de pasajeros en dos ruedas y delivery local"),
        ("Taller mecánico menor / Gomería / Chapa y pintura", "Servicios Técnicos", 3050000,
         "Reparación de motocicletas, auxilio mecánico ligero y parchado de neumáticos"),
        ("Venta ambulante / Feria municipal / Mercaderías", "Comercio Ambulante", 2050000,
         "Venta móvil de productos varios en el centro y feria municipal de Villarrica"),
        ("Servicios domésticos y limpieza informal", "Servicios Personales", 1850000,
         "Labores domésticas por jornal, limpieza de locales y casas de familia"),
        ("Carpintería / Herrería / Mantenimiento general", "Oficios Técnicos", 2850000,
         "Fabricación y refacción menor de muebles de madera y herrería liviana"),
        ("Zapatería y reparación de calzado / Marroquinería", "Artesanías y Reparación", 2200000,
         "Reparación tradicional de calzados y artículos de cuero")
    ]
    query_oficios = """
        INSERT INTO oficios (nombre, sector, ingreso_base_pyg, descripcion)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (nombre) DO NOTHING;
    """
    execute_batch(cursor, query_oficios, oficios_data)

    # 3. Catálogo de Rubros MYPEs
    rubros_mypes_data = [
        ("Comercio minorista y despensa de barrio", "Comercio", 12000000, 1, 4),
        ("Confección textil y talleres de Ao Po'i", "Manufactura", 16000000, 2, 6),
        ("Gastronomía, copetines y rotiserías", "Gastronomía", 14000000, 2, 5),
        ("Servicios técnicos, talleres y gomerías", "Servicios", 15000000, 1, 5),
        ("Transporte de cargas livianas y fletes", "Logística y Transporte", 11000000, 1, 3)
    ]
    query_rubros = """
        INSERT INTO rubros_mypes (nombre, sector_economico, facturacion_base_pyg, rango_trabajadores_min, rango_trabajadores_max)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (nombre) DO NOTHING;
    """
    execute_batch(cursor, query_rubros, rubros_mypes_data)

    # 4. Catálogo de Medios de Pago
    medios_pago_data = [
        ("efectivo", "Efectivo en Guaraníes", "Efectivo", False, "Moneda física en efectivo"),
        ("tigo_money", "Billetera Tigo Money", "Billetera Móvil (EMP)", True, "Billetera móvil operada por Entidad de Medio de Pago"),
        ("billetera_zimple", "Billetera Zimple", "Billetera Móvil (EMP)", True, "Billetera electrónica de inclusión financiera"),
        ("sipap_transferencia", "Transferencia Bancaria SIPAP", "Banca Digital / SIPAP", True, "Sistema de Pagos del Paraguay (BCP)"),
        ("qr_bancario", "Código QR Bancario", "Banca Digital / SIPAP", True, "Cobro instantáneo interoperable mediante código QR"),
        ("tarjeta_debito_credito", "Tarjetas Débito y Crédito (POS)", "POS / Tarjetas", True, "Cobro electrónico por terminal POS")
    ]
    query_medios = """
        INSERT INTO medios_pago (codigo, nombre, categoria, es_digital, descripcion)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (codigo) DO NOTHING;
    """
    execute_batch(cursor, query_medios, medios_pago_data)

    # 5. Catálogo de Canales de Marketing
    canales_marketing_data = [
        ("META_ADS", "Meta Ads (Facebook & Instagram)", "Digital Pago", "Brigada de Marketing Digital UNVES",
         "Pauta segmentada por geolocalización en Villarrica y microaudiencias"),
        ("WHATSAPP", "WhatsApp Business Cátedra UNVES", "Digital Mensajería", "Consultorio Empresarial FCE-UNVES",
         "Atención directa a consultas y derivación asistida a portales"),
        ("PUNTOS_PRESENCIALES", "Puntos Presenciales / Ferias Comunitarias", "BTL / Presencial", "Brigadas de Campo UNVES",
         "Stands informativos en mercados, plazas y ferias de emprendedores"),
        ("AFICHES_QR", "Afiches con QR y Medios Locales", "OOH / Impreso", "Cátedra de Marketing Social",
         "Cartelería en paradas y despensas con escaneo de código QR hacia guía de formalización")
    ]
    query_canales = """
        INSERT INTO canales_marketing (codigo, nombre, tipo, responsable_operativo, descripcion)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (codigo) DO NOTHING;
    """
    execute_batch(cursor, query_canales, canales_marketing_data)

    # 6. Catálogo de Programas de Formalización
    programas_data = [
        ("RESIMPLE", "Régimen Simplificado para Pequeñas Unidades Económicas (RESIMPLE)",
         "Dirección Nacional de Ingresos Tributarios (DNIT)", "Tributario Simplificado (Monotributo)",
         "Ley N° 6380/19 de Modernización Tributaria", "Oficina Regional DNIT Villarrica",
         "Ingresos anuales de hasta Gs. 80.000.000, cédula de identidad y declaración jurada básica.",
         "Régimen tributario unipersonal con cuota fija trimestral que exonera de IVA e IRP.", True),
        ("SUACE", "Sistema Unificado de Apertura y Cierre de Empresas (SUACE)",
         "Ministerio de Industria y Comercio (MIC)", "Ventanilla Única Registro y Formalización",
         "Ley N° 4980/13 y Decreto Reglamentario", "Ventanilla SUACE - Gobernación del Guairá / FCE-UNVES",
         "Formulario unificado, cédula de identidad vigente, constancia RUC y comprobante de domicilio.",
         "Ventanilla única interinstitucional que centraliza trámites municipales, patronales y tributarios.", True),
        ("IPS_MICRO", "Régimen Especial de Seguridad Social para Microempresas e Independientes",
         "Instituto de Previsión Social (IPS)", "Seguro Social y Jubilación",
         "Ley N° 4933/13 (Independientes) y Ley N° 5741/16 (Microempresas)", "Agencia Regional IPS Villarrica",
         "Cédula de identidad, comprobante de ingreso o RUC RESIMPLE, declaración de actividad.",
         "Cobertura integral de salud y esquema de cotización para jubilación proporcional.", True)
    ]
    query_programas = """
        INSERT INTO programas_formalizacion (
            id_programa, nombre, institucion_rectora, tipo_beneficio, base_legal,
            contacto_villarrica, requisitos_resumen, descripcion, activo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_programa) DO UPDATE SET
            nombre = EXCLUDED.nombre,
            institucion_rectora = EXCLUDED.institucion_rectora,
            base_legal = EXCLUDED.base_legal,
            requisitos_resumen = EXCLUDED.requisitos_resumen;
    """
    execute_batch(cursor, query_programas, programas_data)
    logger.info("Catálogos maestros insertados correctamente.")


def get_catalog_lookups(cursor: psycopg2.extensions.cursor) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int], Dict[str, int]]:
    """Obtiene diccionarios de resolución ID para normalización en 3FN."""
    cursor.execute("SELECT nombre, id FROM barrios;")
    barrio_map = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT nombre, id FROM oficios;")
    oficio_map = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT nombre, id FROM rubros_mypes;")
    rubro_mype_map = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT nombre, id_canal FROM canales_marketing;")
    canal_map = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.execute("SELECT codigo, id_canal FROM canales_marketing;")
    for row in cursor.fetchall():
        canal_map[row[0]] = row[1]

    return barrio_map, oficio_map, rubro_mype_map, canal_map


def classify_vulnerability(score: float) -> str:
    """Clasifica el índice sintético de vulnerabilidad social en rangos estándar."""
    if score < 30.0:
        return "Vulnerabilidad Baja"
    if score < 50.0:
        return "Vulnerabilidad Media"
    if score < 70.0:
        return "Vulnerabilidad Alta"
    return "Vulnerabilidad Crítica"


def load_unidades_productivas(
    cursor: psycopg2.extensions.cursor,
    filepath: Path,
    barrio_map: Dict[str, int],
    rubro_mype_map: Dict[str, int]
) -> int:
    """Carga y normaliza el dataset de Unidades Productivas (MYPEs de Villarrica)."""
    logger.info(f"Cargando dataset de unidades productivas desde {filepath}...")
    unidades_rows: List[Tuple[Any, ...]] = []
    unidades_medios: List[Tuple[str, str]] = []

    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            unidad_id = row["id_unidad"]
            barrio_id = barrio_map[row["barrio"]]
            rubro_id = rubro_mype_map[row["rubro_actividad"]]

            unidades_rows.append((
                unidad_id,
                row["nombre_establecimiento"],
                barrio_id,
                float(row["latitud"]),
                float(row["longitud"]),
                rubro_id,
                int(row["antiguedad_anios"]),
                int(row["total_trabajadores"]),
                int(row["trabajadores_sin_ips"]),
                int(row["trabajadores_con_ips"]),
                float(row["tasa_informalidad_laboral_pct"]),
                row["estado_tributario_ruc"],
                row["motivo_no_aporte_ips"],
                float(row["ingreso_mensual_estimado_pyg"]),
                row["disposicion_formalizar"]
            ))

            # Mapeo relacional de medios de pago aceptados
            medios_str = row.get("medios_pago") or row.get("medios_pago_aceptados") or ""
            unidades_medios.append((unidad_id, "efectivo"))
            if "tigo_money" in medios_str or "Tigo" in medios_str:
                unidades_medios.append((unidad_id, "tigo_money"))
            if "billetera_zimple" in medios_str or "Zimple" in medios_str:
                unidades_medios.append((unidad_id, "billetera_zimple"))
            if "sipap" in medios_str or "SIPAP" in medios_str:
                unidades_medios.append((unidad_id, "sipap_transferencia"))
            if "qr" in medios_str or "QR" in medios_str:
                unidades_medios.append((unidad_id, "qr_bancario"))
            if "tarjeta" in medios_str or "Tarjetas" in medios_str:
                unidades_medios.append((unidad_id, "tarjeta_debito_credito"))

    query_unidades = """
        INSERT INTO unidades_productivas (
            id_unidad, nombre_establecimiento, barrio_id, latitud, longitud,
            rubro_id, antiguedad_anios, total_trabajadores, trabajadores_sin_ips,
            trabajadores_con_ips, tasa_informalidad_laboral_pct, estado_tributario_ruc,
            motivo_no_aporte_ips, ingreso_mensual_estimado_pyg, disposicion_formalizar
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_unidad) DO NOTHING;
    """
    execute_batch(cursor, query_unidades, unidades_rows)

    query_unidades_medios = """
        INSERT INTO unidades_medios_pago (unidad_id, medio_pago_codigo)
        VALUES (%s, %s)
        ON CONFLICT (unidad_id, medio_pago_codigo) DO NOTHING;
    """
    execute_batch(cursor, query_unidades_medios, list(set(unidades_medios)))

    logger.info(f"Unidades productivas insertadas: {len(unidades_rows)}")
    return len(unidades_rows)


def load_trabajadores(
    cursor: psycopg2.extensions.cursor,
    filepath: Path,
    barrio_map: Dict[str, int],
    oficio_map: Dict[str, int]
) -> int:
    """Carga y normaliza el dataset de trabajadores, sus indicadores y medios de pago."""
    logger.info(f"Cargando dataset de trabajadores desde {filepath}...")
    trabajadores_rows: List[Tuple[Any, ...]] = []
    indicadores_rows: List[Tuple[Any, ...]] = []
    medios_rows: List[Tuple[str, str]] = []

    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trab_id = row["id_trabajador"]
            barrio_id = barrio_map[row["barrio"]]
            oficio_id = oficio_map[row["oficio_rubro"]]
            unidad_id = row.get("unidad_productiva_id") if row.get("unidad_productiva_id") and row.get("unidad_productiva_id").strip() else None

            # Tupla entidad Trabajadores
            trabajadores_rows.append((
                trab_id,
                row["kobo_uuid"],
                row["fecha_recoleccion"],
                barrio_id,
                float(row["latitud"]),
                float(row["longitud"]),
                int(row["edad"]),
                row["genero"],
                oficio_id,
                int(row["antiguedad_oficio_anios"]),
                float(row["ingreso_mensual_pyg"]),
                int(row["horas_semanales"]),
                row["cobertura_ips"],
                row["motivo_no_ips"],
                row["posee_smartphone"],
                row["tipo_conectividad"],
                row["conoce_resimple"],
                row["interes_formalizacion"],
                unidad_id
            ))

            # Tupla entidad Indicadores Sociales (10 métricas - Cátedra Realidad Social)
            vuln_score = float(row["indice_vulnerabilidad_social"])
            indicadores_rows.append((
                trab_id,
                float(row["salario_minimo_referencia_pyg"]),
                float(row["brecha_salario_pyg"]),
                row["situacion_respecto_minimo"],
                row["condicion_jornada"],
                row["nivel_educativo"],
                int(row["anios_estudio"]),
                row["brecha_digital"],
                row["acepta_pagos_digitales"],
                int(row["personas_a_cargo"]),
                row["tenencia_vivienda"],
                vuln_score,
                classify_vulnerability(vuln_score)
            ))

            # Tabla relacional N:M Medios de Pago
            medios_str = row.get("medios_pago_habilitados") or ""
            if row.get("usa_efectivo") == "1" or "efectivo" in medios_str:
                medios_rows.append((trab_id, "efectivo"))
            if row.get("usa_tigo_money") == "1" or "tigo_money" in medios_str:
                medios_rows.append((trab_id, "tigo_money"))
            if row.get("usa_billetera_zimple") == "1" or "billetera_zimple" in medios_str:
                medios_rows.append((trab_id, "billetera_zimple"))
            if row.get("usa_sipap") == "1" or "sipap_transferencia" in medios_str or "SIPAP" in medios_str:
                medios_rows.append((trab_id, "sipap_transferencia"))
            if row.get("usa_qr_bancario") == "1" or "qr_bancario" in medios_str or "QR" in medios_str:
                medios_rows.append((trab_id, "qr_bancario"))

    # Inserción en batch para alta eficiencia
    query_trabajadores = """
        INSERT INTO trabajadores (
            id_trabajador, kobo_uuid, fecha_recoleccion, barrio_id, latitud, longitud,
            edad, genero, oficio_id, antiguedad_oficio_anios, ingreso_mensual_pyg,
            horas_semanales, cobertura_ips, motivo_no_ips, posee_smartphone,
            tipo_conectividad, conoce_resimple, interes_formalizacion, unidad_productiva_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_trabajador) DO NOTHING;
    """
    execute_batch(cursor, query_trabajadores, trabajadores_rows)

    query_indicadores = """
        INSERT INTO indicadores_sociales (
            trabajador_id, salario_minimo_referencia_pyg, brecha_salario_pyg,
            situacion_respecto_minimo, condicion_jornada, nivel_educativo,
            anios_estudio, brecha_digital, acepta_pagos_digitales, personas_a_cargo,
            tenencia_vivienda, indice_vulnerabilidad_social, clasificacion_vulnerabilidad
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (trabajador_id) DO NOTHING;
    """
    execute_batch(cursor, query_indicadores, indicadores_rows)

    query_medios = """
        INSERT INTO trabajadores_medios_pago (trabajador_id, medio_pago_codigo)
        VALUES (%s, %s)
        ON CONFLICT (trabajador_id, medio_pago_codigo) DO NOTHING;
    """
    execute_batch(cursor, query_medios, list(set(medios_rows)))

    logger.info(f"Trabajadores insertados: {len(trabajadores_rows)}, Indicadores: {len(indicadores_rows)}, Medios: {len(medios_rows)}")
    return len(trabajadores_rows)


def load_marketing_kpis(
    cursor: psycopg2.extensions.cursor,
    filepath: Path,
    canal_map: Dict[str, int]
) -> int:
    """Carga y normaliza métricas multicanal de Marketing Social."""
    logger.info(f"Cargando dataset de marketing social desde {filepath}...")
    kpi_rows: List[Tuple[Any, ...]] = []

    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            canal_key = row.get("codigo_canal") or row.get("canal") or row.get("canal_nombre")
            canal_id = canal_map[canal_key]
            kpi_rows.append((
                row["fecha"],
                canal_id,
                int(row["impresiones_alcance"]),
                int(row["clics_interacciones"]),
                float(row["ctr_interaccion_pct"]),
                int(row["consultas_iniciadas"]),
                int(row["consultas_tema_resimple"]),
                int(row["consultas_tema_ips"]),
                int(row["derivaciones_suace_villarrica"]),
                int(row["derivaciones_ips_regional"]),
                int(row["derivaciones_totales_formalizacion"]),
                float(row["presupuesto_invertido_pyg"]),
                float(row["costo_por_consulta_pyg"])
            ))

    query_kpis = """
        INSERT INTO marketing_kpis (
            fecha, canal_id, impresiones_alcance, clics_interacciones,
            ctr_interaccion_pct, consultas_iniciadas, consultas_tema_resimple,
            consultas_tema_ips, derivaciones_suace_villarrica, derivaciones_ips_regional,
            derivaciones_totales_formalizacion, presupuesto_invertido_pyg, costo_por_consulta_pyg
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (fecha, canal_id) DO NOTHING;
    """
    execute_batch(cursor, query_kpis, kpi_rows)
    logger.info(f"Registros de marketing insertados: {len(kpi_rows)}")
    return len(kpi_rows)


def load_derivaciones_programas(
    cursor: psycopg2.extensions.cursor,
    filepath: Path
) -> int:
    """Carga las 2.217 derivaciones individuales trazables vinculadas a programas y canales."""
    logger.info(f"Cargando dataset de derivaciones desde {filepath}...")
    deriv_rows: List[Tuple[Any, ...]] = []

    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trab_id = row.get("trabajador_asociado")
            if trab_id and not trab_id.strip():
                trab_id = None
            deriv_rows.append((
                int(row["id_derivacion"]),
                row["codigo_derivacion"],
                row["fecha_derivacion"],
                row["canal_codigo"],
                row["programa_id"],
                trab_id,
                row["estado_tramite"],
                row["atendido_por"]
            ))

    query_deriv = """
        INSERT INTO derivaciones_programas (
            id_derivacion, codigo_derivacion, fecha_derivacion,
            canal_codigo, programa_id, trabajador_id, estado_tramite, atendido_por
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_derivacion) DO NOTHING;
    """
    execute_batch(cursor, query_deriv, deriv_rows)
    logger.info(f"Derivaciones individuales insertadas: {len(deriv_rows)}")
    return len(deriv_rows)


def run_pipeline() -> None:
    """Ejecuta el pipeline completo de carga y normalización con control transaccional."""
    start_time = time.time()
    logger.info("=== INICIANDO PIPELINE ETL UNVES 2026 (FASE 3) ===")

    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data" / "processed"

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Catálogos Maestros
            seed_catalogs(cursor)

            # 2. Resolutores de claves foráneas
            barrio_map, oficio_map, rubro_mype_map, canal_map = get_catalog_lookups(cursor)

            # 3. Población de Entidades Principales (MYPEs antes de trabajadores para FK empleador)
            n_unid = load_unidades_productivas(
                cursor, data_dir / "unidades_productivas.csv", barrio_map, rubro_mype_map
            )
            n_trab = load_trabajadores(
                cursor, data_dir / "trabajadores_informales.csv", barrio_map, oficio_map
            )
            n_mkt = load_marketing_kpis(
                cursor, data_dir / "marketing_campana_metricas.csv", canal_map
            )
            n_deriv = load_derivaciones_programas(
                cursor, data_dir / "derivaciones_programas.csv"
            )

        conn.commit()
        elapsed = time.time() - start_time
        logger.info("=== ETL COMPLETADO EXITOSAMENTE ===")
        logger.info(f"Resumen de Carga: {n_unid} MYPEs, {n_trab} trabajadores, {n_mkt} registros marketing, {n_deriv} derivaciones.")
        logger.info(f"Tiempo Total de Procesamiento: {elapsed:.3f} segundos.")
    except Exception as err:
        conn.rollback()
        logger.error(f"Error crítico en el pipeline ETL: {err}", exc_info=True)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    run_pipeline()
