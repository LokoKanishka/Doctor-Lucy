# OpenClaw Tool Integration Plan R30

Fecha: 2026-04-29

## Objetivo

Elegir la forma mas segura de exponer `scripts/lucy_fs_readonly.py` a OpenClaw
como herramienta controlada, sin tocar todavia Telegram real ni la configuracion
principal de OpenClaw.

## Estado de partida

- `scripts/lucy_fs_readonly.py` existe y funciona.
- R29B confirmo hardening contra `.env`, `n8n_data`, traversal, absolute paths,
  symlink externo y rangos excesivos.
- Telegram nativo OpenClaw funciona, pero no tiene filesystem confiable hoy.
- `mcp_config.json` del repo no esta montado en la config activa de OpenClaw.

## Evidencia OpenClaw

### CLI

Hallazgos del CLI:

- `openclaw mcp` existe y ofrece:
  - `list`
  - `show`
  - `set`
  - `unset`
  - `serve`
- `openclaw --dev` y `openclaw --profile <name>` existen para aislar estado y
  config bajo `~/.openclaw-dev` o `~/.openclaw-<name>`.
- `openclaw config file` usa la config activa de OpenClaw, no el
  `mcp_config.json` del repo.

### MCP activos hoy

Prueba local:

- `openclaw mcp list --json` -> `{}`
- `openclaw mcp show --json` -> `{}`

Conclusion:

- hoy no hay MCP servers configurados en la config activa del runtime OpenClaw.

### Codigo OpenClaw

Hallazgos relevantes:

- `mcp-cli-*.js` registra `mcp.command("serve")` con descripcion:
  `Expose OpenClaw channels over MCP stdio`
- `mcp-cli-*.js` usa `listConfiguredMcpServers()` y `loaded.mcpServers`
- `mcp-cli-*.js` muestra que `mcp set` acepta un JSON del estilo:
  `{"command":"...","args":[...]}`
- `agent-runner.runtime-*.js` consulta `workspaceAccess === "rw"` para ciertas
  operaciones del sandbox
- `config-schema-*.js` expone `commands.native`, `commands.nativeSkills` y
  `execApprovals`

Lectura tecnica:

- OpenClaw tiene un carril MCP nativo y separado.
- `commands.native` existe, pero es mas amplio y mas riesgoso que una tool
  especifica read-only.
- No hace falta tocar Telegram para probar un MCP/tool en entorno paralelo.

## Opciones

### Opcion A - MCP stdio local envolviendo `lucy_fs_readonly.py`

Idea:

- exponer `lucy_fs_readonly.py` a OpenClaw via un MCP server local por stdio.

Pros:

- coincide con el carril nativo que OpenClaw ya soporta (`mcp set/list/show`)
- la herramienta queda aislada como capability explicita
- permite pruebas en perfil paralelo o dev profile sin tocar la config principal
- mejor trazabilidad y menor superficie que shell libre

Contras:

- requiere un pequeño wrapper MCP alrededor del script
- hay que definir la interfaz MCP para `find_files`, `grep_text`, `read_lines`

Riesgo de write:

- bajo, si el wrapper solo invoca `lucy_fs_readonly.py` y no expone nada mas

### Opcion B - Native command skill

Idea:

- usar `commands.native` o `nativeSkills` para llamar al script directamente.

Pros:

- menos piezas que MCP
- podria ser rapido de probar localmente

Contras:

- mas cerca de exec generico
- mayor riesgo de desbordar hacia comando arbitrario si el wiring no queda
  extremadamente cerrado
- menos claro para auditoria futura que una tool MCP dedicada

Riesgo de comando arbitrario:

- medio/alto comparado con MCP, aunque el script en si sea seguro

### Opcion C - Bridge HTTP propio

Idea:

- levantar un endpoint local read-only que envuelva `lucy_fs_readonly.py`

Pros:

- desacoplado de MCP
- interfaz simple de testear

Contras:

- agrega otro servicio/puerto
- mas moving parts
- innecesario si OpenClaw ya soporta MCP stdio

Riesgo y overhead:

- mas overhead operativo sin una ventaja clara en este caso

## Recomendacion

Carril recomendado:

- **Opcion A: MCP stdio local**

Motivo:

- es el carril mas alineado con la arquitectura real de OpenClaw;
- permite integrar una capability concreta, no shell abierto;
- permite usar `--dev` o `--profile` para no tocar `~/.openclaw` principal;
- preserva mejor el aislamiento que `commands.native`.

No recomendado como primer paso:

- native command, porque abre una via mas ambigua hacia exec;
- bridge HTTP, porque agrega complejidad sin necesidad.

## R31 propuesto

Objetivo:

- probar la helper como capability OpenClaw en entorno aislado, sin Telegram real
  y sin tocar la config principal.

Forma segura:

1. usar `openclaw --dev` o `openclaw --profile lucy-fs-test`
2. configurar ahi un MCP server local temporal, no en el perfil principal
3. si hace falta, crear un wrapper MCP minimo que solo traduzca
   `find_files/grep_text/read_lines` hacia `lucy_fs_readonly.py`
4. probar por CLI local del perfil aislado
5. no conectar canales reales

## Criterios de aceptacion R31

- no toca `~/.openclaw/openclaw.json` principal
- no toca Telegram real
- el perfil paralelo lista el MCP configurado
- la tool devuelve rutas y lineas exactas
- sigue sin poder leer fuera del repo
- el experimento se puede borrar sin efecto lateral

## Rollback / no-op

- si el wrapper MCP queda confuso, no se enchufa nada al runtime principal
- si la tool expuesta por MCP no conserva exactamente los guardrails de R29/R29B,
  se aborta
- si OpenClaw en perfil paralelo no consume bien el MCP, no se avanza a Telegram

## Conclusion

La mejor integracion para esta helper no es shell nativo ni bridge HTTP. El
carril correcto es un MCP stdio local, pero probado primero en perfil paralelo o
`--dev`, sin tocar la configuracion principal ni Telegram real.
