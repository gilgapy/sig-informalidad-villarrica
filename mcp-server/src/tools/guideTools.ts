import {
  SESSIONS_TIMETABLE,
  RUBRIC_INDICATORS,
  METHODOLOGICAL_STEPS,
  PROJECT_METADATA
} from '../data/projectData.js';
import {
  ApiResponse,
  QuerySessionSchema,
  QueryRubricSchema,
  SearchTopicsSchema,
  SessionPlan,
  RubricIndicator
} from '../types/index.js';

export function handleGetSessionDetails(input: unknown): ApiResponse<SessionPlan | readonly SessionPlan[]> {
  try {
    const parsed = QuerySessionSchema.parse(input);

    if (parsed.sessionNumber !== undefined) {
      const session = SESSIONS_TIMETABLE.find(s => s.sessionNumber === parsed.sessionNumber);
      if (!session) {
        return {
          success: false,
          error: `Sesión pedagógica número ${parsed.sessionNumber} no encontrada.`
        };
      }
      return {
        success: true,
        data: session,
        meta: { source: 'Guía Docente UNVES 2026' }
      };
    }

    if (parsed.date) {
      const sessions = SESSIONS_TIMETABLE.filter(s => s.date === parsed.date);
      if (sessions.length === 0) {
        return {
          success: false,
          error: `No hay sesiones programadas para la fecha ${parsed.date}.`
        };
      }
      return {
        success: true,
        data: sessions,
        meta: { date: parsed.date, totalFound: sessions.length }
      };
    }

    return {
      success: true,
      data: SESSIONS_TIMETABLE,
      meta: { totalSessions: SESSIONS_TIMETABLE.length }
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      success: false,
      error: `Error de validación o ejecución: ${message}`
    };
  }
}

export function handleGetRubricIndicator(input: unknown): ApiResponse<RubricIndicator> {
  try {
    const parsed = QueryRubricSchema.parse(input);
    const indicator = RUBRIC_INDICATORS.find(i => i.id === parsed.indicatorNumber);

    if (!indicator) {
      return {
        success: false,
        error: `Indicador de rúbrica ${parsed.indicatorNumber} no encontrado (rango válido: 1 al 6).`
      };
    }

    return {
      success: true,
      data: indicator,
      meta: { totalRubricPoints: 20 }
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      success: false,
      error: `Error de validación: ${message}`
    };
  }
}

export function handleSearchGuideTopics(input: unknown): ApiResponse<readonly Record<string, unknown>[]> {
  try {
    const parsed = SearchTopicsSchema.parse(input);
    const term = parsed.query.toLowerCase().trim();
    const results: Record<string, unknown>[] = [];

    // Search in Methodological steps
    for (const step of METHODOLOGICAL_STEPS) {
      const matchInTitle = step.title.toLowerCase().includes(term);
      const matchInObjectives = step.objectives.some(o => o.toLowerCase().includes(term));
      if (matchInTitle || matchInObjectives) {
        results.push({
          type: 'methodological_step',
          stepNumber: step.stepNumber,
          title: step.title,
          matchedContent: step.objectives
        });
      }
    }

    // Search in Sessions
    for (const session of SESSIONS_TIMETABLE) {
      const matchInFocus = session.focus.toLowerCase().includes(term);
      const matchInDetails = session.details.toLowerCase().includes(term);
      if (matchInFocus || matchInDetails) {
        results.push({
          type: 'session',
          sessionNumber: session.sessionNumber,
          date: session.date,
          focus: session.focus,
          details: session.details
        });
      }
    }

    // Search in Rubric
    for (const ind of RUBRIC_INDICATORS) {
      const matchTitle = ind.title.toLowerCase().includes(term);
      const matchCriteria = ind.criteria.toLowerCase().includes(term);
      const matchJust = ind.justification.some(j => j.toLowerCase().includes(term));
      if (matchTitle || matchCriteria || matchJust) {
        results.push({
          type: 'rubric_indicator',
          indicatorNumber: ind.id,
          title: ind.title,
          points: ind.points,
          criteria: ind.criteria
        });
      }
    }

    return {
      success: true,
      data: results,
      meta: {
        query: parsed.query,
        matchesCount: results.length,
        project: PROJECT_METADATA.title
      }
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      success: false,
      error: `Error en búsqueda de contenidos: ${message}`
    };
  }
}
