-- ============================================================================
-- PROYECTO INTERDISCIPLINARIO UNVES 2026 - 8° SEMESTRE (4° CURSO)
-- Cátedras: Sistema de Información Gerencial | Análisis de la Realidad Social | Marketing Social
-- Ubicación: Villarrica, Departamento del Guairá, Paraguay
-- Objeto: Esquema Relacional Normalizado en 3FN (Tercera Forma Normal)
-- Motor: PostgreSQL 14+ / Enfoque Robusto, Seguro e Integrado
-- ============================================================================

-- Habilitación de extensiones para UUIDs y funciones criptográficas
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Limpieza controlada e idempotente para inicialización y recreación
DROP VIEW IF EXISTS vw_articulacion_programas_formalizacion CASCADE;
DROP VIEW IF EXISTS vw_marketing_resumen_canales CASCADE;
DROP VIEW IF EXISTS vw_unidades_productivas_consolidado CASCADE;
DROP VIEW IF EXISTS vw_trabajadores_consolidado CASCADE;

DROP TABLE IF EXISTS derivaciones_programas CASCADE;
DROP TABLE IF EXISTS unidades_medios_pago CASCADE;
DROP TABLE IF EXISTS trabajadores_medios_pago CASCADE;
DROP TABLE IF EXISTS marketing_kpis CASCADE;
DROP TABLE IF EXISTS trabajadores CASCADE;
DROP TABLE IF EXISTS unidades_productivas CASCADE;
DROP TABLE IF EXISTS indicadores_sociales CASCADE;
DROP TABLE IF EXISTS programas_formalizacion CASCADE;
DROP TABLE IF EXISTS canales_marketing CASCADE;
DROP TABLE IF EXISTS medios_pago CASCADE;
DROP TABLE IF EXISTS rubros_mypes CASCADE;
DROP TABLE IF EXISTS oficios CASCADE;
DROP TABLE IF EXISTS barrios CASCADE;

-- ============================================================================
-- 1. TABLAS DE CATÁLOGO Y DIMENSIONES (NORMALIZACIÓN 3FN)
-- ============================================================================

-- 1.1 Catálogo de Barrios Urbanos y Periurbanos de Villarrica (Guairá)
CREATE TABLE barrios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    lat_min NUMERIC(10, 6) NOT NULL,
    lat_max NUMERIC(10, 6) NOT NULL,
    lon_min NUMERIC(10, 6) NOT NULL,
    lon_max NUMERIC(10, 6) NOT NULL,
    alt_min NUMERIC(6, 2) NOT NULL,
    alt_max NUMERIC(6, 2) NOT NULL,
    peso_muestral NUMERIC(4, 2) NOT NULL CHECK (peso_muestral > 0 AND peso_muestral <= 1.0),
    descripcion TEXT NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.2 Catálogo de Oficios Típicos del Sector Informal Individual
CREATE TABLE oficios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    sector VARCHAR(60) NOT NULL,
    ingreso_base_pyg NUMERIC(12, 2) NOT NULL CHECK (ingreso_base_pyg >= 0),
    descripcion TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.3 Catálogo de Rubros Económicos de Unidades Productivas (MYPEs)
CREATE TABLE rubros_mypes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    sector_economico VARCHAR(60) NOT NULL,
    facturacion_base_pyg NUMERIC(14, 2) NOT NULL CHECK (facturacion_base_pyg >= 0),
    rango_trabajadores_min INT NOT NULL DEFAULT 1 CHECK (rango_trabajadores_min >= 1),
    rango_trabajadores_max INT NOT NULL DEFAULT 10 CHECK (rango_trabajadores_max >= rango_trabajadores_min),
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.4 Catálogo de Medios de Pago y Cobro (Inclusión Financiera y Bancarización)
CREATE TABLE medios_pago (
    codigo VARCHAR(30) PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    categoria VARCHAR(50) NOT NULL,
    es_digital BOOLEAN NOT NULL DEFAULT FALSE,
    descripcion TEXT
);

-- 1.5 Catálogo de Canales de la Estrategia de Marketing Social
CREATE TABLE canales_marketing (
    id_canal SERIAL PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL,
    responsable_operativo VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- 1.6 Catálogo de Programas Públicos e Interinstitucionales de Formalización
CREATE TABLE programas_formalizacion (
    id_programa VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE,
    institucion_rectora VARCHAR(120) NOT NULL,
    tipo_beneficio VARCHAR(100) NOT NULL,
    base_legal VARCHAR(150) NOT NULL,
    contacto_villarrica VARCHAR(150) NOT NULL,
    requisitos_resumen TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 2. TABLAS PRINCIPALES (ENTIDADES DEL MODELO)
-- ============================================================================

-- 2.1 Entidad UNIDADES_PRODUCTIVAS (MYPEs, Puestos y Talleres de Villarrica)
CREATE TABLE unidades_productivas (
    id_unidad VARCHAR(20) PRIMARY KEY,
    nombre_establecimiento VARCHAR(150) NOT NULL,
    barrio_id INT NOT NULL REFERENCES barrios(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    latitud NUMERIC(10, 6) NOT NULL CHECK (latitud BETWEEN -25.800000 AND -25.700000),
    longitud NUMERIC(10, 6) NOT NULL CHECK (longitud BETWEEN -56.500000 AND -56.400000),
    rubro_id INT NOT NULL REFERENCES rubros_mypes(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    antiguedad_anios INT NOT NULL CHECK (antiguedad_anios >= 0),
    total_trabajadores INT NOT NULL CHECK (total_trabajadores >= 1),
    trabajadores_sin_ips INT NOT NULL CHECK (trabajadores_sin_ips >= 0),
    trabajadores_con_ips INT NOT NULL CHECK (trabajadores_con_ips >= 0),
    tasa_informalidad_laboral_pct NUMERIC(5, 2) NOT NULL CHECK (tasa_informalidad_laboral_pct BETWEEN 0.00 AND 100.00),
    estado_tributario_ruc VARCHAR(80) NOT NULL,
    motivo_no_aporte_ips TEXT NOT NULL,
    ingreso_mensual_estimado_pyg NUMERIC(14, 2) NOT NULL CHECK (ingreso_mensual_estimado_pyg >= 0),
    disposicion_formalizar VARCHAR(80) NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_suma_trabajadores CHECK (total_trabajadores = (trabajadores_sin_ips + trabajadores_con_ips))
);

-- 2.2 Entidad TRABAJADORES (Diagnóstico Sociodemográfico y Laboral)
CREATE TABLE trabajadores (
    id_trabajador VARCHAR(20) PRIMARY KEY,
    kobo_uuid UUID NOT NULL UNIQUE,
    fecha_recoleccion DATE NOT NULL,
    barrio_id INT NOT NULL REFERENCES barrios(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    latitud NUMERIC(10, 6) NOT NULL CHECK (latitud BETWEEN -25.800000 AND -25.700000),
    longitud NUMERIC(10, 6) NOT NULL CHECK (longitud BETWEEN -56.500000 AND -56.400000),
    edad INT NOT NULL CHECK (edad BETWEEN 15 AND 99),
    genero VARCHAR(20) NOT NULL CHECK (genero IN ('masculino', 'femenino', 'otro')),
    oficio_id INT NOT NULL REFERENCES oficios(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    antiguedad_oficio_anios INT NOT NULL CHECK (antiguedad_oficio_anios >= 0),
    ingreso_mensual_pyg NUMERIC(12, 2) NOT NULL CHECK (ingreso_mensual_pyg >= 0),
    horas_semanales INT NOT NULL CHECK (horas_semanales BETWEEN 1 AND 120),
    cobertura_ips VARCHAR(50) NOT NULL,
    motivo_no_ips VARCHAR(100) NOT NULL,
    posee_smartphone VARCHAR(5) NOT NULL CHECK (posee_smartphone IN ('si', 'no')),
    tipo_conectividad VARCHAR(50) NOT NULL,
    conoce_resimple VARCHAR(5) NOT NULL CHECK (conoce_resimple IN ('si', 'no')),
    interes_formalizacion VARCHAR(50) NOT NULL,
    unidad_productiva_id VARCHAR(20) REFERENCES unidades_productivas(id_unidad) ON UPDATE CASCADE ON DELETE SET NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2.3 Entidad INDICADORES_SOCIALES (10 Métricas Analíticas - Cátedra Realidad Social)
-- Normalizado 1:1 con Trabajadores para evitar redundancia y dependencia transitiva
CREATE TABLE indicadores_sociales (
    id_indicador SERIAL PRIMARY KEY,
    trabajador_id VARCHAR(20) NOT NULL UNIQUE REFERENCES trabajadores(id_trabajador) ON DELETE CASCADE,
    salario_minimo_referencia_pyg NUMERIC(12, 2) NOT NULL DEFAULT 3044000.00 CHECK (salario_minimo_referencia_pyg > 0),
    brecha_salario_pyg NUMERIC(12, 2) NOT NULL,
    situacion_respecto_minimo VARCHAR(50) NOT NULL CHECK (situacion_respecto_minimo IN ('Inferior al mínimo', 'Igual o superior al mínimo')),
    condicion_jornada VARCHAR(60) NOT NULL CHECK (condicion_jornada IN ('Subocupado por insuficiencia de tiempo', 'Jornada laboral típica', 'Sobreocupado laboralmente')),
    nivel_educativo VARCHAR(80) NOT NULL,
    anios_estudio INT NOT NULL CHECK (anios_estudio BETWEEN 0 AND 30),
    brecha_digital VARCHAR(80) NOT NULL,
    acepta_pagos_digitales VARCHAR(5) NOT NULL CHECK (acepta_pagos_digitales IN ('si', 'no')),
    personas_a_cargo INT NOT NULL CHECK (personas_a_cargo >= 0),
    tenencia_vivienda VARCHAR(50) NOT NULL CHECK (tenencia_vivienda IN ('propia', 'alquilada', 'prestada_familiar')),
    indice_vulnerabilidad_social NUMERIC(5, 2) NOT NULL CHECK (indice_vulnerabilidad_social BETWEEN 0.00 AND 100.00),
    clasificacion_vulnerabilidad VARCHAR(40) NOT NULL CHECK (clasificacion_vulnerabilidad IN ('Vulnerabilidad Baja', 'Vulnerabilidad Media', 'Vulnerabilidad Alta', 'Vulnerabilidad Crítica')),
    fecha_calculo TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2.4 Entidad MARKETING_KPIS (Rendimiento Multicanal Campaña "Trabajo Formal, Futuro Seguro")
CREATE TABLE marketing_kpis (
    id_kpi SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    canal_id INT NOT NULL REFERENCES canales_marketing(id_canal) ON UPDATE CASCADE ON DELETE RESTRICT,
    impresiones_alcance INT NOT NULL CHECK (impresiones_alcance >= 0),
    clics_interacciones INT NOT NULL CHECK (clics_interacciones >= 0),
    ctr_interaccion_pct NUMERIC(6, 2) NOT NULL CHECK (ctr_interaccion_pct >= 0),
    consultas_iniciadas INT NOT NULL CHECK (consultas_iniciadas >= 0),
    consultas_tema_resimple INT NOT NULL CHECK (consultas_tema_resimple >= 0),
    consultas_tema_ips INT NOT NULL CHECK (consultas_tema_ips >= 0),
    derivaciones_suace_villarrica INT NOT NULL CHECK (derivaciones_suace_villarrica >= 0),
    derivaciones_ips_regional INT NOT NULL CHECK (derivaciones_ips_regional >= 0),
    derivaciones_totales_formalizacion INT NOT NULL CHECK (derivaciones_totales_formalizacion >= 0),
    presupuesto_invertido_pyg NUMERIC(12, 2) NOT NULL CHECK (presupuesto_invertido_pyg >= 0),
    costo_por_consulta_pyg NUMERIC(12, 2) NOT NULL CHECK (costo_por_consulta_pyg >= 0),
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_marketing_fecha_canal UNIQUE (fecha, canal_id),
    CONSTRAINT chk_suma_derivaciones CHECK (derivaciones_totales_formalizacion = (derivaciones_suace_villarrica + derivaciones_ips_regional))
);

-- 2.5 Entidad DERIVACIONES_PROGRAMAS (Trazabilidad y Articulación con Políticas Públicas)
CREATE TABLE derivaciones_programas (
    id_derivacion INT PRIMARY KEY,
    codigo_derivacion VARCHAR(40) NOT NULL UNIQUE,
    fecha_derivacion DATE NOT NULL,
    canal_codigo VARCHAR(30) NOT NULL REFERENCES canales_marketing(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    programa_id VARCHAR(20) NOT NULL REFERENCES programas_formalizacion(id_programa) ON UPDATE CASCADE ON DELETE RESTRICT,
    trabajador_id VARCHAR(20) REFERENCES trabajadores(id_trabajador) ON UPDATE CASCADE ON DELETE SET NULL,
    estado_tramite VARCHAR(50) NOT NULL,
    atendido_por VARCHAR(120) NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. TABLAS ASOCIATIVAS / RELACIONALES (DESCOMPOSICIÓN EN 1FN Y 3FN)
-- ============================================================================

-- 3.1 Relación N:M Trabajadores <-> Medios de Pago
CREATE TABLE trabajadores_medios_pago (
    trabajador_id VARCHAR(20) NOT NULL REFERENCES trabajadores(id_trabajador) ON DELETE CASCADE,
    medio_pago_codigo VARCHAR(30) NOT NULL REFERENCES medios_pago(codigo) ON DELETE RESTRICT,
    PRIMARY KEY (trabajador_id, medio_pago_codigo)
);

-- 3.2 Relación N:M Unidades Productivas <-> Medios de Pago
CREATE TABLE unidades_medios_pago (
    unidad_id VARCHAR(20) NOT NULL REFERENCES unidades_productivas(id_unidad) ON DELETE CASCADE,
    medio_pago_codigo VARCHAR(30) NOT NULL REFERENCES medios_pago(codigo) ON DELETE RESTRICT,
    PRIMARY KEY (unidad_id, medio_pago_codigo)
);

-- ============================================================================
-- 4. ÍNDICES DE RENDIMIENTO (B-TREE Y ESPACIALES)
-- ============================================================================

-- Índices B-Tree en Claves Foráneas (optimización de joins)
CREATE INDEX idx_trabajadores_barrio_id ON trabajadores(barrio_id);
CREATE INDEX idx_trabajadores_oficio_id ON trabajadores(oficio_id);
CREATE INDEX idx_trabajadores_fecha ON trabajadores(fecha_recoleccion);
CREATE INDEX idx_trabajadores_genero ON trabajadores(genero);

CREATE INDEX idx_indicadores_trabajador_id ON indicadores_sociales(trabajador_id);
CREATE INDEX idx_indicadores_vulnerabilidad ON indicadores_sociales(indice_vulnerabilidad_social);
CREATE INDEX idx_indicadores_brecha_digital ON indicadores_sociales(brecha_digital);
CREATE INDEX idx_indicadores_sit_minimo ON indicadores_sociales(situacion_respecto_minimo);

CREATE INDEX idx_unidades_barrio_id ON unidades_productivas(barrio_id);
CREATE INDEX idx_unidades_rubro_id ON unidades_productivas(rubro_id);
CREATE INDEX idx_unidades_estado_ruc ON unidades_productivas(estado_tributario_ruc);
CREATE INDEX idx_unidades_tasa_informalidad ON unidades_productivas(tasa_informalidad_laboral_pct);

CREATE INDEX idx_marketing_fecha ON marketing_kpis(fecha);
CREATE INDEX idx_marketing_canal_id ON marketing_kpis(canal_id);

CREATE INDEX idx_derivaciones_fecha ON derivaciones_programas(fecha_derivacion);
CREATE INDEX idx_derivaciones_canal ON derivaciones_programas(canal_codigo);
CREATE INDEX idx_derivaciones_programa ON derivaciones_programas(programa_id);
CREATE INDEX idx_derivaciones_trabajador ON derivaciones_programas(trabajador_id);
CREATE INDEX idx_trabajadores_unidad ON trabajadores(unidad_productiva_id);

-- Índices B-Tree compuestos para optimización de consultas geoespaciales
CREATE INDEX idx_trabajadores_geo_coords ON trabajadores(latitud, longitud);
CREATE INDEX idx_unidades_geo_coords ON unidades_productivas(latitud, longitud);

-- ============================================================================
-- 5. VISTAS ANALÍTICAS GERENCIALES (PARA POWER BI / TABLEAU Y REPORTES APA 7)
-- ============================================================================

-- 5.1 Vista Consolidada de Trabajadores e Indicadores Sociales
CREATE OR REPLACE VIEW vw_trabajadores_consolidado AS
SELECT 
    t.id_trabajador,
    t.kobo_uuid,
    t.fecha_recoleccion,
    b.nombre AS barrio,
    t.latitud,
    t.longitud,
    t.edad,
    t.genero,
    i.nivel_educativo,
    i.anios_estudio,
    o.nombre AS oficio_rubro,
    o.sector AS sector_oficio,
    t.antiguedad_oficio_anios,
    t.ingreso_mensual_pyg,
    i.salario_minimo_referencia_pyg,
    i.brecha_salario_pyg,
    i.situacion_respecto_minimo,
    t.horas_semanales,
    i.condicion_jornada,
    t.cobertura_ips,
    t.motivo_no_ips,
    t.posee_smartphone,
    t.tipo_conectividad,
    i.brecha_digital,
    i.acepta_pagos_digitales,
    i.personas_a_cargo,
    i.tenencia_vivienda,
    i.indice_vulnerabilidad_social,
    i.clasificacion_vulnerabilidad,
    t.conoce_resimple,
    t.interes_formalizacion,
    t.unidad_productiva_id,
    up.nombre_establecimiento AS establecimiento_empleador,
    COALESCE(STRING_AGG(mp.nombre, ', ' ORDER BY mp.nombre), 'Sin registro') AS medios_pago_habilitados
FROM trabajadores t
JOIN barrios b ON t.barrio_id = b.id
JOIN oficios o ON t.oficio_id = o.id
LEFT JOIN unidades_productivas up ON t.unidad_productiva_id = up.id_unidad
LEFT JOIN indicadores_sociales i ON t.id_trabajador = i.trabajador_id
LEFT JOIN trabajadores_medios_pago tmp ON t.id_trabajador = tmp.trabajador_id
LEFT JOIN medios_pago mp ON tmp.medio_pago_codigo = mp.codigo
GROUP BY 
    t.id_trabajador, t.kobo_uuid, t.fecha_recoleccion, b.nombre, t.latitud, t.longitud,
    t.edad, t.genero, i.nivel_educativo, i.anios_estudio, o.nombre, o.sector, t.antiguedad_oficio_anios, t.ingreso_mensual_pyg,
    i.salario_minimo_referencia_pyg, i.brecha_salario_pyg, i.situacion_respecto_minimo,
    t.horas_semanales, i.condicion_jornada, t.cobertura_ips, t.motivo_no_ips,
    t.posee_smartphone, t.tipo_conectividad, i.brecha_digital, i.acepta_pagos_digitales,
    i.personas_a_cargo, i.tenencia_vivienda, i.indice_vulnerabilidad_social,
    i.clasificacion_vulnerabilidad, t.conoce_resimple, t.interes_formalizacion,
    t.unidad_productiva_id, up.nombre_establecimiento;

-- 5.2 Vista Consolidada de Unidades Productivas
CREATE OR REPLACE VIEW vw_unidades_productivas_consolidado AS
SELECT 
    u.id_unidad,
    u.nombre_establecimiento,
    b.nombre AS barrio,
    u.latitud,
    u.longitud,
    rm.nombre AS rubro_actividad,
    rm.sector_economico,
    u.antiguedad_anios,
    u.total_trabajadores,
    u.trabajadores_sin_ips,
    u.trabajadores_con_ips,
    u.tasa_informalidad_laboral_pct,
    u.estado_tributario_ruc,
    u.motivo_no_aporte_ips,
    u.ingreso_mensual_estimado_pyg,
    u.disposicion_formalizar,
    COALESCE(STRING_AGG(mp.nombre, ', ' ORDER BY mp.nombre), 'Exclusivamente efectivo') AS medios_pago_aceptados
FROM unidades_productivas u
JOIN barrios b ON u.barrio_id = b.id
JOIN rubros_mypes rm ON u.rubro_id = rm.id
LEFT JOIN unidades_medios_pago ump ON u.id_unidad = ump.unidad_id
LEFT JOIN medios_pago mp ON ump.medio_pago_codigo = mp.codigo
GROUP BY 
    u.id_unidad, u.nombre_establecimiento, b.nombre, u.latitud, u.longitud,
    rm.nombre, rm.sector_economico, u.antiguedad_anios, u.total_trabajadores,
    u.trabajadores_sin_ips, u.trabajadores_con_ips, u.tasa_informalidad_laboral_pct,
    u.estado_tributario_ruc, u.motivo_no_aporte_ips, u.ingreso_mensual_estimado_pyg,
    u.disposicion_formalizar;

-- 5.3 Vista Resumen de Rendimiento de Marketing Social por Canal
CREATE OR REPLACE VIEW vw_marketing_resumen_canales AS
SELECT 
    c.codigo AS codigo_canal,
    c.nombre AS canal_nombre,
    c.tipo AS tipo_canal,
    COUNT(m.id_kpi) AS dias_medidos,
    SUM(m.impresiones_alcance) AS total_alcance,
    SUM(m.clics_interacciones) AS total_interacciones,
    ROUND(AVG(m.ctr_interaccion_pct), 2) AS ctr_promedio_pct,
    SUM(m.consultas_iniciadas) AS total_consultas,
    SUM(m.consultas_tema_resimple) AS total_consultas_resimple,
    SUM(m.consultas_tema_ips) AS total_consultas_ips,
    SUM(m.derivaciones_suace_villarrica) AS total_derivaciones_suace,
    SUM(m.derivaciones_ips_regional) AS total_derivaciones_ips,
    SUM(m.derivaciones_totales_formalizacion) AS total_derivaciones,
    SUM(m.presupuesto_invertido_pyg) AS presupuesto_total_pyg,
    CASE 
        WHEN SUM(m.consultas_iniciadas) > 0 
        THEN ROUND(SUM(m.presupuesto_invertido_pyg) / SUM(m.consultas_iniciadas), 0)
        ELSE 0 
    END AS costo_promedio_por_consulta_pyg,
    CASE 
        WHEN SUM(m.derivaciones_totales_formalizacion) > 0 
        THEN ROUND(SUM(m.presupuesto_invertido_pyg) / SUM(m.derivaciones_totales_formalizacion), 0)
        ELSE 0 
    END AS costo_por_derivacion_efectiva_pyg
FROM canales_marketing c
LEFT JOIN marketing_kpis m ON c.id_canal = m.canal_id
GROUP BY c.id_canal, c.codigo, c.nombre, c.tipo
ORDER BY total_derivaciones DESC;

-- 5.4 Vista de Articulación de Programas de Formalización con Demanda Ciudadana
CREATE OR REPLACE VIEW vw_articulacion_programas_formalizacion AS
SELECT 
    p.id_programa,
    p.nombre AS programa,
    p.institucion_rectora,
    p.base_legal,
    p.contacto_villarrica,
    COUNT(d.id_derivacion) AS total_derivaciones_registradas,
    COUNT(DISTINCT d.trabajador_id) AS trabajadores_unicos_derivados,
    SUM(CASE WHEN d.estado_tramite = 'Formalizado' THEN 1 ELSE 0 END) AS tramites_formalizados,
    SUM(CASE WHEN d.estado_tramite = 'En Asistencia' THEN 1 ELSE 0 END) AS tramites_en_asistencia,
    CASE 
        WHEN p.id_programa = 'RESIMPLE' THEN (SELECT COUNT(*) FROM unidades_productivas WHERE estado_tributario_ruc = 'Inscripto en RESIMPLE (DNIT)')
        WHEN p.id_programa = 'IPS_MICRO' THEN (SELECT COUNT(*) FROM unidades_productivas WHERE trabajadores_con_ips > 0)
        WHEN p.id_programa = 'SUACE' THEN (SELECT COUNT(*) FROM unidades_productivas WHERE estado_tributario_ruc <> 'Sin RUC (Totalmente informal)')
        ELSE 0
    END AS unidades_vinculadas_actualmente
FROM programas_formalizacion p
LEFT JOIN derivaciones_programas d ON p.id_programa = d.programa_id
GROUP BY p.id_programa, p.nombre, p.institucion_rectora, p.base_legal, p.contacto_villarrica
ORDER BY p.id_programa;
