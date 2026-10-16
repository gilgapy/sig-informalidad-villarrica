import {
  PROJECT_METADATA,
  PROJECT_OBJECTIVES,
  METHODOLOGICAL_STEPS,
  SESSIONS_TIMETABLE,
  RUBRIC_INDICATORS
} from '../data/projectData.js';

export interface McpResourceDefinition {
  readonly uri: string;
  readonly name: string;
  readonly description: string;
  readonly mimeType: string;
}

export const GUIDE_RESOURCES: readonly McpResourceDefinition[] = Object.freeze([
  Object.freeze({
    uri: 'unves://guia/general',
    name: 'Información General del Proyecto Interdisciplinario',
    description: 'Datos institucionales UNVES, fundamentación y objetivos de las 3 materias',
    mimeType: 'application/json'
  }),
  Object.freeze({
    uri: 'unves://guia/metodologia',
    name: 'Guía Metodológica de 6 Pasos (SIG)',
    description: 'Etapas de ejecución para la cátedra de Sistema de Información Gerencial',
    mimeType: 'application/json'
  }),
  Object.freeze({
    uri: 'unves://guia/cronograma',
    name: 'Cronograma de 17 Sesiones Pedagógicas',
    description: 'Calendario detallado de las 17 sesiones (Setiembre - Noviembre 2026)',
    mimeType: 'application/json'
  }),
  Object.freeze({
    uri: 'unves://guia/rubrica',
    name: 'Rúbrica de Evaluación Institucional (20 Puntos)',
    description: 'Criterios detallados y desglose de puntajes para Sistema de Información Gerencial',
    mimeType: 'application/json'
  }),
  Object.freeze({
    uri: 'unves://guia/indicadores-sociales',
    name: 'Requerimientos de Datos Sociales y Territoriales',
    description: 'Variables de campo requeridas por Análisis de la Realidad Social del Paraguay',
    mimeType: 'application/json'
  }),
  Object.freeze({
    uri: 'unves://guia/marketing',
    name: 'Métricas de la Campaña de Marketing Social',
    description: 'Estructura de datos para la campaña Trabajo Formal, Futuro Seguro',
    mimeType: 'application/json'
  })
]);

export function getResourceContent(uri: string): { readonly text: string; readonly mimeType: string } | null {
  try {
    switch (uri) {
      case 'unves://guia/general':
        return {
          text: JSON.stringify({
            metadata: PROJECT_METADATA,
            objectives: PROJECT_OBJECTIVES
          }, null, 2),
          mimeType: 'application/json'
        };

      case 'unves://guia/metodologia':
        return {
          text: JSON.stringify({
            steps: METHODOLOGICAL_STEPS
          }, null, 2),
          mimeType: 'application/json'
        };

      case 'unves://guia/cronograma':
        return {
          text: JSON.stringify({
            totalSessions: SESSIONS_TIMETABLE.length,
            timetable: SESSIONS_TIMETABLE
          }, null, 2),
          mimeType: 'application/json'
        };

      case 'unves://guia/rubrica':
        return {
          text: JSON.stringify({
            totalPoints: 20,
            indicatorsCount: RUBRIC_INDICATORS.length,
            indicators: RUBRIC_INDICATORS
          }, null, 2),
          mimeType: 'application/json'
        };

      case 'unves://guia/indicadores-sociales':
        return {
          text: JSON.stringify({
            socialContext: 'Informalidad Laboral en Paraguay (Villarrica / Dpto. Guairá)',
            targetIndicators: [
              'Nivel de ingresos mensuales (en PYG frente a Salario Mínimo Legal)',
              'Acceso y cotización a la Seguridad Social (IPS)',
              'Nivel educativo alcanzado y alfabetización digital',
              'Sector de actividad económica informal (comercio, servicios, manufactura, gastronomía)',
              'Condición de empleo (cuenta propia, asalariado no registrado, familiar no remunerado)',
              'Años de antigüedad en la actividad informal',
              'Tenencia y uso de smartphone para transacciones / cobros digitales',
              'Ubicación territorial y barrio georreferenciado en Villarrica',
              'Motivo principal de no formalización (costos, trámites, desconocimiento)',
              'Interés y disposición hacia programas de formalización o microcréditos'
            ]
          }, null, 2),
          mimeType: 'application/json'
        };

      case 'unves://guia/marketing':
        return {
          text: JSON.stringify({
            campaignName: 'Trabajo Formal, Futuro Seguro',
            channels: ['Facebook Ads', 'Instagram', 'WhatsApp Business Directo', 'Feria Presencial en Villarrica'],
            kpis: [
              'Alcance total de impresiones digitales',
              'Tasa de interacción (engagement rate)',
              'Consultas directas iniciadas sobre formalización',
              'Direccionamiento a portales del MTESS / IPS / SUACE',
              'Asistencias a charlas de orientación en Villarrica'
            ]
          }, null, 2),
          mimeType: 'application/json'
        };

      default:
        return null;
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    throw new Error(`Error recuperando recurso ${uri}: ${message}`);
  }
}
