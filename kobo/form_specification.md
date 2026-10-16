# Especificación Técnica de Formulario KoboToolbox / ODK
**Proyecto:** “Transformación Digital y Diagnóstico Social en la Gestión Organizacional: La Informalidad Laboral en el Paraguay”  
**Institución:** Universidad Nacional de Villarrica del Espíritu Santo (UNVES) - Facultad de Ciencias Económicas  
**Form ID:** `encuesta_informalidad_villarrica_2026`  
**Versión:** `vK8m2PqL9n_2026`  

---

## 1. Hoja `survey` (Estructura de Preguntas y Flujos ODK)

| type | name | label (Español) | hint / constraint | appearance |
| :--- | :--- | :--- | :--- | :--- |
| `start` | `start` | Inicio de la entrevista | Automático dispositivo | |
| `end` | `end` | Cierre de la entrevista | Automático dispositivo | |
| `today` | `today` | Fecha de captura | Automático dispositivo | |
| `deviceid` | `deviceid` | Identificador del terminal | Automático dispositivo | |
| `acknowledge` | `consentimiento_informado` | ¿El entrevistado consiente voluntariamente participar en el estudio académico UNVES? | Obligatorio | |
| `geopoint` | `geolocalizacion` | Capture la coordenada GPS exacta del punto de trabajo | Esperar precisión < 10m | placement-map |
| `select_one barrios_list` | `datos_encuesta/barrio` | Seleccione el barrio de Villarrica | Obligatorio | minimal |
| `integer` | `datos_encuesta/edad` | ¿Cuál es su edad en años cumplidos? | `. >= 18 and . <= 85` | |
| `select_one genero_list` | `datos_encuesta/genero` | Género del entrevistado | | horizontal |
| `select_one edu_list` | `datos_encuesta/nivel_educativo` | Máximo nivel educativo formal alcanzado | | |
| `select_one oficios_list`| `datos_encuesta/actividad_economica`| Oficio o rubro de labor principal | | |
| `integer` | `datos_encuesta/antiguedad_oficio_anios`| ¿Cuántos años lleva desempeñando esta actividad? | `. >= 0 and . <= 50` | |
| `integer` | `datos_encuesta/ingreso_mensual_estimado_pyg` | ¿Cuál es su ingreso monetario promedio mensual estimado en Guaraníes? | `. >= 300000 and . <= 15000000` | thousands-sep |
| `integer` | `datos_encuesta/horas_semanales_trabajadas` | ¿Cuántas horas trabaja habitualmente por semana? | `. >= 4 and . <= 98` | |
| `select_one sino_list` | `datos_encuesta/cobertura_ips` | ¿Cuenta actualmente con seguro social o cobertura médica en IPS? | | horizontal |
| `select_one motivos_ips_list`| `datos_encuesta/motivo_no_ips` | ¿Cuál es la principal razón por la que no cuenta con seguro social IPS? | Relevant: `${cobertura_ips} = 'no'` | |
| `select_one sino_list` | `datos_encuesta/posee_smartphone` | ¿Posee usted teléfono celular inteligente (Smartphone)? | | horizontal |
| `select_one conectividad_list`| `datos_encuesta/tipo_acceso_internet`| ¿Cómo se conecta a internet habitualmente? | Relevant: `${posee_smartphone} = 'si'` | |
| `select_multiple pagos_list` | `datos_encuesta/medios_pago_cobro` | ¿Qué medios de pago utiliza o acepta habitualmente para sus cobros? | Múltiple selección permitida | |
| `select_one sino_list` | `datos_encuesta/conoce_resimple` | ¿Conoce el régimen de tributación simplificada RESIMPLE de la DNIT? | | horizontal |
| `select_one interes_list`| `datos_encuesta/interes_capacitacion_formalizacion`| ¿Qué tan interesado estaría en recibir asesoría para formalizar su actividad? | | |
| `integer` | `datos_encuesta/personas_a_cargo` | ¿Cuántas personas dependen económicamente de usted en el hogar? | `. >= 0 and . <= 15` | |
| `select_one vivienda_list`| `datos_encuesta/tenencia_vivienda` | La vivienda donde habita es: | | |

---

## 2. Hoja `choices` (Opciones de Respuesta)

| list_name | name | label |
| :--- | :--- | :--- |
| `barrios_list` | `Centro` | Centro |
| `barrios_list` | `Ybaroty` | Ybaroty |
| `barrios_list` | `San Miguel` | San Miguel |
| `barrios_list` | `Santa Librada` | Santa Librada |
| `barrios_list` | `Estación` | Estación |
| `barrios_list` | `Lomas Valentinas` | Lomas Valentinas |
| `barrios_list` | `Tuyutimí` | Tuyutimí |
| `sino_list` | `si` | Sí |
| `sino_list` | `no` | No |
| `genero_list` | `masculino` | Masculino |
| `genero_list` | `femenino` | Femenino |
| `pagos_list` | `efectivo` | Dinero en efectivo |
| `pagos_list` | `tigo_money` | Billetera electrónica Tigo Money |
| `pagos_list` | `billetera_zimple` | Billetera Personal / Zimple |
| `pagos_list` | `sipap_transferencia` | Transferencia bancaria directa SIPAP |
| `pagos_list` | `qr_bancario` | Cobro con código QR bancario |
