## R33 - Perfil aislado OpenClaw con modelo no-Anthropic

Fecha: 2026-04-29

### Objetivo

Desbloquear el perfil aislado `lucy-fs-test` para probar el MCP `lucy-fs-readonly`
sin usar Anthropic, sin tocar Telegram real y sin modificar la configuracion
principal de OpenClaw.

### Estado inicial

- Perfil principal con MCP vacio.
- Perfil aislado `lucy-fs-test` con `lucy-fs-readonly` registrado.
- R32 fallaba antes de llamar la tool por:
  - `No API key found for provider "anthropic"`

### Evidencia relevada

- `openclaw --profile lucy-fs-test config file` apunta a:
  - `~/.openclaw-lucy-fs-test/openclaw.json`
- El perfil aislado no tenia `agents.defaults.model`.
- El perfil aislado no tenia `agents.defaults.models`.
- El auth store aislado del agente `main` no tenia perfil `ollama:default`.
- La configuracion principal usa modelos locales/fallbacks no-Anthropic,
  incluyendo `ollama/qwen2.5-coder:14b`.
- El codigo de OpenClaw reconoce el marcador no secreto `ollama-local`
  para provider `ollama`.

### Cambios hechos solo en el perfil aislado

Antes de modificar, se hicieron backups:

- `~/.openclaw-lucy-fs-test/openclaw.json.r33-pre-model-20260429_212426.bak`
- `~/.openclaw-lucy-fs-test/agents/main/agent/auth-profiles.r33-pre-ollama-20260429_212700.bak`

Se ajusto solo `~/.openclaw-lucy-fs-test/openclaw.json` para agregar:

- `agents.defaults.model`
  - primary: `ollama/qwen2.5-coder:14b`
  - fallbacks:
    - `ollama/qwen3-coder:30b-a3b-q8_0`
    - `ollama/devstral-small-2:latest`
    - `google/gemini-2.5-flash`
- `agents.defaults.models`
  - incluye los modelos anteriores y `openai-codex/gpt-5.4`

Se ajusto solo el auth store aislado del agente `main` para agregar:

- perfil `ollama:default`
- provider `ollama`
- tipo `api_key`
- marcador no secreto local `ollama-local`

No se copiaron credenciales Anthropic ni se tocaron tokens del perfil principal.

### Resultado

La llamada aislada de OpenClaw dejo de fallar por Anthropic. El agente paso a usar:

- provider: `ollama`
- model: `qwen2.5-coder:14b`

La nueva falla observable fue distinta:

- `[bundle-mcp] failed to start server "lucy-fs-readonly"`
- `McpError: MCP error -32001: Request timed out`

Esto muestra que el bloqueo de R32 no era la tool ni el registro MCP, sino la
combinacion de provider/auth del perfil aislado. Eso ya quedo resuelto para el
entorno de prueba.

### Verificacion adicional

La helper local sigue funcionando por fuera de OpenClaw:

- `python3 scripts/lucy_fs_readonly.py read_lines --path scripts/lucy_openclaw_bridge.py --start 138 --end 138`
- devuelve la linea real:
  - `def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):`

### Seguridad

- `~/.openclaw` principal: no tocado
- Telegram real: no tocado
- gateway principal: no reiniciado
- tokens/secretos: no impresos en documentacion
- cambios limitados al perfil aislado con backup previo

### Diagnostico

R33 resolvio el bloqueo `anthropic` del perfil aislado y tambien el faltante de
auth para `ollama`. El siguiente cuello de botella real ya no es de modelo ni de
credenciales: es el arranque/handshake del MCP `lucy-fs-readonly` cuando OpenClaw
intenta levantarlo dentro del bundle MCP.

### Proximo paso sugerido (R34)

Investigar por que `lucy_fs_mcp_server.py` expira al ser lanzado por OpenClaw:

- framing/stdin-stdout del wrapper MCP
- handshake `initialize` esperado por OpenClaw
- tiempo de arranque y readiness
- posibles diferencias entre el test local del wrapper y el runner `bundle-mcp`

Rollback/no-op:

- restaurar backups del perfil aislado si hace falta volver al estado previo
- no hace falta tocar el perfil principal
