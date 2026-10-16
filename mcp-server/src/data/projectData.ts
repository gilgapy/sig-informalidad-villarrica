import {
  ProjectMetadata,
  ProjectObjective,
  MethodologicalStep,
  SessionPlan,
  RubricIndicator
} from '../types/index.js';

export const PROJECT_METADATA: ProjectMetadata = Object.freeze({
  title: 'Transformación Digital y Diagnóstico Social en la Gestión Organizacional',
  socialProblem: 'La Informalidad Laboral en el Paraguay',
  institution: 'Universidad Nacional de Villarrica del Espíritu Santo - UNVES',
  faculty: 'Facultad de Ciencias Económicas',
  career: 'Licenciatura en Administración de Empresas',
  semester: '8° Semestre',
  course: '4° curso',
  location: 'Villarrica - Paraguay',
  academicYear: 2026,
  subjects: Object.freeze([
    'Marketing Social',
    'Análisis de la Realidad Social del Paraguay',
    'Sistema de Información Gerencial'
  ]),
  facultyStaff: Object.freeze([
    'Prof. Mag. Clara Demattei',
    'Prof. Mag. Gerardo Ortiz',
    'Prof. Dra. Ramona Demattei'
  ]),
  studentGroup: 'Estudiantes del 8° semestre de la carrera Administración de Empresas'
});

export const PROJECT_OBJECTIVES: readonly ProjectObjective[] = Object.freeze([
  Object.freeze({
    id: 'obj-1',
    description: 'Diagnosticar problemáticas sociales del entorno local.'
  }),
  Object.freeze({
    id: 'obj-2',
    description: 'Proponer campañas de marketing social basadas en datos.'
  }),
  Object.freeze({
    id: 'obj-3',
    description: 'Diseñar un sistema de información que apoye la toma de decisiones sociales.'
  })
]);

export const METHODOLOGICAL_STEPS: readonly MethodologicalStep[] = Object.freeze([
  Object.freeze({
    stepNumber: 1,
    title: 'Lanzamiento e Identificación de Requerimientos de Información',
    objectives: Object.freeze([
      'Presentar el proyecto interdisciplinario enfocado en la problemática de la informalidad laboral en Paraguay.',
      'Identificar necesidades de captura, almacenamiento, procesamiento y análisis de datos para la gestión del proyecto.'
    ])
  }),
  Object.freeze({
    stepNumber: 2,
    title: 'Diseño y Modelado de la Base de Datos Relacional',
    objectives: Object.freeze([
      'Orientar el diseño lógico y conceptual del modelo entidad-relación (Trabajadores, Empleadores / Unidades Productivas, Programas de Formalización, Indicadores Sociales).',
      'Asegurar que los atributos de cada entidad respondan directamente a los indicadores medidos por Análisis de la Realidad Social del Paraguay (ingresos, seguridad social, georreferenciación, brecha digital, etc.).'
    ])
  }),
  Object.freeze({
    stepNumber: 3,
    title: 'Arquitectura Tecnológica e Integración de Herramientas de Captura',
    objectives: Object.freeze([
      'Definir el motor de base de datos (PostgreSQL / MySQL) y las interfaces de captura mediante formularios digitales en smartphones/tablets (KoboToolbox, Google Forms, SurveyCTO, ODK).',
      'Establecer mecanismos de integración para recibir las métricas digitales y de alcance generadas en las campañas de Marketing Social (consultas, interacciones, alcance digital).'
    ])
  }),
  Object.freeze({
    stepNumber: 4,
    title: 'Desarrollo de Sistemas de Información y Dashboards de Control (Power BI / Tableau / R)',
    objectives: Object.freeze([
      'Creación de tableros de control interactivos (dashboards) para visualizar indicadores en tiempo real.',
      'Diseñar reportes gerenciales orientados a la toma de decisiones, la reducción de la duplicación de datos y la transparencia en programas de formalización.'
    ])
  }),
  Object.freeze({
    stepNumber: 5,
    title: 'Sinergia e Integración Interdisciplinaria',
    objectives: Object.freeze([
      'Con Análisis de la Realidad Social: Automatizar el procesamiento de datos de campo y la georreferenciación de zonas con alta concentración de informalidad.',
      'Con Marketing Social: Incorporar al sistema el monitoreo continuo de los KPIs de la campaña "Trabajo Formal, Futuro Seguro" y el registro de consultas en portales digitales.'
    ])
  }),
  Object.freeze({
    stepNumber: 6,
    title: 'Consolidación del Informe, Evaluación y Cierre',
    objectives: Object.freeze([
      'Supervisar la inclusión de la propuesta tecnológica, diagramas ER, arquitectura y muestras de dashboards en el informe escrito en formato FCE-UNVES (normas APA 7.ª ed.).',
      'Evaluar mediante la rúbrica de 20 puntos, corroborar las evidencias digitales y firmar registros de asistencia y actas correspondientes.'
    ])
  })
]);

export const SESSIONS_TIMETABLE: readonly SessionPlan[] = Object.freeze([
  Object.freeze({
    sessionNumber: 1,
    date: '07/09/2026',
    day: 'Lunes',
    focus: 'Lanzamiento del Proyecto',
    details: 'Socialización del proyecto interdisciplinario, rol del SIG en la gestión de datos sociales y organización de equipos.'
  }),
  Object.freeze({
    sessionNumber: 2,
    date: '07/09/2026',
    day: 'Lunes',
    focus: 'Requerimientos de Información',
    details: 'Identificación de entidades y atributos necesarios para diagnosticar la informalidad laboral en Paraguay.'
  }),
  Object.freeze({
    sessionNumber: 3,
    date: '14/09/2026',
    day: 'Lunes',
    focus: 'Modelado de Datos I',
    details: 'Diseño del Modelo Entidad-Relación (Entidades: Trabajadores y Empleadores/Unidades Productivas).'
  }),
  Object.freeze({
    sessionNumber: 4,
    date: '14/09/2026',
    day: 'Lunes',
    focus: 'Modelado de Datos II',
    details: 'Diseño de las entidades de Programas de Formalización e Indicadores Sociales.'
  }),
  Object.freeze({
    sessionNumber: 5,
    date: '21/09/2026',
    day: 'Lunes',
    focus: 'Arquitectura de Base de Datos',
    details: 'Definición del motor de base de datos (PostgreSQL/MySQL) y normalización de tablas.'
  }),
  Object.freeze({
    sessionNumber: 6,
    date: '21/09/2026',
    day: 'Lunes',
    focus: 'Interfaces de Captura',
    details: 'Configuración de formularios móviles (KoboToolbox, Google Forms, ODK) para levantamiento de datos en campo.'
  }),
  Object.freeze({
    sessionNumber: 7,
    date: '28/09/2026',
    day: 'Lunes',
    focus: 'Integración de Insumos Social/Territorial',
    details: 'Carga y estructuración de los datos primarios recolectados por la cátedra de Análisis de la Realidad Social.'
  }),
  Object.freeze({
    sessionNumber: 8,
    date: '28/09/2026',
    day: 'Lunes',
    focus: 'Integración de Insumos de Marketing',
    details: 'Configuración de tablas para captura de métricas digitales (alcance, interacciones, consultas de formalización).'
  }),
  Object.freeze({
    sessionNumber: 9,
    date: '05/10/2026',
    day: 'Lunes',
    focus: 'Desarrollo de Dashboard I (Infraestructura)',
    details: 'Conexión de la base de datos con herramientas de BI (Power BI / Tableau / R) y backend en la nube.'
  }),
  Object.freeze({
    sessionNumber: 10,
    date: '05/10/2026',
    day: 'Lunes',
    focus: 'Desarrollo de Dashboard II (Visualización Social)',
    details: 'Diseño de tableros interactivos para indicadores de informalidad, género y georreferenciación.'
  }),
  Object.freeze({
    sessionNumber: 11,
    date: '12/10/2026',
    day: 'Lunes',
    focus: 'Desarrollo de Dashboard III (Monitoreo de Campaña)',
    details: 'Gráficos en tiempo real para evaluar el rendimiento del Plan de Marketing Social "Trabajo Formal, Futuro Seguro".'
  }),
  Object.freeze({
    sessionNumber: 12,
    date: '12/10/2026',
    day: 'Lunes',
    focus: 'Pruebas de Interoperabilidad y Calidad',
    details: 'Verificación de la no duplicidad de datos, integridad referencial y tiempos de respuesta.'
  }),
  Object.freeze({
    sessionNumber: 13,
    date: '19/10/2026',
    day: 'Lunes',
    focus: 'Redacción del Capítulo Cátedra',
    details: 'Documentación técnica del SIG (diagramas, código, arquitectura y manuales de usuario) para el informe.'
  }),
  Object.freeze({
    sessionNumber: 14,
    date: '19/10/2026',
    day: 'Lunes',
    focus: 'Ensamble del Informe Interdisciplinario',
    details: 'Integración de los apartados con Marketing Social y Análisis de la Realidad Social.'
  }),
  Object.freeze({
    sessionNumber: 15,
    date: '26/10/2026',
    day: 'Lunes',
    focus: 'Compilación de Evidencias Digitales',
    details: 'Preparación de capturas de pantallas, enlaces de dashboards funcionales y anexos.'
  }),
  Object.freeze({
    sessionNumber: 16,
    date: '26/10/2026',
    day: 'Lunes',
    focus: 'Ensayo y Ajustes Técnicos',
    details: 'Simulación de presentación del sistema, revisión bajo normas APA 7.ª edición.'
  }),
  Object.freeze({
    sessionNumber: 17,
    date: '02/11/2026',
    day: 'Lunes',
    focus: 'Presentación Final, Evaluación y Cierre',
    details: 'Demostración en vivo del Sistema de Información, aplicación de rúbricas y firma del acta de cierre.'
  })
]);

export const RUBRIC_INDICATORS: readonly RubricIndicator[] = Object.freeze([
  Object.freeze({
    id: 1,
    title: 'Modelado de Base de Datos y Entidades',
    points: 4,
    criteria: 'Diseña correctamente el esquema relacional identificando entidades principales (Trabajadores, Empleadores, Programas, Indicadores), claves y relaciones clave.',
    justification: Object.freeze([
      'Presenta el diagrama Entidad-Relación lógicamente estructurado.',
      'Define los campos primarios e identificadores clave (ID Trabajador, ID Empleador, ID Programa, ID Indicador) asegurando la integridad de la información.'
    ])
  }),
  Object.freeze({
    id: 2,
    title: 'Arquitectura Tecnológica y Captura Digital',
    points: 4,
    criteria: 'Define una arquitectura técnica viable (PostgreSQL/MySQL, nube) e integra herramientas digitales móviles de captura de datos (KoboToolbox/Google Forms).',
    justification: Object.freeze([
      'Fundamenta la elección de herramientas en la nube, servidores y motor de base de datos.',
      'Implementa formularios digitales que simplifican el levantamiento de datos primarios en el terreno de estudio.'
    ])
  }),
  Object.freeze({
    id: 3,
    title: 'Desarrollo de Dashboard Gerencial (Power BI / Tableau / R)',
    points: 4,
    criteria: 'Construye un tablero de control interactivo que permite visualizar indicadores clave en tiempo real para la toma de decisiones.',
    justification: Object.freeze([
      'Presenta tableros visuales interactivos y dinámicos creados en Power BI, Tableau u otros entornos interactivos.',
      'Facilita la generación de reportes estratégicos para la toma de decisiones en la gestión organizacional y de políticas públicas.'
    ])
  }),
  Object.freeze({
    id: 4,
    title: 'Articulación con Análisis de la Realidad Social',
    points: 3,
    criteria: 'Estructura la base de datos para almacenar y procesar con precisión los 10 indicadores sociales de campo y los datos georreferenciados recolectados.',
    justification: Object.freeze([
      'Almacena correctamente las variables de ingreso, seguridad social (IPS), educación, vulnerabilidad y ubicación geográfica obtenidas en el diagnóstico social.'
    ])
  }),
  Object.freeze({
    id: 5,
    title: 'Articulación con Marketing Social',
    points: 2,
    criteria: 'Incorpora métricas de seguimiento de la campaña "Trabajo Formal, Futuro Seguro" (alcance, interacciones, consultas de formalización) en el sistema.',
    justification: Object.freeze([
      'Registra y analiza los datos provenientes de la estrategia comunicacional (interacciones, impacto digital y flujo de interesados hacia portales de formalización).'
    ])
  }),
  Object.freeze({
    id: 6,
    title: 'Documentación Técnica, Evidencias y Defensa',
    points: 3,
    criteria: 'Documenta el sistema formalmente en el informe escrito (APA 7.ª ed.), adjunta evidencias de funcionamiento y demuestra el uso del software en la defensa final.',
    justification: Object.freeze([
      'Incluye la documentación técnica dentro del informe final institucional (FCE-UNVES).',
      'Realiza la navegación y demostración funcional del sistema durante la defensa oral ante la mesa evaluadora.'
    ])
  })
]);
