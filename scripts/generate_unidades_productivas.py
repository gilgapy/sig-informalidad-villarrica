"""
Generador del dataset de Unidades Productivas y Microempresas de Villarrica (UNVES 2026).
Produce data/processed/unidades_productivas.csv reflejando el tejido económico real de 135 MYPEs
con 396 trabajadores dependientes, 51.1% sin RUC y 17.8% operando exclusivamente en efectivo.
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

BARRIOS = {
    "Centro": {"lat": (-25.7560, -25.7500), "lon": (-56.4510, -56.4450), "n_mypes": 32},
    "Santa Librada": {"lat": (-25.7660, -25.7600), "lon": (-56.4550, -56.4470), "n_mypes": 24},
    "Ybaroty": {"lat": (-25.7530, -25.7470), "lon": (-56.4600, -56.4540), "n_mypes": 22},
    "San Miguel": {"lat": (-25.7450, -25.7380), "lon": (-56.4450, -56.4380), "n_mypes": 21},
    "Estación": {"lat": (-25.7680, -25.7610), "lon": (-56.4410, -56.4330), "n_mypes": 16},
    "Tuyutimí": {"lat": (-25.7750, -25.7680), "lon": (-56.4650, -56.4570), "n_mypes": 11},
    "Lomas Valentinas": {"lat": (-25.7510, -25.7450), "lon": (-56.4370, -56.4310), "n_mypes": 9}
}

def generar_dataset_unidades(output_path: str = "data/processed/unidades_productivas.csv") -> List[Dict[str, Any]]:
    rng = np.random.default_rng(20261016)
    
    # 135 MYPEs que totalizan exactamente 396 trabajadores dependientes
    trab_dist = [1]*18 + [2]*40 + [3]*45 + [4]*20 + [5]*8 + [6]*4
    for i in range(19):
        trab_dist[i + 18] += 1
    assert sum(trab_dist) == 396
    assert len(trab_dist) == 135
    rng.shuffle(trab_dist)
    
    # 51.1% Sin RUC (69), 38.5% RESIMPLE (52), 10.4% Régimen General (14)
    estados_ruc = ["Sin RUC (Totalmente informal)"] * 69 + ["Inscripto en RESIMPLE (DNIT)"] * 52 + ["Régimen General (IVA/IRP)"] * 14
    rng.shuffle(estados_ruc)
    
    # 17.8% Efectivo exclusivo (24 MYPEs)
    es_efectivo_solo = [True] * 24 + [False] * 111
    rng.shuffle(es_efectivo_solo)
    
    # Motivo patronal más frecuente: 23% desconocimiento normativo
    motivos_pat = ["Desconocimiento de los trámites y exigencias de inscripción"] * 31 + \
                  ["Costo de aporte mensual no sostenible con la facturación actual"] * 30 + \
                  ["Personal contratado por jornada transitoria o destajo"] * 27 + \
                  ["Los propios trabajadores prefieren cobrar el jornal íntegro sin retención"] * 24 + \
                  ["Burocracia y excesivos requisitos documentales exigidos"] * 23
    rng.shuffle(motivos_pat)
    
    rubros_pool = ["Comercio minorista y despensa de barrio"] * 43 + \
                  ["Confección textil y talleres de Ao Po'i"] * 30 + \
                  ["Gastronomía, copetines y rotiserías"] * 27 + \
                  ["Servicios técnicos, talleres y gomerías"] * 22 + \
                  ["Transporte de cargas livianas y fletes"] * 13
    assert len(rubros_pool) == 135
    rng.shuffle(rubros_pool)
    
    mypes_list = []
    mype_idx = 1
    mype_ptr = 0
    
    for b_nombre, b_info in BARRIOS.items():
        for _ in range(b_info["n_mypes"]):
            m_id = f"MYPE-VIL-{mype_idx:03d}"
            lat = round(float(rng.uniform(b_info["lat"][0], b_info["lat"][1])), 6)
            lon = round(float(rng.uniform(b_info["lon"][0], b_info["lon"][1])), 6)
            rubro = rubros_pool[mype_ptr]
            tot_t = trab_dist[mype_ptr]
            ruc = estados_ruc[mype_ptr]
            mot_p = motivos_pat[mype_ptr]
            ef_solo = es_efectivo_solo[mype_ptr]
            
            # Informalidad patronal por rubro
            if rubro == "Servicios técnicos, talleres y gomerías":
                con_ips = 1 if (rng.random() < 0.04 and tot_t > 1) else 0
            elif rubro == "Confección textil y talleres de Ao Po'i":
                con_ips = 1 if (rng.random() < 0.08 and tot_t > 1) else 0
            elif rubro == "Gastronomía, copetines y rotiserías":
                con_ips = 1 if (rng.random() < 0.12 and tot_t > 1) else 0
            else:
                con_ips = 1 if (rng.random() < 0.08 and tot_t > 1) else 0
            sin_ips = tot_t - con_ips
            tasa_inf = round((sin_ips / tot_t) * 100.0, 2)
            
            if ef_solo:
                medios = ["efectivo"]
            else:
                medios = ["efectivo"]
                if rng.random() < 0.70: medios.append("tigo_money")
                if rng.random() < 0.42: medios.append("qr_bancario")
                if rng.random() < 0.28: medios.append("sipap_transferencia")
                
            ingreso_est = int(rng.uniform(8500000, 26000000))
            disp = rng.choice(["Muy interesado", "Interesado", "Poco interesado", "No interesado"], p=[0.30, 0.42, 0.18, 0.10])
            
            mypes_list.append({
                "id_unidad": m_id,
                "nombre_establecimiento": f"Taller / Local {b_nombre} #{mype_idx}",
                "barrio": b_nombre,
                "latitud": lat,
                "longitud": lon,
                "rubro_actividad": rubro,
                "antiguedad_anios": int(rng.integers(1, 20)),
                "total_trabajadores": tot_t,
                "trabajadores_sin_ips": sin_ips,
                "trabajadores_con_ips": con_ips,
                "tasa_informalidad_laboral_pct": tasa_inf,
                "estado_tributario_ruc": ruc,
                "motivo_no_aporte_ips": mot_p,
                "ingreso_mensual_estimado_pyg": ingreso_est,
                "disposicion_formalizar": disp,
                "medios_pago": medios
            })
            mype_idx += 1
            mype_ptr += 1
            
    out_file = Path(output_path)
    if not out_file.is_absolute():
        out_file = BASE_DIR / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id_unidad", "nombre_establecimiento", "barrio", "latitud", "longitud",
            "rubro_actividad", "antiguedad_anios", "total_trabajadores", "trabajadores_sin_ips",
            "trabajadores_con_ips", "tasa_informalidad_laboral_pct", "estado_tributario_ruc",
            "motivo_no_aporte_ips", "ingreso_mensual_estimado_pyg", "disposicion_formalizar", "medios_pago"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in mypes_list:
            row = dict(m)
            row["medios_pago"] = ";".join(m["medios_pago"])
            writer.writerow(row)
            
    print(f"✔ Dataset de Unidades Productivas generado en: {out_file} (135 MYPEs, {sum(m['total_trabajadores'] for m in mypes_list)} trabajadores)")
    return mypes_list

if __name__ == "__main__":
    generar_dataset_unidades()
