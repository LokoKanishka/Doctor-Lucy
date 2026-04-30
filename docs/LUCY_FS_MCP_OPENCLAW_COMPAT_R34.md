## R34 - Compatibilidad MCP del wrapper bajo OpenClaw

Fecha: 2026-04-29

### Objetivo

Aislar por que `scripts/lucy_fs_mcp_server.py` pasaba el test local propio pero
expiraba cuando OpenClaw lo lanzaba como MCP bundled en el perfil aislado
`lucy-fs-test`.

### Reproduccion inicial

Con el perfil aislado listo para `ollama`, el agente local seguia fallando al
arrancar el MCP:

- `[bundle-mcp] failed to start server "lucy-fs-readonly"`
- `McpError: MCP error -32001: Request timed out`

No se toco el perfil principal ni Telegram real.

### Causa probable confirmada

El wrapper estaba implementando transporte stdio con framing estilo LSP:

- `Content-Length: ...`
- cuerpo JSON luego de linea en blanco

Pero OpenClaw no estaba usando ese framing para MCP stdio. El SDK MCP real que
usa OpenClaw (`@modelcontextprotocol/sdk`) usa mensajes JSON por linea:

- un JSON-RPC por linea
- sin headers `Content-Length`

Eso explica por que:

- el test Python local propio pasaba
- OpenClaw y el SDK MCP real expiraban esperando respuesta

### Evidencia tecnica

Se inspecciono el SDK MCP instalado dentro de OpenClaw:

- `client/stdio.js` serializa con `JSON.stringify(message) + "\\n"`
- el transporte de lectura usa parseo por linea, no por `Content-Length`

Se hizo una reproduccion directa con el mismo SDK MCP de OpenClaw:

- antes del parche: timeout `MCP error -32001: Request timed out`
- despues del parche: conecta, lista tools y ejecuta `lucy_read_lines`

### Cambios hechos

Archivo modificado:

- `scripts/lucy_fs_mcp_server.py`

Archivo agregado:

- `scripts/test_lucy_fs_mcp_openclaw_compat.py`

Cambios funcionales del wrapper:

- soporte dual de transporte stdio:
  - modo legacy `Content-Length`
  - modo `ndjson` por linea
- autodeteccion del modo segun el primer mensaje recibido
- respuestas emitidas en el mismo modo detectado
- handlers de compatibilidad:
  - `ping`
  - `resources/list` -> lista vacia
  - `prompts/list` -> lista vacia
- notificaciones sin `id` se ignoran sin colgar
- debug a `stderr` solo si `LUCY_FS_MCP_DEBUG=1`

### Tests locales

#### 1. Wrapper original

- `python3 scripts/test_lucy_fs_mcp_server.py`
- resultado: `MCP wrapper test: OK`

#### 2. Compat OpenClaw-like

- `python3 scripts/test_lucy_fs_mcp_openclaw_compat.py`
- resultado: `MCP OpenClaw compat test: OK`

#### 3. Helper directa

- `python3 scripts/lucy_fs_readonly.py read_lines --path scripts/lucy_openclaw_bridge.py --start 138 --end 138`
- devuelve la linea real:
  - `def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):`

#### 4. Prueba con el SDK MCP real de OpenClaw

Se lanzo una prueba local con:

- `@modelcontextprotocol/sdk/dist/cjs/client/index.js`
- `@modelcontextprotocol/sdk/dist/cjs/client/stdio.js`

Resultado:

- `CONNECTED`
- `TOOLS` devuelve `lucy_find_files`, `lucy_grep_text`, `lucy_read_lines`
- `CALL` a `lucy_read_lines` devuelve la linea 138 correcta

Debug del server:

- `server starting`
- `detected io_mode=ndjson`
- `recv method='initialize'`
- `recv method='tools/list'`
- `recv method='tools/call'`

### Reintento con OpenClaw perfil aislado

Comando usado:

- `openclaw --profile lucy-fs-test agent --local --agent main ...`

Resultado del reintento:

- ya no aparece `bundle-mcp failed to start server`
- ya no aparece timeout MCP del server
- el `systemPromptReport` del run incluye las tools:
  - `lucy_find_files`
  - `lucy_grep_text`
  - `lucy_read_lines`

Interpretacion:

- el MCP ya arranca bajo OpenClaw
- OpenClaw llego al menos a descubrir/listar tools
- en este reintento el agente no devolvio payload util, asi que no queda
  evidencia material de un `tools/call` disparado desde el propio agente

### Diagnostico honesto

R34 resolvio el problema de compatibilidad que causaba el timeout de arranque
MCP. El bloqueo inicial del bundle MCP queda levantado.

Lo que queda pendiente no es el startup del server sino la invocacion efectiva
de la tool desde el agente OpenClaw en perfil aislado.

### Seguridad

- `~/.openclaw` principal: no tocado
- Telegram real: no tocado
- gateway principal: no reiniciado
- tokens/secretos: no impresos en documentacion
- cambios solo en scripts/docs del repo

### Proximo paso tecnico (R35)

Probar una invocacion local mas forzada y verificable desde OpenClaw en el
perfil aislado:

- prompt que exija usar `lucy_read_lines`
- verificacion externa de la linea exacta
- si hace falta, inspeccionar trazas del agente para confirmar `tools/call`

