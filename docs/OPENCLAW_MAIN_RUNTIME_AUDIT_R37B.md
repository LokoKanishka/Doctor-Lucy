## R37B - Auditoria solo lectura del OpenClaw principal

Fecha: 2026-04-29

### Alcance

Auditoria de la instalacion principal real de OpenClaw/LucyClaw en modo solo
lectura.

Proteccion explicita:

- Doctora Lucy no se toca
- memoria no se toca
- n8n no se toca
- boveda no se toca
- personalidad no se toca
- scripts centrales ajenos a OpenClaw no se tocan
- daemons legacy no se tocan

### Estado general

- OpenClaw version: `2026.3.28 (f9b1079)`
- config principal: `~/.openclaw/openclaw.json`
- servicio principal:
  - `openclaw-gateway.service`
  - activo y corriendo
- puerto activo:
  - `127.0.0.1:18789`
- no se vio listener en `18790`

### Modelo y providers del principal

`openclaw models status --json` y `models list --json` muestran:

- primary:
  - `ollama/qwen2.5-coder:14b`
- fallbacks:
  - `ollama/qwen3-coder:30b-a3b-q8_0`
  - `ollama/devstral-small-2:latest`
  - `google/gemini-2.5-flash`
- modelos configurados y visibles:
  - `ollama/qwen2.5-coder:14b`
  - `ollama/qwen3-coder:30b-a3b-q8_0`
  - `ollama/devstral-small-2:latest`
  - `google/gemini-2.5-flash`
  - `openai-codex/gpt-5.4`

Auth disponible sin exponer secretos:

- Anthropic: presente
- Google/Gemini: presente
- Ollama local: presente (`marker(ollama-local)`)
- OpenAI: presente
- OpenAI-Codex: presente via OAuth

Conclusion de auth:

- el principal si tiene OpenAI/Codex disponible
- el principal si tiene Gemini disponible
- pero el runtime principal hoy sigue eligiendo Ollama local como default real

### Telegram principal

Config segura leida desde `~/.openclaw/openclaw.json`:

- `telegram_enabled = true`
- `dmPolicy = pairing`
- `groupPolicy = allowlist`
- token configurado: si
- `tokenFile`: no

Canal:

- Telegram nativo esta habilitado
- el servicio principal estaba arrancando el provider Telegram
- la prueba real previa ya habia respondido OK

Pairing:

- `openclaw pairing list telegram`
- resultado:
  - no habia pairing requests pendientes

### MCP y tools del principal

CLI oficial:

- `openclaw mcp list --json` -> `{}`
- `openclaw mcp show --json` -> `{}`

Interpretacion:

- el principal no tiene MCP cliente registrado hoy
- no hay filesystem/tool MCP montado en el runtime principal

Config segura:

- `tools.deny`:
  - `group:web`
  - `browser`
- `commands.native = auto`
- `commands.nativeSkills = auto`
- sandbox default:
  - `mode = all`
  - `workspaceAccess = none`

### Logs relevantes

Los logs recientes muestran varias cosas importantes:

1. El principal usa de hecho:
   - `ollama/qwen2.5-coder:14b`

2. Hay advertencias repetidas de contexto bajo:
   - `ctx=16000 (warn<32000)`

3. Hubo conflictos historicos de Telegram long polling:
   - `getUpdates conflict`
   - consistente con una etapa previa donde coexistio otro poller

4. Hubo fallas/redes/fallbacks en Telegram:
   - `sticky IPv4-only dispatcher`
   - `ENETUNREACH`

5. Hubo un problema de sandbox/container en una corrida:
   - nombre de contenedor ya en uso

6. Tambien hubo decisiones de fallback entre:
   - `qwen2.5-coder`
   - `qwen3-coder`
   - `devstral-small-2`
   - `gemini-2.5-flash`

### Diferencia con `lucy-fs-test`

`lucy-fs-test` fue un laboratorio aislado para:

- registrar el MCP `lucy-fs-readonly`
- probar el wrapper MCP
- separar el problema de provider/auth del problema de tool use

Diferencia clave:

- `lucy-fs-test` si tenia el MCP registrado
- el principal hoy tiene MCP vacio

Otra diferencia importante:

- el laboratorio desvio hacia Ollama porque el principal ya estaba configurado
  asi y la ruta embedded local heredo ese default
- eso no significa que sea la mejor ruta para tool calling confiable

### Conclusion honesta

El principal no parece necesitar una reinstalacion total de OpenClaw.

Estado real:

- Telegram nativo principal: funcional
- auth principal: amplia, incluyendo Codex y Gemini
- modelo default principal: Ollama local
- MCP principal: vacio

Problema estructural mas probable:

- no falta OpenClaw
- falta alinear el runtime principal con un provider/modelo mas confiable para
  tool use y decidir si montar un MCP read-only en el principal

### Recomendacion

De las opciones pedidas, la recomendacion es:

- **A) reparar config principal**

Concretamente, cuando llegue el momento de intervenir:

1. backup de `~/.openclaw/openclaw.json`
2. diff claro de modelo/provider default
3. decidir si el principal debe dejar de usar `ollama/qwen2.5-coder:14b`
4. evaluar montar MCP read-only solo despues de eso

No recomiendo hoy:

- `C) reset/reinstall solo OpenClaw`

porque la instalacion principal:

- arranca
- atiende Telegram
- tiene auth funcional
- expone modelos validos

La falla no parece ser de instalacion rota sino de configuracion/ruta de modelo.

Si se quiere extrema prudencia antes de tocar el principal:

- se puede considerar `D) pausar`

pero a nivel tecnico el siguiente paso razonable no es reinstall, sino reparar
la configuracion principal de OpenClaw de forma acotada.

