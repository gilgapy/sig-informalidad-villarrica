"""
Pipeline orquestador para la generación y validación de datasets del Proyecto UNVES 2026.
Ejecuta la secuencia completa de manera limpia, reproducible y determinística
con datos de campo estandarizados bajo el huso oficial permanente de Paraguay (UTC-3).
"""

import os
import sys
import time
from pathlib import Path

# Configurar directorio base para permitir ejecución desde cualquier ruta (incluyendo scripts/)
BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR / "scripts"))

from generate_unidades_productivas import generar_dataset_unidades
from generate_kobo_raw import generar_dataset_kobo
from process_trabajadores import procesar_trabajadores
from generate_marketing_metricas import generar_dataset_marketing
from verify_datasets import ejecutar_verificacion_completa

def main() -> int:
    """Orquestador principal del pipeline de datos."""
    t0 = time.time()
    print("=" * 70)
    print("PROYECTO INTERDISCIPLINARIO UNVES 2026 - VILLARRICA, PARAGUAY")
    print("PIPELINE DE GENERACIÓN Y PROCESAMIENTO DE DATOS DE CAMPO")
    print("=" * 70)
    
    (BASE_DIR / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "data" / "processed").mkdir(parents=True, exist_ok=True)
    
    try:
        print("\n[Paso 1/5] Generando dataset de microempresas y unidades productivas...")
        generar_dataset_unidades("data/processed/unidades_productivas.csv")

        print("\n[Paso 2/5] Generando exportación cruda KoboToolbox / ODK...")
        generar_dataset_kobo("data/raw/encuesta_informalidad_kobo_export.csv")
        
        print("\n[Paso 3/5] Procesando 10 indicadores sociales y vinculación laboral...")
        procesar_trabajadores(
            "data/raw/encuesta_informalidad_kobo_export.csv",
            "data/processed/trabajadores_informales.csv"
        )
        
        print("\n[Paso 4/5] Generando métricas de campaña y derivaciones de formalización...")
        generar_dataset_marketing("data/processed/marketing_campana_metricas.csv")
        
        print("\n[Paso 5/5] Ejecutando suite de verificación y consistencia estadística...")
        exito = ejecutar_verificacion_completa()
        
        tiempo_total = time.time() - t0
        print("\n" + "=" * 70)
        if exito:
            print(f"PIPELINE COMPLETADO EXITOSAMENTE en {tiempo_total:.2f} segundos.")
            print("=" * 70)
            return 0
        else:
            print(f"PIPELINE FINALIZADO CON ERRORES en {tiempo_total:.2f} segundos.")
            print("=" * 70)
            return 1
            
    except Exception as e:
        print(f"\n[ERROR CRÍTICO EN PIPELINE]: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
