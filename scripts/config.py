"""
Configuración general y parámetros del Proyecto Interdisciplinario UNVES 2026.
Investigación: Diagnóstico de la Informalidad Laboral en el Municipio de Villarrica, Guairá.
Cátedras: Sistema de Información Gerencial | Análisis de la Realidad Social | Marketing Social
Facultad de Ciencias Económicas - Universidad Nacional de Villarrica del Espíritu Santo.
"""

from typing import Dict, List, Tuple

# Parámetros Normativos y Salario Mínimo Legal (Vigente desde Julio 2026 en Paraguay)
SALARIO_MINIMO_LEGAL_2026: int = 3044000

# Parámetros Muestrales del Censo de Campo en Villarrica
N_ENCUESTAS_TRABAJADORES: int = 420
N_UNIDADES_PRODUCTIVAS: int = 135

# Período de Relevamiento de Campo ODK / KoboCollect (Horario Permanente UTC-3)
FECHA_INICIO_CAMPO: str = "2026-09-08T08:00:00-03:00"
FECHA_FIN_CAMPO: str = "2026-09-26T18:30:00-03:00"

# Período de Ejecución de la Campaña de Marketing Social "Trabajo Formal, Futuro Seguro" (42 días cerrados)
FECHA_INICIO_CAMPANA: str = "2026-09-01"
FECHA_FIN_CAMPANA: str = "2026-10-12"

# Brigadas de Relevamiento Estudiantil y Terminales KoboCollect Autorizadas (Android IMEI/Collect IDs)
BRIGADAS_UNVES: List[Dict[str, str]] = [
    {"usuario": "unves_brigada_01", "deviceid": "collect:358921098471923", "zona": "Centro"},
    {"usuario": "unves_brigada_02", "deviceid": "collect:354719283749102", "zona": "Ybaroty"},
    {"usuario": "unves_brigada_03", "deviceid": "collect:864719283019284", "zona": "San Miguel"},
    {"usuario": "unves_brigada_04", "deviceid": "collect:359182736451928", "zona": "Santa Librada"},
    {"usuario": "unves_brigada_05", "deviceid": "collect:865192837401928", "zona": "Estación / Lomas Valentinas"},
    {"usuario": "unves_brigada_06", "deviceid": "collect:351928374619283", "zona": "Tuyutimí"}
]

# Delimitación Geográfica de los 7 Barrios Relevados en Villarrica (Guairá, Paraguay)
BARRIOS_VILLARRICA: Dict[str, Dict] = {
    "Centro": {
        "lat_range": (-25.7560, -25.7500),
        "lon_range": (-56.4510, -56.4450),
        "alt_range": (140.0, 148.0),
        "peso_muestral": 0.22,
        "descripcion": "Zona comercial céntrica, comercios minoristas, trámites y servicios"
    },
    "Ybaroty": {
        "lat_range": (-25.7530, -25.7470),
        "lon_range": (-56.4600, -56.4540),
        "alt_range": (135.0, 144.0),
        "peso_muestral": 0.18,
        "descripcion": "Barrio tradicional histórico, talleres artesanales y negocios familiares"
    },
    "San Miguel": {
        "lat_range": (-25.7450, -25.7380),
        "lon_range": (-56.4450, -56.4380),
        "alt_range": (132.0, 140.0),
        "peso_muestral": 0.16,
        "descripcion": "Zona residencial y mixta, talleres mecánicos y despensas"
    },
    "Santa Librada": {
        "lat_range": (-25.7660, -25.7600),
        "lon_range": (-56.4550, -56.4470),
        "alt_range": (138.0, 146.0),
        "peso_muestral": 0.15,
        "descripcion": "Zona densa con puestos de comida, confección y transporte local"
    },
    "Estación": {
        "lat_range": (-25.7680, -25.7610),
        "lon_range": (-56.4410, -56.4330),
        "alt_range": (130.0, 139.0),
        "peso_muestral": 0.13,
        "descripcion": "Entorno del Parque M. Ortiz Guerrero y antigua estación, oficios diversos"
    },
    "Lomas Valentinas": {
        "lat_range": (-25.7510, -25.7450),
        "lon_range": (-56.4370, -56.4310),
        "alt_range": (142.0, 152.0),
        "peso_muestral": 0.09,
        "descripcion": "Zona este de la ciudad, comercio barrial y servicios independientes"
    },
    "Tuyutimí": {
        "lat_range": (-25.7750, -25.7680),
        "lon_range": (-56.4650, -56.4570),
        "alt_range": (128.0, 137.0),
        "peso_muestral": 0.07,
        "descripcion": "Sector periurbano suroeste, oficios de construcción y reciclaje"
    }
}

# Catálogo Oficial de Oficios Informales Relevados en Villarrica
OFICIOS_LOCALES: List[Dict[str, str]] = [
    {"oficio": "Confección y bordado artesanal (Prendas de vestir)", "sector": "Manufactura Textil"},
    {"oficio": "Comercio al paso / Copetín / Venta de alimentos", "sector": "Gastronomía Callejera"},
    {"oficio": "Construcción / Albañilería / Pintura", "sector": "Construcción y Mantenimiento"},
    {"oficio": "Mototaxi / Reparto y delivery en motocicleta", "sector": "Transporte y Logística"},
    {"oficio": "Taller mecánico menor / Gomería / Chapa y pintura", "sector": "Servicios Técnicos"},
    {"oficio": "Venta ambulante / Feria municipal / Mercaderías", "sector": "Comercio Ambulante"},
    {"oficio": "Servicios domésticos y limpieza informal", "sector": "Servicios Personales"},
    {"oficio": "Carpintería / Herrería / Mantenimiento general", "sector": "Oficios Técnicos"},
    {"oficio": "Zapatería y reparación de calzado / Marroquinería", "sector": "Artesanías y Reparación"}
]

# Niveles Educativos Observados en el Relevamiento Sociodemográfico
NIVELES_EDUCATIVOS: List[str] = [
    "Primaria incompleta",
    "Primaria completa",
    "Secundaria incompleta",
    "Secundaria completa (Bachiller)",
    "Terciario / Universitario incompleto"
]

# Medios de Pago y Cobro Registrados en el Censo de Villarrica
MEDIOS_PAGO_OPCIONES: List[str] = [
    "efectivo",
    "tigo_money",
    "billetera_zimple",
    "sipap_transferencia",
    "qr_bancario"
]

# Rubros Económicos de Micro y Pequeñas Empresas (MYPEs) Censadas
RUBROS_UNIDADES_PRODUCTIVAS: List[Dict[str, str]] = [
    {"rubro": "Comercio minorista y despensa de barrio", "sector": "Comercio"},
    {"rubro": "Confección textil y talleres artesanales", "sector": "Manufactura"},
    {"rubro": "Gastronomía, copetines y rotiserías", "sector": "Gastronomía"},
    {"rubro": "Servicios técnicos, talleres y gomerías", "sector": "Servicios"},
    {"rubro": "Transporte de cargas livianas y fletes", "sector": "Logística y Transporte"}
]
