## R35 - Tool call MCP desde OpenClaw en perfil aislado

Fecha: 2026-04-29

### Objetivo

Obtener evidencia material de que el agente OpenClaw en el perfil aislado
`lucy-fs-test` puede invocar la tool MCP `lucy_read_lines` y devolver una linea
exacta del repo.

### Preflight

Wrapper y helper verificados antes de la prueba:

- `python3 -m py_compile scripts/lucy_fs_readonly.py scripts/lucy_fs_mcp_server.py`
- `python3 scripts/test_lucy_fs_mcp_server.py` -> `MCP wrapper test: OK`
- `python3 scripts/test_lucy_fs_mcp_openclaw_compat.py` -> `MCP OpenClaw compat test: OK`

Perfil aislado confirmado:

- `openclaw --profile lucy-fs-test mcp list --json`
- `openclaw --profile lucy-fs-test mcp show --json`

Resultado:

- `lucy-fs-readonly` sigue registrado
- command: `python3`
- args:
  - `/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_fs_mcp_server.py`

### Intentos A/B/C

#### Variante A - mandato directo

Prompt:

- usar obligatoriamente `lucy_read_lines`
- devolver solo el JSON de la tool

Resultado:

- `payloads: []`
- sin error MCP
- el `systemPromptReport` incluye la tool `lucy_read_lines`
- no hay evidencia de `tools/call`

#### Variante B - instruccion menos rígida

Prompt:

- llamar `lucy_read_lines`
- incluir `path`, `line`, `text`

Resultado:

- `payloads: []`
- sin error MCP
- el `systemPromptReport` incluye la tool `lucy_read_lines`
- no hay evidencia de `tools/call`

#### Variante C - modo verificacion

Prompt:

- si no puede llamar tools, responder `TOOL_NOT_CALLED`
- si puede, llamar `lucy_read_lines`

Resultado:

- el agente devolvio:
  - `TOOL_NOT_CALLED`
- esto es la señal mas clara del tramo

### Evidencia relevada

En los artefactos temporales:

- `grep` encontro `lucy_read_lines` en el `systemPromptReport` de A/B/C
- no aparecio evidencia de:
  - `tools/call`
  - resultado JSON de la tool dentro de los payloads del agente
  - linea 138 devuelta por el agente OpenClaw

Evidencia directa de referencia:

- `python3 scripts/lucy_fs_readonly.py read_lines --path scripts/lucy_openclaw_bridge.py --start 138 --end 138`
- devuelve correctamente:
  - path: `scripts/lucy_openclaw_bridge.py`
  - line: `138`
  - text: `def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):`

### Diagnostico

Conclusiones honestas de R35:

1. El MCP arranca en OpenClaw perfil aislado.
2. La tool `lucy_read_lines` esta visible para el agente.
3. El agente local con `ollama/qwen2.5-coder:14b` no llego a invocar la tool en
   estas tres variantes.
4. El problema ya no parece ser:
   - registro MCP
   - startup del wrapper
   - compatibilidad de transporte
5. El cuello actual parece estar en uno de estos frentes:
   - comportamiento del modelo local frente a tools
   - modo de ejecucion del comando `agent --local`
   - politica interna de tool use / approvals / prompting del agente

### Flags y pistas encontradas

`openclaw agent --help` mostro opciones utiles pero no una bandera obvia para
forzar tool use:

- `--json`
- `--local`
- `--thinking <level>`

No aparecio en esa ayuda corta una opcion explicita tipo:

- `--force-tools`
- `--tool-choice required`
- `--mcp required`

### Seguridad

- `~/.openclaw` principal: no tocado
- Telegram real: no tocado
- gateway principal: no reiniciado
- tokens/secretos: no impresos
- sin cambios de config principal

### Proximo paso sugerido (R36)

Investigar como OpenClaw decide o habilita tool use con ese modelo local:

- flags adicionales de `agent`, `run` o modo no interactivo
- posibles settings de approvals/permisos para tools
- si existe un endpoint o comando que fuerce tool use
- si hace falta probar con otro modelo ya configurado en el perfil aislado, sin
  tocar el principal

