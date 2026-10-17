# Diccionario de Datos del Proyecto Interdisciplinario UNVES 2026
**Cátedras Intervinientes:** Sistema de Información Gerencial | Análisis de la Realidad Social del Paraguay | Marketing Social  
**Ubicación:** Villarrica, Departamento del Guairá, Paraguay  
**Año Lectivo:** 2026 (8° Semestre - Lic. en Administración de Empresas)

---

## 1. Exportación Cruda de Campo: `data/raw/encuesta_informalidad_kobo_export.csv`
- **Origen:** Plataforma KoboToolbox / Open Data Kit (ODK Collect v2026.x).
- **Período de Levantamiento:** 08/09/2026 al 25/09/2026.
- **Tamaño Muestral:** 420 observaciones individuales.
- **Brigadas de Campo:** 6 brigadas estudiantiles UNVES (`unves_brigada_01` a `06`).

| Campo ODK / Kobo | Tipo de Dato | Descripción y Valores Permitidos |
| :--- | :--- | :--- |
| `_id` | Integer | Identificador secuencial interno generado por el servidor KoboToolbox. |
| `_uuid` | UUID | Identificador universal único de la instancia de formulario móvil. |
| `_submission_time` | Timestamp ISO 8601 | Fecha y hora UTC-04:00 de sincronización al servidor. |
| `_validation_status` | String | Estado de control de calidad institucional en Kobo. |
| `_status` | String | Modo de envío (`submitted_via_odk`). |
| `_submitted_by` | String | Cuenta de usuario de la brigada asignada en terreno. |
| `deviceid` | String | Identificador de hardware del smartphone ODK (`collect:...`). |
| `start` / `end` | Timestamp | Tiempos de inicio y cierre de la entrevista presencial. |
| `today` | Date | Fecha calendario de la jornada de recolección (YYYY-MM-DD). |
| `consentimiento_informado` | Text (select_one) | Aceptación del protocolo ético y estadístico (`si`). |
| `datos_encuesta/barrio` | Text (select_one) | Barrio urbano de Villarrica: `Centro`, `Ybaroty`, `San Miguel`, `Santa Librada`, `Estación`, `Lomas Valentinas`, `Tuyutimí`. |
| `datos_encuesta/edad` | Integer | Edad del trabajador en años cumplidos (18 a 68). |
| `datos_encuesta/genero` | Text (select_one) | Género (`masculino`, `femenino`). |
| `datos_encuesta/nivel_educativo` | Text (select_one) | Nivel formal alcanzado (desde `Primaria incompleta` hasta `Universitario incompleto`). |
| `datos_encuesta/actividad_economica` | Text (select_one) | Oficio informal desempeñado en Villarrica. |
| `datos_encuesta/ingreso_mensual_estimado_pyg` | Integer | Estimación de ingreso neto mensual en Guaraníes (PYG). |
| `datos_encuesta/horas_semanales_trabajadas` | Integer | Carga horaria habitual dedicada al oficio por semana. |
| `datos_encuesta/cobertura_ips` | Text (select_one) | Tenencia de seguro médico/jubilatorio en IPS (`no`). |
| `datos_encuesta/motivo_no_ips` | Text (select_one) | Causa declarada de no aseguramiento social. |
| `datos_encuesta/posee_smartphone` | Text (select_one) | Tenencia personal de teléfono inteligente (`si`, `no`). |
| `datos_encuesta/tipo_acceso_internet` | Text (select_one) | Conectividad habitual (`datos_moviles_prepago`, `wifi_hogar_y_movil`, `sin_acceso_propio`). |
| `datos_encuesta/medios_pago_cobro` | Text (select_multiple) | Cadena de opciones seleccionadas separadas por espacio. |
| `datos_encuesta/medios_pago_cobro/*` | Binary (0 / 1) | Dummies desglosadas para `efectivo`, `tigo_money`, `billetera_zimple`, `sipap_transferencia`, `qr_bancario`. |
| `datos_encuesta/conoce_resimple` | Text (select_one) | Conocimiento del régimen tributario RESIMPLE de la DNIT (`si`, `no`). |
| `datos_encuesta/interes_capacitacion_formalizacion`| Text (select_one) | Actitud hacia programas de formalización. |
| `datos_encuesta/personas_a_cargo` | Integer | Carga de dependencia económica familiar directa. |
| `datos_encuesta/tenencia_vivienda` | Text (select_one) | Régimen habitacional (`propia`, `alquilada`, `prestada_familiar`). |
| `geolocalizacion` | Geopoint | Cadena estándar ODK: `latitud longitud altitud precision`. |
| `_geolocalizacion_latitude` | Float | Latitud geográfica WGS84 (-25.7962 a -25.7673). |
| `_geolocalizacion_longitude` | Float | Longitud geográfica WGS84 (-56.4630 a -56.4353). |
| `_geolocalizacion_altitude` | Float | Elevación sobre el nivel del mar en metros (128m a 152m). |
| `_geolocalizacion_precision` | Float | Margen de error GPS en metros (3.2m a 9.8m). |

---

## 2. Dataset Analítico de Trabajadores: `data/processed/trabajadores_informales.csv`
- **Articulación:** Cátedra de *Análisis de la Realidad Social del Paraguay*.
- **Contenido:** 10 indicadores sociales estandarizados para análisis econométrico y tableros BI.

| Variable | Tipo | Descripción Metodológica / Criterio Social |
| :--- | :--- | :--- |
| `id_trabajador` | String (PK) | Código unívoco del trabajador (`TRAB-0001` a `TRAB-0420`). |
| `kobo_uuid` | UUID (FK) | Enlace de trazabilidad con la boleta de campo en KoboToolbox. |
| `fecha_recoleccion` | Date | Fecha de captura en terreno. |
| `barrio` | String | Barrio de Villarrica donde desempeña su actividad. |
| `latitud` / `longitud` | Float | Coordenadas decimales para georreferenciación GIS. |
| `edad` | Integer | Edad en años. |
| `genero` | String | Género. |
| `nivel_educativo` | String | Nivel educativo máximo reportado. |
| `anios_estudio` | Integer | Estimación cuantitativa de años de escolarización formal. |
| `oficio_rubro` | String | Clasificación del oficio local en Villarrica. |
| `antiguedad_oficio_anios`| Integer | Trayectoria laboral acumulada en el sector informal. |
| `ingreso_mensual_pyg` | Integer | Ingreso percibido mensual promedio en Guaraníes. |
| `salario_minimo_referencia_pyg` | Integer | Parámetro legal de referencia en Paraguay (Gs. 3.044.000). |
| `brecha_salario_pyg` | Integer | Diferencial absoluto: `ingreso_mensual_pyg - 3.044.000`. |
| `situacion_respecto_minimo` | String | Condición: `Inferior al mínimo` o `Igual o superior al mínimo`. |
| `horas_semanales` | Integer | Horas de labor semanales. |
| `condicion_jornada` | String | Subocupación visible (<30h), Típica (30-48h), Sobreocupado (>48h). |
| `cobertura_ips` | String | Estado ante el seguro social (`Sin seguro IPS`). |
| `motivo_no_ips` | String | Causa estructural o de percepción para no aportar a IPS. |
| `posee_smartphone` | String | Posesión de dispositivo inteligente personal (`si`, `no`). |
| `tipo_conectividad` | String | Modalidad de acceso a datos e internet. |
| `brecha_digital` | String | Categoría ordinal: `Brecha Alta`, `Brecha Media`, `Brecha Baja`. |
| `usa_efectivo` | Binary (0/1) | Empleo de moneda física en efectivo. |
| `usa_tigo_money` | Binary (0/1) | Uso de billetera electrónica Tigo Money. |
| `usa_billetera_zimple` | Binary (0/1) | Uso de billetera electrónica Zimple. |
| `usa_sipap` | Binary (0/1) | Uso de transferencias interbancarias inmediatas SIPAP. |
| `usa_qr_bancario` | Binary (0/1) | Cobro mediante códigos QR bancarios. |
| `acepta_pagos_digitales`| String | Capacidad de cobro electrónico (`si`, `no`). |
| `conoce_resimple` | String | Nivel de conocimiento del monotributo simplificado DNIT. |
| `interes_formalizacion`| String | Predisposición a incorporarse a esquemas formales. |
| `personas_a_cargo` | Integer | Número de dependientes en el hogar. |
| `tenencia_vivienda` | String | Seguridad en la tenencia de la vivienda familiar. |
| `indice_vulnerabilidad_social` | Float | Score sintético continuo (10.0 a 98.0) basado en dimensiones socioeconómicas. |

---

## 3. Dataset de Unidades Productivas: `data/processed/unidades_productivas.csv`
- **Articulación:** Cátedra de *Sistema de Información Gerencial*.
- **Tamaño Muestral:** 135 microempresas y talleres de Villarrica.

| Variable | Tipo | Definición |
| :--- | :--- | :--- |
| `id_unidad` | String (PK) | Código único de la unidad (`MYPE-001` a `MYPE-135`). |
| `nombre_establecimiento` | String | Nombre de fantasía comercial verosímil de Villarrica. |
| `barrio` | String | Localización barrial de la unidad económica. |
| `latitud` / `longitud` | Float | Coordenadas geográficas del local / puesto. |
| `rubro_actividad` | String | Rama de actividad económica principal. |
| `antiguedad_anios` | Integer | Tiempo de funcionamiento en el mercado. |
| `total_trabajadores` | Integer | Dotación total de personal (propietario + dependientes). |
| `trabajadores_sin_ips` | Integer | Cantidad de trabajadores sin aseguramiento patronal. |
| `trabajadores_con_ips` | Integer | Cantidad de trabajadores con cobertura IPS formal. |
| `tasa_informalidad_laboral_pct` | Float | Porcentaje de empleo informal interno de la unidad. |
| `estado_tributario_ruc`| String | Estado ante la DNIT (`Sin RUC`, `RESIMPLE`, `RUC General IVA`). |
| `motivo_no_aporte_ips`| String | Principal barrera patronal expresada para no registrar personal. |
| `ingreso_mensual_estimado_pyg` | Integer | Facturación comercial mensual estimada en Guaraníes. |
| `disposicion_formalizar`| String | Nivel de apertura patronal hacia asesorías de formalización. |
| `medios_pago_aceptados`| String | Combinación de medios de cobro habilitados a clientes. |

---

## 4. Dataset de Campaña de Marketing Social: `data/processed/marketing_campana_metricas.csv`
- **Articulación:** Cátedra de *Marketing Social* ("Trabajo Formal, Futuro Seguro").
- **Ventana de Medición:** 10/09/2026 al 21/10/2026 (42 días continuos, 168 observaciones multicanal).

| Variable | Tipo | Definición y Unidad |
| :--- | :--- | :--- |
| `fecha` | Date | Fecha del registro de desempeño (YYYY-MM-DD). |
| `canal` | String | Medio comunicacional (`Meta Ads`, `WhatsApp Business`, `Puntos Presenciales`, `Afiches QR`). |
| `impresiones_alcance` | Integer | Número de personas alcanzadas o impresiones servidas. |
| `clics_interacciones` | Integer | Clics, respuestas, escaneos QR o interacciones activas. |
| `ctr_interaccion_pct` | Float | Tasa de efectividad de interacción (`clics / alcance * 100`). |
| `consultas_iniciadas` | Integer | Consultas ciudadanas efectivas recibidas solicitando información. |
| `consultas_tema_resimple`| Integer | Consultas orientadas al régimen tributario simplificado. |
| `consultas_tema_ips` | Integer | Consultas orientadas a cobertura de salud y jubilación IPS. |
| `derivaciones_suace_villarrica` | Integer | Casos derivados a la ventanilla SUACE regional (formalización de empresas). |
| `derivaciones_ips_regional` | Integer | Casos derivados a la delegación de IPS Villarrica. |
| `derivaciones_totales_formalizacion` | Integer | Total de usuarios vinculados a trámites formales. |
| `presupuesto_invertido_pyg` | Integer | Costo publicitario / operativo incurrido por jornada en Guaraníes. |
| `costo_por_consulta_pyg` | Integer | Eficiencia de inversión (`presupuesto / consultas_iniciadas`). |
