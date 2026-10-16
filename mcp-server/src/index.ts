import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListToolsRequestSchema,
  CallToolRequestSchema,
  ErrorCode,
  McpError
} from '@modelcontextprotocol/sdk/types.js';

import { GUIDE_RESOURCES, getResourceContent } from './resources/guideResources.js';
import {
  handleGetSessionDetails,
  handleGetRubricIndicator,
  handleSearchGuideTopics
} from './tools/guideTools.js';

const server = new Server(
  {
    name: 'unves-informalidad-mcp-server',
    version: '1.0.0'
  },
  {
    capabilities: {
      resources: {},
      tools: {}
    }
  }
);

// 1. List Resources handler
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  try {
    return {
      resources: GUIDE_RESOURCES.map(r => ({
        uri: r.uri,
        name: r.name,
        description: r.description,
        mimeType: r.mimeType
      }))
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    process.stderr.write(`Error listing resources: ${message}\n`);
    throw new McpError(ErrorCode.InternalError, `No se pudieron listar los recursos: ${message}`);
  }
});

// 2. Read Resource handler
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;
  try {
    const resource = getResourceContent(uri);
    if (!resource) {
      throw new McpError(ErrorCode.InvalidRequest, `Recurso no encontrado con la URI: ${uri}`);
    }

    return {
      contents: [
        {
          uri,
          mimeType: resource.mimeType,
          text: resource.text
        }
      ]
    };
  } catch (err) {
    if (err instanceof McpError) throw err;
    const message = err instanceof Error ? err.message : String(err);
    process.stderr.write(`Error reading resource ${uri}: ${message}\n`);
    throw new McpError(ErrorCode.InternalError, `Fallo al leer recurso: ${message}`);
  }
});

// 3. List Tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_session_details',
        description: 'Obtiene detalles pedagógicos, fecha y actividades de las 17 sesiones del cronograma lectivo UNVES 2026',
        inputSchema: {
          type: 'object',
          properties: {
            sessionNumber: {
              type: 'integer',
              description: 'Número de sesión pedagógica (1 a 17)',
              minimum: 1,
              maximum: 17
            },
            date: {
              type: 'string',
              description: 'Fecha en formato DD/MM/AAAA (ejemplo: 07/09/2026)'
            }
          }
        }
      },
      {
        name: 'get_rubric_indicator',
        description: 'Consulta los criterios de evaluación, justificación y puntajes de los 6 indicadores (20 puntos totales)',
        inputSchema: {
          type: 'object',
          properties: {
            indicatorNumber: {
              type: 'integer',
              description: 'Número del indicador evaluativo (1 a 6)',
              minimum: 1,
              maximum: 6
            }
          },
          required: ['indicatorNumber']
        }
      },
      {
        name: 'search_guide_topics',
        description: 'Busca temas, palabras clave o competencias en la guía docente oficial del proyecto interdisciplinario',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Término a buscar (ej: "PostgreSQL", "marketing", "IPS", "dashboard", "KoboToolbox")'
            }
          },
          required: ['query']
        }
      }
    ]
  };
});

// 4. Call Tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    switch (name) {
      case 'get_session_details': {
        const result = handleGetSessionDetails(args ?? {});
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
        };
      }
      case 'get_rubric_indicator': {
        const result = handleGetRubricIndicator(args ?? {});
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
        };
      }
      case 'search_guide_topics': {
        const result = handleSearchGuideTopics(args ?? {});
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
        };
      }
      default:
        throw new McpError(ErrorCode.MethodNotFound, `Herramienta desconocida: ${name}`);
    }
  } catch (err) {
    if (err instanceof McpError) throw err;
    const message = err instanceof Error ? err.message : String(err);
    process.stderr.write(`Tool error on ${name}: ${message}\n`);
    throw new McpError(ErrorCode.InternalError, `Error ejecutando ${name}: ${message}`);
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  process.stderr.write('Servidor MCP UNVES Guía Docente conectado y listo via STDIO.\n');
}

main().catch((error) => {
  process.stderr.write(`Error fatal en el servidor MCP: ${error}\n`);
  process.exit(1);
});
