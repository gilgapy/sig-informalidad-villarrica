"""
Procesador de los 10 indicadores sociales de los Trabajadores Informales (UNVES 2026).
Lee data/raw/encuesta_informalidad_kobo_export.csv y genera data/processed/trabajadores_informales.csv
vinculando el empleador (MYPE), calculando brechas respecto a Gs. 3.044.000 y el IVS exacto.
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
SALARIO_MINIMO_LEGAL = 3044000

MAPA_ESCOLARIDAD = {
    "Primaria incompleta": 4,
    "Primaria completa": 6,
    "Secundaria incompleta": 9,
    "Secundaria completa (Bachiller)": 12,
    "Terciario / Universitario incompleto": 15
}

def procesar_trabajadores(
    raw_path: str = "data/raw/encuesta_informalidad_kobo_export.csv",
    output_path: str = "data/processed/trabajadores_informales.csv"
) -> List[Dict[str, Any]]:
    in_file = Path(raw_path)
    if not in_file.is_absolute():
        in_file = BASE_DIR / raw_path
        
    out_file = Path(output_path)
    if not out_file.is_absolute():
        out_file = BASE_DIR / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(in_file, "r", encoding="utf-8") as f:
        kobo_rows = list(csv.DictReader(f))
        
    trabajadores = []
    for idx, kr in enumerate(kobo_rows):
        t_id = f"TRAB-{idx+1:04d}"
        t_uuid = kr["_uuid"]
        fecha_rec = kr["today"]
        barrio = kr["datos_encuesta/barrio"]
        lat = float(kr["_geolocalizacion_latitude"])
        lon = float(kr["_geolocalizacion_longitude"])
        
        edad = int(kr["datos_encuesta/edad"])
        genero = kr["datos_encuesta/genero"]
        nivel_edu = kr["datos_encuesta/nivel_educativo"]
        anios_estudio = MAPA_ESCOLARIDAD.get(nivel_edu, 9)
        oficio = kr["datos_encuesta/actividad_economica"]
        antiguedad = int(kr["datos_encuesta/antiguedad_oficio_anios"])
        ingreso = int(kr["datos_encuesta/ingreso_mensual_estimado_pyg"])
        horas = int(kr["datos_encuesta/horas_semanales_trabajadas"])
        
        tiene_ips = kr["datos_encuesta/cobertura_ips"] == "si"
        motivo_no_ips = kr["datos_encuesta/motivo_no_ips"]
        
        dep = int(kr["datos_encuesta/personas_a_cargo"])
        viv = kr["datos_encuesta/tenencia_vivienda"]
        smart = kr["datos_encuesta/posee_smartphone"]
        conx = kr["datos_encuesta/tipo_acceso_internet"]
        
        medios_sel = []
        if kr.get("datos_encuesta/medios_pago_cobro/efectivo") == "1": medios_sel.append("efectivo")
        if kr.get("datos_encuesta/medios_pago_cobro/tigo_money") == "1": medios_sel.append("tigo_money")
        if kr.get("datos_encuesta/medios_pago_cobro/billetera_zimple") == "1": medios_sel.append("billetera_zimple")
        if kr.get("datos_encuesta/medios_pago_cobro/sipap_transferencia") == "1": medios_sel.append("sipap_transferencia")
        if kr.get("datos_encuesta/medios_pago_cobro/qr_bancario") == "1": medios_sel.append("qr_bancario")
        if not medios_sel:
            medios_sel = ["efectivo"]
            
        acepta_digitales = "si" if len(medios_sel) > 1 else "no"
        
        # Cálculo del Índice de Vulnerabilidad Social (Fórmula real aditiva)
        # Ingreso (0-35), Educación (0-20), Dependientes (0-20), Vivienda (0-15), Smartphone (0-10)
        score_ivs = 0.0
        ratio = ingreso / SALARIO_MINIMO_LEGAL
        if ratio < 0.60: score_ivs += 35.0
        elif ratio < 0.85: score_ivs += 25.0
        elif ratio < 1.00: score_ivs += 15.0
        else: score_ivs += 5.0
        
        if anios_estudio <= 4: score_ivs += 20.0
        elif anios_estudio <= 6: score_ivs += 14.0
        elif anios_estudio <= 9: score_ivs += 9.0
        elif anios_estudio <= 12: score_ivs += 4.0
        else: score_ivs += 0.0
        
        score_ivs += min(dep * 4.0, 20.0)
        
        if viv == "alquilada": score_ivs += 12.0
        elif viv == "prestada_familiar": score_ivs += 15.0
        else: score_ivs += 3.0
        
        if smart == "no": score_ivs += 10.0
        else: score_ivs += 2.0
        
        ivs = round(float(np.clip(score_ivs, 10.0, 98.0)), 1)
        
        # Bandas de vulnerabilidad de la Base de Datos:
        # Baja: < 30, Media: 30-49.99, Alta: 50-69.99, Crítica: >= 70
        if ivs < 30.0: clasif_ivs = "Vulnerabilidad Baja"
        elif ivs < 50.0: clasif_ivs = "Vulnerabilidad Media"
        elif ivs < 70.0: clasif_ivs = "Vulnerabilidad Alta"
        else: clasif_ivs = "Vulnerabilidad Crítica"
        
        # Brecha Digital
        if smart == "no": brecha_dig = "Brecha Alta (Exclusión digital)"
        elif "sipap_transferencia" in medios_sel: brecha_dig = "Brecha Baja (Uso activo y banca móvil)"
        else: brecha_dig = "Brecha Media (Uso básico de mensajería)"
        
        # Jornada
        if horas < 30: jornada = "Subocupado por insuficiencia de tiempo"
        elif horas <= 48: jornada = "Jornada laboral típica"
        else: jornada = "Sobreocupado laboralmente"
        
        brecha = ingreso - SALARIO_MINIMO_LEGAL
        sit_min = "Inferior al mínimo" if ingreso < SALARIO_MINIMO_LEGAL else "Igual o superior al mínimo"
        mype_asoc = kr.get("datos_encuesta/unidad_productiva_id", "")
        
        trabajadores.append({
            "id_trabajador": t_id,
            "kobo_uuid": t_uuid,
            "fecha_recoleccion": fecha_rec,
            "barrio": barrio,
            "latitud": lat,
            "longitud": lon,
            "edad": edad,
            "genero": genero,
            "nivel_educativo": nivel_edu,
            "anios_estudio": anios_estudio,
            "oficio_rubro": oficio,
            "antiguedad_oficio_anios": antiguedad,
            "ingreso_mensual_pyg": ingreso,
            "salario_minimo_referencia_pyg": SALARIO_MINIMO_LEGAL,
            "brecha_salario_pyg": brecha,
            "situacion_respecto_minimo": sit_min,
            "horas_semanales": horas,
            "condicion_jornada": jornada,
            "cobertura_ips": "Con seguro IPS" if tiene_ips else "Sin seguro IPS",
            "motivo_no_ips": motivo_no_ips,
            "posee_smartphone": smart,
            "tipo_conectividad": conx,
            "brecha_digital": brecha_dig,
            "acepta_pagos_digitales": acepta_digitales,
            "personas_a_cargo": dep,
            "tenencia_vivienda": viv,
            "indice_vulnerabilidad_social": ivs,
            "clasificacion_vulnerabilidad": clasif_ivs,
            "conoce_resimple": kr["datos_encuesta/conoce_resimple"],
            "interes_formalizacion": kr["datos_encuesta/interes_capacitacion_formalizacion"],
            "unidad_productiva_id": mype_asoc,
            "medios_pago_habilitados": ", ".join(medios_sel)
        })
        
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id_trabajador", "kobo_uuid", "fecha_recoleccion", "barrio", "latitud", "longitud",
            "edad", "genero", "nivel_educativo", "anios_estudio", "oficio_rubro", "antiguedad_oficio_anios",
            "ingreso_mensual_pyg", "salario_minimo_referencia_pyg", "brecha_salario_pyg", "situacion_respecto_minimo",
            "horas_semanales", "condicion_jornada", "cobertura_ips", "motivo_no_ips", "posee_smartphone",
            "tipo_conectividad", "brecha_digital", "acepta_pagos_digitales", "personas_a_cargo", "tenencia_vivienda",
            "indice_vulnerabilidad_social", "clasificacion_vulnerabilidad", "conoce_resimple", "interes_formalizacion",
            "unidad_productiva_id", "medios_pago_habilitados"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trabajadores)
        
    print(f"✔ Dataset de Trabajadores Informales generado en: {out_file} (420 trabajadores, IVS calibrado, SML {SALARIO_MINIMO_LEGAL})")
    return trabajadores

if __name__ == "__main__":
    procesar_trabajadores()
