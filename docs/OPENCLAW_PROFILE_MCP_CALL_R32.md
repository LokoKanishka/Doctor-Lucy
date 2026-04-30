# OpenClaw Profile MCP Call R32

Fecha: 2026-04-29

## Objetivo

Verificar si OpenClaw, usando el perfil aislado `lucy-fs-test`, puede consumir
el MCP `lucy-fs-readonly` y llamar tools reales sin tocar Telegram ni la config
principal.

## Configuracion MCP

Perfil principal:

- `openclaw mcp list --json` -> `{}`
- `openclaw mcp show --json` -> `{}`

Perfil aislado `lucy-fs-test`:

- `openclaw --profile lucy-fs-test mcp list --json` -> contiene
  `lucy-fs-readonly`
- `openclaw --profile lucy-fs-test mcp show --json` -> muestra:
  - `command: python3`
  - `args: [/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_fs_mcp_server.py]`

## Carril probado

Se reviso la ayuda de OpenClaw y el carril no interactivo mas claro fue:

- `openclaw --profile lucy-fs-test agent --local --json --message ...`

Intento ejecutado:

- pedido: usar `lucy_read_lines` para leer exactamente
  `scripts/lucy_openclaw_bridge.py` linea `138`

## Resultado

OpenClaw no llego a llamar la tool.

Fallo antes, con error de autenticacion del agente en el perfil aislado:

- `No API key found for provider "anthropic"`
- auth store faltante en:
  `/home/lucy-ubuntu/.openclaw-lucy-fs-test/agents/main/agent/auth-profiles.json`

Interpretacion:

- el MCP esta registrado en el perfil aislado;
- el carril CLI del agente existe;
- pero ese perfil aislado todavia no tiene el auth/runtime de agente necesario
  para ejecutar un turno local y, por lo tanto, no llego a consumir el MCP.

## Verificacion directa

Comparacion local directa con la helper:

- `python3 scripts/lucy_fs_readonly.py read_lines --path scripts/lucy_openclaw_bridge.py --start 138 --end 138`

Resultado exacto:

- linea 138:
  `def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):`

## Conclusión

R32 no prueba todavia el consumo real del MCP por OpenClaw.

Lo que si queda probado:

- el perfil principal sigue limpio;
- el perfil `lucy-fs-test` tiene el MCP correctamente registrado;
- el bloqueo actual no es de la tool MCP sino del runtime/auth del agente en el
  perfil aislado.

## Seguridad

- Telegram real: no tocado
- gateway principal: no reiniciado
- `~/.openclaw` principal: no tocado
- tokens: no impresos

## Próximo R33

Diseñar un carril alternativo para invocar el MCP desde OpenClaw en perfil
aislado sin tocar produccion.

Opciones a evaluar:

- inicializar auth/modelo local minimo en `lucy-fs-test` sin copiar secretos a
  ciegas;
- usar otro comando CLI/gateway call si existe un carril que no dependa del
  agente local completo;
- mantener `lucy-fs-test` como laboratorio y no acercarse todavia a Telegram.
