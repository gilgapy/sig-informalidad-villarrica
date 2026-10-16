"""
Módulo de Ingesta y Validación de Datos Primarios de Campo (UNVES 2026).
Cátedras: Sistema de Información Gerencial | Realidad Social | Marketing Social
Procesa la exportación oficial de KoboToolbox / ODK y valida la integridad de los datasets de campo.
"""

import csv
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

from config import (
    SALARIO_MINIMO_LEGAL_2026,
    N_ENCUESTAS_TRABAJADORES,
    N_UNIDADES_PRODUCTIVAS,
    BARRIOS_VILLARRICA
)
from process_trabajadores import procesar_trabajadores

logger = logging.getLogger("unves.import")

def importar_y_procesar_datos_campo(
    raw_path: str = "data/raw/encuesta_informalidad_kobo_export.csv",
    proc_trabajadores_path: str = "data/processed/trabajadores_informales.csv",
    proc_unidades_path: str = "data/processed/unidades_productivas.csv",
    proc_marketing_path: str = "data/processed/marketing_campana_metricas.csv"
) -> bool:
    """
    Ingesta los datos primarios recolectados en campo mediante KoboCollect / ODK
    y genera los datasets procesados con indicadores sociales normalizados.
    """
    print(f"-> Ingestando exportación oficial de campo: {raw_path}")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"No se encontró el archivo de exportación de campo: {raw_path}")

    # 1. Validar integridad de la exportación KoboToolbox
    df_raw = pd.read_csv(raw_path)
    if len(df_raw) != N_ENCUESTAS_TRABAJADORES:
        raise ValueError(f"Se esperaban {N_ENCUESTAS_TRABAJADORES} registros de campo, se hallaron {len(df_raw)}")
    print(f"   ✔ Exportación KoboToolbox validada: {len(df_raw)} encuestas individuales.")

    # 2. Procesar los 10 indicadores sociales de los trabajadores
    print(f"-> Computando indicadores de vulnerabilidad y procesando trabajadores...")
    n_proc_trab = procesar_trabajadores(raw_path, proc_trabajadores_path)
    print(f"   ✔ Dataset de trabajadores consolidado: {n_proc_trab} registros en {proc_trabajadores_path}")

    # 3. Validar unidades productivas
    if not os.path.exists(proc_unidades_path):
        raise FileNotFoundError(f"No se encontró el censo de unidades productivas: {proc_unidades_path}")
    df_unidades = pd.read_csv(proc_unidades_path)
    if len(df_unidades) != N_UNIDADES_PRODUCTIVAS:
        raise ValueError(f"Se esperaban {N_UNIDADES_PRODUCTIVAS} MYPEs censadas, se hallaron {len(df_unidades)}")
    print(f"   ✔ Censo de unidades productivas verificado: {len(df_unidades)} MYPEs en {proc_unidades_path}")

    # 4. Validar métricas de campaña de marketing social
    if not os.path.exists(proc_marketing_path):
        raise FileNotFoundError(f"No se encontró el registro de marketing social: {proc_marketing_path}")
    df_mkt = pd.read_csv(proc_marketing_path)
    print(f"   ✔ Métricas de campaña de marketing social verificadas: {len(df_mkt)} registros diarios.")

    return True

if __name__ == "__main__":
    importar_y_procesar_datos_campo()
