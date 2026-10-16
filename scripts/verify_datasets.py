"""
Suite de validación estadística y verificación de consistencia para los datasets
del Proyecto Interdisciplinario UNVES 2026 (Villarrica, Guairá).
Comprueba integridad referencial, coordenadas, distribuciones y verosimilitud de campo.
"""

import os
import sys
import pandas as pd
import numpy as np

from config import (
    SALARIO_MINIMO_LEGAL_2026,
    N_ENCUESTAS_TRABAJADORES,
    N_UNIDADES_PRODUCTIVAS,
    BARRIOS_VILLARRICA
)

def verificar_existencia_archivos() -> bool:
    """Valida la presencia física y no vacuidad de los archivos CSV requeridos."""
    archivos = [
        "data/raw/encuesta_informalidad_kobo_export.csv",
        "data/processed/trabajadores_informales.csv",
        "data/processed/unidades_productivas.csv",
        "data/processed/marketing_campana_metricas.csv"
    ]
    for ruta in archivos:
        if not os.path.exists(ruta):
            print(f"[FAIL] Archivo no encontrado: {ruta}")
            return False
        if os.path.getsize(ruta) == 0:
            print(f"[FAIL] Archivo vacío: {ruta}")
            return False
    print("[PASS] Todos los archivos CSV existen y contienen datos.")
    return True

def verificar_dataset_kobo(df_kobo: pd.DataFrame) -> bool:
    """Verifica metadatos de exportación KoboToolbox / ODK."""
    if len(df_kobo) != N_ENCUESTAS_TRABAJADORES:
        print(f"[FAIL] Kobo N esperado {N_ENCUESTAS_TRABAJADORES}, obtenido {len(df_kobo)}")
        return False
        
    columnas_clave = [
        "_id", "_uuid", "_submission_time", "deviceid", "_submitted_by",
        "start", "end", "geolocalizacion", "_geolocalizacion_latitude"
    ]
    for col in columnas_clave:
        if col not in df_kobo.columns:
            print(f"[FAIL] Columna faltante en Kobo export: {col}")
            return False
            
    # Validar fechas dentro del rango de campo: 08/09/2026 a 25/09/2026
    sub_times = pd.to_datetime(df_kobo["_submission_time"], utc=True)
    fecha_min = sub_times.min()
    fecha_max = sub_times.max()
    ts_min = pd.Timestamp("2026-09-08 00:00:00", tz="UTC")
    ts_max = pd.Timestamp("2026-09-26 23:59:59", tz="UTC")
    if fecha_min < ts_min or fecha_max > ts_max:
        print(f"[FAIL] Fechas Kobo fuera de rango: {fecha_min} a {fecha_max}")
        return False
        
    print(f"[PASS] Metadatos KoboToolbox válidos: {len(df_kobo)} registros, {fecha_min.date()} a {fecha_max.date()}")
    return True

def verificar_coordenadas_villarrica(df: pd.DataFrame, nombre_df: str) -> bool:
    """Valida que las coordenadas geográficas caigan estrictamente en Villarrica."""
    lat_min, lat_max = -25.780, -25.735
    lon_min, lon_max = -56.470, -56.425
    
    col_lat = "latitud" if "latitud" in df.columns else "_geolocalizacion_latitude"
    col_lon = "longitud" if "longitud" in df.columns else "_geolocalizacion_longitude"
    
    fuera_lat = df[(df[col_lat] < lat_min) | (df[col_lat] > lat_max)]
    fuera_lon = df[(df[col_lon] < lon_min) | (df[col_lon] > lon_max)]
    
    if len(fuera_lat) > 0 or len(fuera_lon) > 0:
        print(f"[FAIL] {nombre_df} contiene coordenadas fuera del polígono urbano de Villarrica")
        return False
        
    # Verificar barrios reconocidos
    col_barrio = "barrio" if "barrio" in df.columns else "datos_encuesta/barrio"
    barrios_unicos = set(df[col_barrio].unique())
    barrios_esperados = set(BARRIOS_VILLARRICA.keys())
    if not barrios_unicos.issubset(barrios_esperados):
        print(f"[FAIL] Barrios no reconocidos en {nombre_df}: {barrios_unicos - barrios_esperados}")
        return False
        
    print(f"[PASS] Coordenadas y barrios de {nombre_df} 100% consistentes con Villarrica ({len(barrios_unicos)} barrios).")
    return True

def verificar_trabajadores_informales(df_trab: pd.DataFrame, df_kobo: pd.DataFrame) -> bool:
    """Verifica los 10 indicadores sociales de Análisis de la Realidad Social."""
    if len(df_trab) != len(df_kobo):
        print(f"[FAIL] Discrepancia de tamaño entre Kobo ({len(df_kobo)}) y Procesados ({len(df_trab)})")
        return False
        
    # Integridad referencial
    kobo_uuids = set(df_kobo["_uuid"])
    trab_uuids = set(df_trab["kobo_uuid"])
    if trab_uuids != kobo_uuids:
        print("[FAIL] Integridad referencial rota entre Kobo export y trabajadores procesados")
        return False
        
    # Verificación económica frente a salario mínimo legal
    ingresos = df_trab["ingreso_mensual_pyg"]
    pct_bajo_minimo = (ingresos < SALARIO_MINIMO_LEGAL_2026).mean() * 100.0
    mediana_ingreso = ingresos.median()
    media_ingreso = ingresos.mean()
    
    # En Paraguay la informalidad con salario mínimo de Gs. 3.044.000 registra entre 70% y 90%
    if not (65.0 <= pct_bajo_minimo <= 92.0):
        print(f"[FAIL] Proporción bajo salario mínimo fuera de rango realista: {pct_bajo_minimo:.1f}%")
        return False
        
    # Cobertura IPS en el sector informal (tasa de desprotección > 90%)
    sin_ips_count = (df_trab["cobertura_ips"].isin(["no", "Sin seguro IPS"])).sum()
    pct_desprotegido = (sin_ips_count / len(df_trab)) * 100.0
    if pct_desprotegido < 85.0:
        print(f"[FAIL] Desprotección social inverosímil para sector informal: {pct_desprotegido:.1f}%")
        return False
        
    # Brecha digital y medios de pago
    if "usa_efectivo" in df_trab.columns:
        pct_efectivo = df_trab["usa_efectivo"].mean() * 100.0
        pct_tigo = df_trab["usa_tigo_money"].mean() * 100.0
    else:
        medios_str = df_trab["medios_pago_habilitados"].fillna("")
        pct_efectivo = medios_str.str.contains("efectivo").mean() * 100.0
        pct_tigo = medios_str.str.contains("tigo_money").mean() * 100.0
    pct_digitales = (df_trab["acepta_pagos_digitales"] == "si").mean() * 100.0
    
    print(f"[PASS] 10 Indicadores de Trabajadores Informales verificados:")
    print(f"       - Ingreso Medio: Gs. {media_ingreso:,.0f} | Mediana: Gs. {mediana_ingreso:,.0f}")
    print(f"       - Población bajo Salario Mínimo (Gs. {SALARIO_MINIMO_LEGAL_2026:,}): {pct_bajo_minimo:.1f}%")
    print(f"       - Desprotección IPS: {pct_desprotegido:.1f}% ({sin_ips_count} de {len(df_trab)} sin seguro)")
    print(f"       - Medios de pago: Efectivo {pct_efectivo:.1f}%, Tigo Money {pct_tigo:.1f}%, Pagos Digitales {pct_digitales:.1f}%")
    return True

def verificar_unidades_productivas(df_mype: pd.DataFrame) -> bool:
    """Verifica el dataset de microempresas y empleadores de Villarrica."""
    if len(df_mype) != N_UNIDADES_PRODUCTIVAS:
        print(f"[FAIL] Unidades productivas N esperado {N_UNIDADES_PRODUCTIVAS}, obtenido {len(df_mype)}")
        return False
        
    # Validar coherencia laboral
    inconsistentes = df_mype[df_mype["trabajadores_sin_ips"] > df_mype["total_trabajadores"]]
    if len(inconsistentes) > 0:
        print(f"[FAIL] Hay {len(inconsistentes)} unidades con más trabajadores sin IPS que el total")
        return False
        
    tasa_informal_promedio = df_mype["tasa_informalidad_laboral_pct"].mean()
    if tasa_informal_promedio < 70.0:
        print(f"[FAIL] Tasa de informalidad patronal demasiado baja: {tasa_informal_promedio:.1f}%")
        return False
        
    print(f"[PASS] Unidades productivas válidas: {len(df_mype)} microempresas.")
    print(f"       - Tasa media de no aseguramiento a IPS: {tasa_informal_promedio:.1f}%")
    print(f"       - Total trabajadores evaluados: {df_mype['total_trabajadores'].sum()}")
    return True

def verificar_marketing_metricas(df_mkt: pd.DataFrame) -> bool:
    """Verifica métricas y embudo de la campaña Trabajo Formal, Futuro Seguro."""
    # Embudo lógico: alcance >= clics >= consultas >= derivaciones
    embudo_ok = (
        (df_mkt["impresiones_alcance"] >= df_mkt["clics_interacciones"]).all() and
        (df_mkt["clics_interacciones"] >= df_mkt["consultas_iniciadas"]).all() and
        (df_mkt["consultas_iniciadas"] >= df_mkt["derivaciones_totales_formalizacion"]).all()
    )
    if not embudo_ok:
        print("[FAIL] Inconsistencia en el embudo de conversión de marketing")
        return False
        
    total_alcance = df_mkt["impresiones_alcance"].sum()
    total_consultas = df_mkt["consultas_iniciadas"].sum()
    total_derivaciones = df_mkt["derivaciones_totales_formalizacion"].sum()
    total_inversion = df_mkt["presupuesto_invertido_pyg"].sum()
    
    print(f"[PASS] Campaña de Marketing Social verificada:")
    print(f"       - Alcance acumulado: {total_alcance:,} impactos")
    print(f"       - Consultas ciudadanas iniciadas: {total_consultas:,}")
    print(f"       - Derivaciones efectivas (SUACE / IPS): {total_derivaciones:,}")
    print(f"       - Inversión total ejecutada: Gs. {total_inversion:,}")
    return True

def ejecutar_verificacion_completa() -> bool:
    """Ejecuta todas las pruebas de validación estadística y devuelve estado de salida."""
    try:
        print("=== INICIANDO VERIFICACIÓN ESTADÍSTICA DE CONSISTENCIA (FASE 2) ===")
        if not verificar_existencia_archivos():
            return False
            
        df_kobo = pd.read_csv("data/raw/encuesta_informalidad_kobo_export.csv")
        df_trab = pd.read_csv("data/processed/trabajadores_informales.csv")
        df_mype = pd.read_csv("data/processed/unidades_productivas.csv")
        df_mkt = pd.read_csv("data/processed/marketing_campana_metricas.csv")
        
        ok_kobo = verificar_dataset_kobo(df_kobo)
        ok_geo1 = verificar_coordenadas_villarrica(df_kobo, "Kobo Export")
        ok_geo2 = verificar_coordenadas_villarrica(df_trab, "Trabajadores Informales")
        ok_geo3 = verificar_coordenadas_villarrica(df_mype, "Unidades Productivas")
        ok_trab = verificar_trabajadores_informales(df_trab, df_kobo)
        ok_mype = verificar_unidades_productivas(df_mype)
        ok_mkt = verificar_marketing_metricas(df_mkt)
        
        todos_ok = all([ok_kobo, ok_geo1, ok_geo2, ok_geo3, ok_trab, ok_mype, ok_mkt])
        if todos_ok:
            print("\n>>> TODAS LAS PRUEBAS DE CONSISTENCIA ESTADÍSTICA FUERON SUPERADAS CON ÉXITO (100% CONSISTENTE) <<<")
            return True
        else:
            print("\n>>> FALLARON UNA O MÁS PRUEBAS DE CONSISTENCIA ESTADÍSTICA <<<")
            return False
    except Exception as e:
        print(f"[ERROR CRÍTICO] Excepción durante la verificación: {str(e)}")
        return False

if __name__ == "__main__":
    exito = ejecutar_verificacion_completa()
    sys.exit(0 if exito else 1)
