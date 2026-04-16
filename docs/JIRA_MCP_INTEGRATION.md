# Manual de Integración Jira MCP

## Información General
- **Servidor:** `@aashari/mcp-server-atlassian-jira`
- **Protocolo:** Model Context Protocol (MCP)
- **Instalación:** Configurado en `~/.mcporter/mcporter.json` vía `npx`.

## Herramientas Disponibles
Este servidor permite interactuar con Jira Cloud mediante herramientas que los LLMs pueden invocar:
- `search_issues`: Ejecuta consultas JQL para encontrar tickets.
- `get_issue`: Obtiene detalles completos de un ticket por ID/Key.
- `list_projects`: Lista los proyectos disponibles en el sitio.
- `get_dev_info`: Recupera información de desarrollo vinculada (commits, PRs).

## Configuración de Credenciales
El servidor requiere las siguientes variables de entorno en el objeto `env` de la configuración de mcporter:

| Variable | Descripción | Valor detectado |
| :--- | :--- | :--- |
| `ATLASSIAN_SITE_NAME` | Subdominio de Jira (ej: `empresa` en `empresa.atlassian.net`) | `chat-jepete` |
| `ATLASSIAN_USER_EMAIL` | Email de la cuenta de Atlassian | `chatjepetex4@gmail.com` |
| `ATLASSIAN_API_TOKEN` | Token generado en id.atlassian.com | *Pendiente* |

## Cómo usar desde Agentes
Una vez configuradas las credenciales, el agente Lucy podrá gestionar tickets de Jira automáticamente pidiendo permiso para buscar o leer estados de proyectos.

---
*Documento generado por Doctora Lucy el 16/04/2026.*
