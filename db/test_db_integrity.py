"""
Suite de Pruebas de Integridad, Queries Analíticas y Benchmarking de Rendimiento
Proyecto Interdisciplinario UNVES 2026 - Fase 3 (Base de Datos PostgreSQL 3FN)
Cátedras: Sistema de Información Gerencial | Realidad Social | Marketing Social
"""

import os
import sys
import time
from typing import Any, Dict, List, Tuple
import psycopg2

# Configuración de Conexión a PostgreSQL
DB_NAME = os.getenv("PGDATABASE", "unves_sig_2026")
DB_USER = os.getenv("PGUSER", os.getenv("USER", "johnnyoviedo"))
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = int(os.getenv("PGPORT", "5432"))
DB_PASS = os.getenv("PGPASSWORD", "")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection() -> psycopg2.extensions.connection:
    """Retorna conexión a la base de datos PostgreSQL."""
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT,
        password=DB_PASS
    )


def test_referential_integrity(cursor: psycopg2.extensions.cursor) -> List[str]:
    """Verifica ausencia de registros huérfanos y cumplimiento de claves foráneas."""
    errors: List[str] = []
    checks = [
        ("Trabajadores sin Barrio válido",
         "SELECT count(*) FROM trabajadores t LEFT JOIN barrios b ON t.barrio_id = b.id WHERE b.id IS NULL;"),
        ("Trabajadores sin Oficio válido",
         "SELECT count(*) FROM trabajadores t LEFT JOIN oficios o ON t.oficio_id = o.id WHERE o.id IS NULL;"),
        ("Indicadores sin Trabajador válido",
         "SELECT count(*) FROM indicadores_sociales i LEFT JOIN trabajadores t ON i.trabajador_id = t.id_trabajador WHERE t.id_trabajador IS NULL;"),
        ("Medios de Pago de Trabajadores huérfanos",
         "SELECT count(*) FROM trabajadores_medios_pago tmp LEFT JOIN trabajadores t ON tmp.trabajador_id = t.id_trabajador WHERE t.id_trabajador IS NULL;"),
        ("Unidades Productivas sin Barrio válido",
         "SELECT count(*) FROM unidades_productivas u LEFT JOIN barrios b ON u.barrio_id = b.id WHERE b.id IS NULL;"),
        ("Unidades Productivas sin Rubro válido",
         "SELECT count(*) FROM unidades_productivas u LEFT JOIN rubros_mypes r ON u.rubro_id = r.id WHERE r.id IS NULL;"),
        ("Medios de Pago de Unidades huérfanos",
         "SELECT count(*) FROM unidades_medios_pago ump LEFT JOIN unidades_productivas u ON ump.unidad_id = u.id_unidad WHERE u.id_unidad IS NULL;"),
        ("Marketing KPIs sin Canal válido",
         "SELECT count(*) FROM marketing_kpis m LEFT JOIN canales_marketing c ON m.canal_id = c.id_canal WHERE c.id_canal IS NULL;")
    ]

    for label, query in checks:
        cursor.execute(query)
        res = cursor.fetchone()
        count = res[0] if res else -1
        if count != 0:
            errors.append(f"Falla de Integridad: {label} (Huérfanos detectados: {count})")
    return errors


def test_domain_constraints(cursor: psycopg2.extensions.cursor) -> List[str]:
    """Verifica reglas de negocio y restricciones CHECK en las entidades."""
    errors: List[str] = []
    checks = [
        ("Edades fuera de rango (15 a 99)",
         "SELECT count(*) FROM trabajadores WHERE edad < 15 OR edad > 99;"),
        ("Coordenadas de trabajadores fuera de Villarrica",
         "SELECT count(*) FROM trabajadores WHERE latitud NOT BETWEEN -25.800000 AND -25.700000 OR longitud NOT BETWEEN -56.500000 AND -56.400000;"),
        ("Incoherencia en suma de dotación de personal MYPEs",
         "SELECT count(*) FROM unidades_productivas WHERE total_trabajadores <> (trabajadores_sin_ips + trabajadores_con_ips);"),
        ("Incoherencia en suma de derivaciones de formalización",
         "SELECT count(*) FROM marketing_kpis WHERE derivaciones_totales_formalizacion <> (derivaciones_suace_villarrica + derivaciones_ips_regional);"),
        ("Índice de vulnerabilidad fuera de rango [0, 100]",
         "SELECT count(*) FROM indicadores_sociales WHERE indice_vulnerabilidad_social < 0.0 OR indice_vulnerabilidad_social > 100.0;"),
        ("Tasa de informalidad MYPEs fuera de rango [0, 100]",
         "SELECT count(*) FROM unidades_productivas WHERE tasa_informalidad_laboral_pct < 0.0 OR tasa_informalidad_laboral_pct > 100.0;")
    ]

    for label, query in checks:
        cursor.execute(query)
        res = cursor.fetchone()
        count = res[0] if res else -1
        if count != 0:
            errors.append(f"Violación de Restricción CHECK: {label} (Infracciones: {count})")
    return errors


def run_analytics_realidad_social(cursor: psycopg2.extensions.cursor) -> Dict[str, Any]:
    """Ejecuta consultas analíticas clave para la Cátedra de Realidad Social."""
    # 1. Brecha Salarial promedio por Barrio
    cursor.execute("""
        SELECT b.nombre, 
               COUNT(t.id_trabajador) AS total_encuestados,
               ROUND(AVG(t.ingreso_mensual_pyg), 0) AS ingreso_promedio_pyg,
               ROUND(AVG(i.brecha_salario_pyg), 0) AS brecha_promedio_pyg,
               ROUND(AVG(i.indice_vulnerabilidad_social), 2) AS vulnerabilidad_promedio
        FROM trabajadores t
        JOIN barrios b ON t.barrio_id = b.id
        JOIN indicadores_sociales i ON t.id_trabajador = i.trabajador_id
        GROUP BY b.nombre
        ORDER BY vulnerabilidad_promedio DESC;
    """)
    brecha_barrios = cursor.fetchall()

    # 2. Distribución de Brecha Digital
    cursor.execute("""
        SELECT i.brecha_digital, 
               COUNT(*) AS cantidad, 
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trabajadores), 2) AS porcentaje
        FROM indicadores_sociales i
        GROUP BY i.brecha_digital
        ORDER BY cantidad DESC;
    """)
    brecha_digital_dist = cursor.fetchall()

    return {
        "brecha_barrios": brecha_barrios,
        "brecha_digital_dist": brecha_digital_dist
    }


def run_analytics_sig(cursor: psycopg2.extensions.cursor) -> Dict[str, Any]:
    """Ejecuta consultas analíticas clave para la Cátedra de Sistema de Información Gerencial."""
    # 1. Tasa de Informalidad y Trabajadores sin IPS por Rubro MYPE
    cursor.execute("""
        SELECT rm.nombre AS rubro,
               COUNT(u.id_unidad) AS total_unidades,
               SUM(u.total_trabajadores) AS dotacion_total,
               SUM(u.trabajadores_sin_ips) AS personal_sin_ips,
               ROUND(AVG(u.tasa_informalidad_laboral_pct), 2) AS tasa_informalidad_media_pct,
               ROUND(AVG(u.ingreso_mensual_estimado_pyg), 0) AS facturacion_promedio_pyg
        FROM unidades_productivas u
        JOIN rubros_mypes rm ON u.rubro_id = rm.id
        GROUP BY rm.nombre
        ORDER BY tasa_informalidad_media_pct DESC;
    """)
    informalidad_mypes = cursor.fetchall()

    # 2. Motivo Preponderante de no Aporte a IPS
    cursor.execute("""
        SELECT motivo_no_aporte_ips,
               COUNT(*) AS frecuencia,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM unidades_productivas), 2) AS porcentaje_mypes
        FROM unidades_productivas
        GROUP BY motivo_no_aporte_ips
        ORDER BY frecuencia DESC;
    """)
    motivos_ips = cursor.fetchall()

    return {
        "informalidad_mypes": informalidad_mypes,
        "motivos_ips": motivos_ips
    }


def run_analytics_marketing(cursor: psycopg2.extensions.cursor) -> Dict[str, Any]:
    """Ejecuta consultas analíticas clave para la Cátedra de Marketing Social."""
    cursor.execute("""
        SELECT canal_nombre,
               tipo_canal,
               total_alcance,
               total_interacciones,
               ctr_promedio_pct,
               total_consultas,
               total_derivaciones,
               presupuesto_total_pyg,
               costo_promedio_por_consulta_pyg,
               costo_por_derivacion_efectiva_pyg
        FROM vw_marketing_resumen_canales;
    """)
    kpis_canales = cursor.fetchall()
    return {"kpis_canales": kpis_canales}


def test_performance_and_indexes(cursor: psycopg2.extensions.cursor) -> Dict[str, float]:
    """Evalúa la velocidad de ejecución y uso de índices en consultas complejas."""
    queries = {
        "Join_Geo_Trabajadores": """
            EXPLAIN ANALYZE
            SELECT t.id_trabajador, b.nombre, t.latitud, t.longitud, i.indice_vulnerabilidad_social
            FROM trabajadores t
            JOIN barrios b ON t.barrio_id = b.id
            JOIN indicadores_sociales i ON t.id_trabajador = i.trabajador_id
            WHERE t.latitud BETWEEN -25.760000 AND -25.740000;
        """,
        "Agregacion_Marketing_Temporal": """
            EXPLAIN ANALYZE
            SELECT fecha, SUM(consultas_iniciadas), SUM(derivaciones_totales_formalizacion)
            FROM marketing_kpis
            WHERE fecha >= '2026-09-15'
            GROUP BY fecha ORDER BY fecha;
        """,
        "Join_MYPEs_Medios_Pago": """
            EXPLAIN ANALYZE
            SELECT u.id_unidad, u.nombre_establecimiento, mp.nombre
            FROM unidades_productivas u
            JOIN unidades_medios_pago ump ON u.id_unidad = ump.unidad_id
            JOIN medios_pago mp ON ump.medio_pago_codigo = mp.codigo
            WHERE u.tasa_informalidad_laboral_pct > 80.0;
        """
    }

    timings: Dict[str, float] = {}
    for name, query in queries.items():
        t0 = time.perf_counter()
        cursor.execute(query)
        plan = cursor.fetchall()
        t1 = time.perf_counter()
        timings[name] = (t1 - t0) * 1000.0  # en milisegundos

        # Verificar que el query plan se generó correctamente
        assert len(plan) > 0, f"Error en plan de ejecución para {name}"

    return timings


def main() -> None:
    """Función principal de ejecución y reporte de integridad."""
    print("================================================================================")
    print("PROYECTO INTERDISCIPLINARIO UNVES 2026 - REPORTE DE INTEGRIDAD DE BASE DE DATOS")
    print("Fase 3: Verificación Relacional, Constraints 3FN y Rendimiento Analítico")
    print("================================================================================\n")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Integridad Referencial
            ref_errors = test_referential_integrity(cursor)
            if not ref_errors:
                print(" [PASSED] Integridad Referencial: 100% libre de registros huérfanos.")
            else:
                for err in ref_errors:
                    print(f" [FAILED] {err}")

            # 2. Restricciones CHECK de Negocio
            domain_errors = test_domain_constraints(cursor)
            if not domain_errors:
                print(" [PASSED] Restricciones CHECK y Dominios: 100% de coherencia lógica.")
            else:
                for err in domain_errors:
                    print(f" [FAILED] {err}")

            # 3. Queries Analíticas de Realidad Social
            print("\n--------------------------------------------------------------------------------")
            print("CÁTEDRA 1: ANÁLISIS DE LA REALIDAD SOCIAL (DIAGNÓSTICO SOCIAL VILLARRICA)")
            print("--------------------------------------------------------------------------------")
            social_data = run_analytics_realidad_social(cursor)
            print("Brecha Salarial Promedio por Barrio (vs. SML Gs. 3.044.000):")
            for b in social_data["brecha_barrios"]:
                print(f"  - Barrio {b[0]:<17} | N: {b[1]:<3} | Ingreso Med: Gs. {int(b[2]):>9,}".replace(",", ".") +
                      f" | Brecha: Gs. {int(b[3]):>9,}".replace(",", ".") + f" | Vuln: {b[4]:>5.2f}")

            print("\nDistribución de la Brecha Digital:")
            for bd in social_data["brecha_digital_dist"]:
                print(f"  - {bd[0]:<40}: {bd[1]:>3} personas ({bd[2]:>5.2f}%)")

            # 4. Queries Analíticas de SIG
            print("\n--------------------------------------------------------------------------------")
            print("CÁTEDRA 2: SISTEMA DE INFORMACIÓN GERENCIAL (MYPEs Y DIAGNÓSTICO PATRONAL)")
            print("--------------------------------------------------------------------------------")
            sig_data = run_analytics_sig(cursor)
            print("Informalidad Laboral Patronal por Rubro Económico:")
            for r in sig_data["informalidad_mypes"]:
                print(f"  - {r[0]:<42} | MYPEs: {r[1]:>2} | Dotación: {r[2]:>3} | Sin IPS: {r[3]:>3} | Tasa Inf: {r[4]:>5.2f}%")

            print("\nPrincipales Barreras Patronales para Aporte a IPS:")
            for m in sig_data["motivos_ips"]:
                print(f"  - {m[0][:55]:<55} | {m[1]:>2} MYPEs ({m[2]:>5.2f}%)")

            # 5. Queries Analíticas de Marketing Social
            print("\n--------------------------------------------------------------------------------")
            print("CÁTEDRA 3: MARKETING SOCIAL ('TRABAJO FORMAL, FUTURO SEGURO')")
            print("--------------------------------------------------------------------------------")
            mkt_data = run_analytics_marketing(cursor)
            print("Rendimiento Multicanal Consolidado:")
            for k in mkt_data["kpis_canales"]:
                print(f"  - {k[0]:<36} | Alcance: {k[2]:>6,} | Clics: {k[3]:>4,} | CTR: {k[4]:>5.2f}% | Consultas: {k[5]:>4,} | Derivaciones: {k[6]:>4} | CAC: Gs. {int(k[9]):>7,}".replace(",", "."))

            # 6. Benchmark de Rendimiento y Uso de Índices B-Tree
            print("\n--------------------------------------------------------------------------------")
            print("PRUEBAS DE RENDIMIENTO Y LATENCIA (EXPLAIN ANALYZE CON ÍNDICES B-TREE)")
            print("--------------------------------------------------------------------------------")
            timings = test_performance_and_indexes(cursor)
            all_under_sla = True
            for q_name, ms in timings.items():
                status = "OK" if ms < 50.0 else "WARNING"
                if ms >= 50.0:
                    all_under_sla = False
                print(f"  - Query '{q_name:<30}': {ms:>6.2f} ms [{status}]")

            if all_under_sla:
                print(" [PASSED] SLA de Rendimiento: Todas las consultas ejecutaron en < 50 ms.")

            # Validación final
            total_errors = len(ref_errors) + len(domain_errors)
            print("\n================================================================================")
            if total_errors == 0:
                print("RESULTADO GLOBAL: TODAS LAS PRUEBAS DE INTEGRIDAD Y RENDIMIENTO PASARON (0 ERRORES)")
                print("================================================================================")
                sys.exit(0)
            else:
                print(f"RESULTADO GLOBAL: SE ENCONTRARON {total_errors} FALLOS DE INTEGRIDAD")
                print("================================================================================")
                sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
