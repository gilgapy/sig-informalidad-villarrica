# Servidor MCP - Guía Docente UNVES (Proyecto Interdisciplinario)

Servidor MCP implementado en Node.js y TypeScript con `@modelcontextprotocol/sdk` para servir como **recurso estructurado y herramientas de consulta** del PDF oficial: *“Proyecto Interdisciplinario: Transformación Digital y Diagnóstico Social en la Gestión Organizacional - Problemática: La Informalidad Laboral en el Paraguay”* (UNVES - FCE, 8° Semestre, Villarrica - 2026).

---

## 📌 Recursos Expuestos (MCP Resources)

| URI | Nombre | Descripción |
| :--- | :--- | :--- |
| `unves://guia/general` | General | Datos institucionales UNVES, justificación y objetivos de las 3 cátedras. |
| `unves://guia/metodologia` | Metodología | Los 6 pasos metodológicos de ejecución para Sistema de Información Gerencial. |
| `unves://guia/cronograma` | Cronograma | Detalle de las 17 sesiones pedagógicas (Setiembre - Noviembre 2026). |
| `unves://guia/rubrica` | Rúbrica | Criterios de evaluación (20 puntos totales, 6 indicadores de desempeño). |
| `unves://guia/indicadores-sociales` | Indicadores Sociales | Variables clave de campo para Análisis de la Realidad Social del Paraguay. |
| `unves://guia/marketing` | Marketing Social | Estructura y KPIs de la campaña *"Trabajo Formal, Futuro Seguro"*. |

---

## 🛠️ Herramientas Disponibles (MCP Tools)

1. `get_session_details`: Consulta por número de sesión (1 a 17) o por fecha (`DD/MM/AAAA`).
2. `get_rubric_indicator`: Consulta criterios y justificación por número de indicador (1 a 6).
3. `search_guide_topics`: Búsqueda de texto completo sobre contenidos de la guía.

---

## 🚀 Comandos

```bash
# Compilar TypeScript
npm run build

# Ejecutar pruebas unitarias
npm test

# Ejecutar servidor MCP via stdio
npm start
```
