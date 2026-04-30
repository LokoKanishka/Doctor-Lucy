## R36 - Politica de tool use en OpenClaw perfil aislado

Fecha: 2026-04-29

### Objetivo

Entender por que `openclaw --profile lucy-fs-test agent --local` ve tools MCP
pero no las invoca, y determinar si falta una policy, approval, flag CLI o
modelo compatible.

### Estado relevado

Perfil aislado:

- `agents.defaults.model.primary`: `ollama/qwen2.5-coder:14b`
- fallbacks:
  - `ollama/qwen3-coder:30b-a3b-q8_0`
  - `ollama/devstral-small-2:latest`
  - `google/gemini-2.5-flash`
- `commands.native`: `auto`
- `commands.nativeSkills`: `auto`
- `tools`: ausente en config aislada
- `mcpServers`: ausente en config aislada base

Nota:

- el MCP `lucy-fs-readonly` si existe y se ve via `openclaw mcp list/show`
- no hay un bloque `tools` en la config aislada que niegue o perfile tools

### Hallazgos de codigo OpenClaw

#### 1. Las tools no estan globalmente deshabilitadas

En el runtime embebido:

- `supportsModelTools(model)` devuelve falso solo si:
  - `model.compat.supportsTools === false`

Codigo observado:

- `function supportsModelTools(model) { return ...?.supportsTools !== false; }`

Y luego:

- `const toolsEnabled = supportsModelTools(runtimeModel);`
- si eso da true, OpenClaw monta:
  - core tools
  - bundle MCP tools
  - bundle LSP tools

#### 2. El MCP realmente se monta como tool usable

En `bundle-mcp`:

- OpenClaw crea `StdioClientTransport`
- hace `await client.connect(transport)`
- hace `const listedTools = await listAllTools(client)`
- por cada tool registrada, crea un `execute(...)` que llama:
  - `client.callTool(...)`

O sea:

- no es un decorado visual
- las tools MCP listadas son ejecutables si el agente decide llamarlas

#### 3. No aparece una policy de approvals bloqueando tool use

Se reviso `resolveEffectiveToolPolicy(...)`:

- lee `config.tools`
- lee `agent.tools`
- lee `tools.byProvider`
- arma `profile` y `providerProfile`

Pero en `lucy-fs-test`:

- `config.tools` no existe
- `agent.tools` no existe en la config aislada auditada

Conclusion:

- no hay evidencia de una policy explicita bloqueando `lucy_read_lines`

#### 4. Los modelos locales relevados no vienen marcados como no compatibles

En `~/.openclaw-lucy-fs-test/agents/main/agent/models.json`:

- `qwen2.5-coder:14b`
- `qwen3-coder:30b-a3b-q8_0`
- `devstral-small-2:latest`

aparecen sin bloque `compat.supportsTools: false`.

Eso significa que, para OpenClaw:

- no estan explicitamente inhabilitados para tools

### CLI y modos

#### `agent --help`

Flags observados:

- `--local`
- `--json`
- `--thinking`
- `--timeout`
- `--agent`
- `--session-id`

No aparece:

- `--model`
- `--force-tools`
- `--tool-choice required`
- `--mcp required`

#### `run --help`

No existe un subcomando `run` util para agente; `openclaw run --help` cae en la
ayuda raiz.

#### `chat --help`

No aporto un carril CLI distinto para forzar tools; tambien redirige al arbol
general.

#### `gateway --help`

Confirma que sin `--local` el comando `agent` pasa por Gateway.

Por seguridad no se probo modo no-local en este tramo porque:

- tocaria el gateway en uso
- eso se sale del aislamiento pedido para `lucy-fs-test`

### Modelos y soporte practico

`openclaw models list --json --local` en el perfil aislado mostro:

- `ollama/qwen2.5-coder:14b`
- `ollama/qwen3-coder:30b-a3b-q8_0`
- `ollama/devstral-small-2:latest`

Todos:

- locales
- disponibles
- configurados

Pero `agent --help` no ofrece `--model`, asi que no hay override por corrida
limpio para comparar modelos sin mutar el perfil aislado.

Siguiendo la regla del tramo:

- no se improviso un cambio persistente de modelo

### Diagnostico

La mejor explicacion actual es:

1. OpenClaw si entrega las tools al agente local.
2. No hay evidencia de bloqueo por approvals o policy explicita.
3. El modelo local `ollama/qwen2.5-coder:14b` no esta invocando tools en este
   modo de ejecucion.
4. Como no hay `--tool-choice required` ni `--model` en el CLI de `agent`,
   estamos dependiendo de la obediencia del modelo.

### Solucion probable

R37 deberia ir por uno de estos caminos:

1. encontrar un modo de OpenClaw que fuerce tool use
2. usar otro modelo local mas proclive a tool calling
3. cambiar temporalmente solo el perfil aislado, con backup previo, a un modelo
   ya disponible, si el experimento lo justifica
4. investigar si existe otro comando/runner interno que acepte `toolChoice:
   required`

### Riesgo

El riesgo principal ya no es seguridad del helper ni del MCP.

El riesgo ahora es metodologico:

- seguir gastando rondas en prompts sobre un runner/modelo que no tiene un
  mecanismo CLI claro para forzar tool calling

### Seguridad

- `~/.openclaw` principal: no tocado
- Telegram real: no tocado
- gateway principal: no reiniciado
- tokens/secretos: no impresos en documentacion
- sin cambios en config principal

