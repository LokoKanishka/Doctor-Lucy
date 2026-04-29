# OpenClaw Telegram Filesystem Tool Design R28

Fecha: 2026-04-29

## Objetivo

Diseñar una via segura para que LucyClaw/OpenClaw, desde Telegram nativo, pueda
buscar y leer archivos locales de forma real y verificable, empezando por modo
solo lectura dentro del repo `Doctor-Lucy`.

## Estado honesto de partida

Queda validado:

- Telegram nativo OpenClaw funciona.
- Gateway `18789` funciona.
- Bridge HTTP funciona.
- Daemons legacy estan apagados.
- No hay doble polling.

Pero filesystem confiable por Telegram no esta resuelto:

- R25: alucino rutas inexistentes.
- R26: leyo bien la primera linea de `scripts/lucy_openclaw_bridge.py`, pero
  alucino la linea de `delegate_mission`.
- R27: con pedido estricto de lineas exactas, respondio `pudo_leer: no`.

Conclusion operativa: hoy Telegram nativo conversa, pero no tiene lectura de
filesystem materialmente confiable.

## Evidencia tecnica

### Config OpenClaw activa

De `~/.openclaw/openclaw.json` y del CLI:

- `channels.telegram.enabled = true`
- `commands.native = auto`
- `commands.nativeSkills = auto`
- `agents.defaults.sandbox.mode = all`
- `agents.defaults.sandbox.workspaceAccess = none`
- `tools.deny = ["group:web", "browser"]`
- `session.dmScope = per-peer`

Lectura importante:

- Hay capacidad potencial de comandos nativos.
- El browser esta denegado.
- El workspace no esta expuesto libremente por sandbox.

### MCP del repo vs MCP real de OpenClaw

En el repo existe:

- `mcp_config.json` con `anthropic-filesystem` apuntando a
  `/home/lucy-ubuntu/Escritorio`.

Pero el runtime OpenClaw activo no lo esta usando hoy:

- `openclaw config file` apunta a `~/.openclaw/openclaw.json`.
- `openclaw mcp list` devolvio:
  `No MCP servers configured in /home/lucy-ubuntu/.openclaw/openclaw.json.`
- `openclaw mcp show` devolvio `{}` para `mcpServers`.
- El codigo del CLI `mcp` usa `loaded.mcpServers` desde el config activo.

Conclusion:

- `mcp_config.json` del repo no prueba integracion con Telegram nativo.
- A dia de hoy, el runtime OpenClaw/Telegram no tiene ningun MCP server
  configurado en su config activa.

### Señales de codigo OpenClaw

- El CLI trae comando `openclaw mcp` con `list/show/set/unset/serve`.
- El schema y runtime muestran soporte de sandbox, `workspaceAccess`,
  `commands.native` y `commands.nativeSkills`.
- El runtime tambien contiene logica de `exec approvals`, lo que sugiere que la
  via nativa de comandos existe, pero no equivale a filesystem confiable por si
  sola.

## Diagnostico

### Por que fallaron R25/R26/R27

La causa mas probable es combinada:

1. Telegram nativo no tiene una herramienta de filesystem realmente conectada.
2. `commands.native=auto` no garantiza que el agente elija o pueda usar shell
   para lecturas concretas en este contexto.
3. `workspaceAccess=none` hace improbable que el agente tenga acceso directo al
   repo por sandbox.
4. Sin herramienta material, el modelo rellena con inferencia o responde que no
   puede leer.

### Riesgo principal

Dar acceso a shell o filesystem sin una envoltura estricta podria abrir:

- lectura fuera del repo;
- escritura accidental;
- comandos arbitrarios;
- resultados no verificables desde Telegram.

## Opciones

### Opcion A - MCP filesystem read-only conectado a OpenClaw Telegram

Idea:

- Configurar un MCP server real en `~/.openclaw/openclaw.json` para filesystem,
  pero restringido a una raiz puntual.

Forma segura:

- ruta permitida inicial: solo `/home/lucy-ubuntu/Escritorio/doctor de lucy`
- sin rutas parent ni home completa;
- sin write tools expuestos al agente;
- verificar con `openclaw mcp list/show`;
- prueba material por Telegram pidiendo una lectura exacta y luego contrastando
  con Codex.

Ventajas:

- camino mas nativo con OpenClaw;
- reusable para Telegram y otros canales del gateway.

Riesgos:

- no esta claro en este tramo si `server-filesystem` ofrece modo read-only puro;
- si el server expone write ops por defecto, el riesgo sube;
- requiere tocar config activa de OpenClaw, que hoy esta fuera de alcance.

### Opcion B - wrapper propio `lucy_fs_readonly.py`

Idea:

- crear una herramienta minima, explicitamente read-only, y exponerla a OpenClaw
  como comando o MCP controlado.

Comandos permitidos:

- `find`
- `grep`
- `sed -n`
- opcionalmente `head`

Guardrails:

- base path obligatorio fijo al repo;
- denylist de `..`, glob libre, pipes, redirections, `~`, `/`, `.git`, binarios
  no permitidos;
- limite de profundidad;
- limite de cantidad de resultados;
- limite de bytes de salida;
- modo solo lectura por implementacion, no por prompt.

Ventajas:

- control fino y auditable;
- mas facil demostrar que no escribe;
- resultados verificables con pruebas exactas.

Riesgos:

- requiere integrar una tool nueva a OpenClaw;
- hay que decidir si entra por MCP, plugin o comando nativo.

### Opcion C - filesystem via Codex/bridge y Telegram solo chat

Idea:

- dejar Telegram como canal conversacional y seguir usando Codex/bridge para
  lecturas reales del repo.

Ventajas:

- camino mas seguro hoy;
- cero cambios en runtime Telegram;
- evita exponer host tools al bot.

Riesgos:

- no cumple la meta de “Lucy desde el celular” leyendo archivos por si misma;
- dependencia operativa de Codex o del bridge humano-supervisado.

## Recomendacion

La mejor via para avanzar es:

- **Recomendada: Opcion B**

Motivo:

- hoy no hay MCP filesystem conectado al runtime Telegram activo;
- Opcion A solo es aceptable si primero se prueba que el server puede quedar
  realmente read-only;
- un wrapper propio read-only permite definir superficie minima y verificable
  antes de conectar nada sensible.

Segunda mejor:

- Opcion A, solo despues de confirmar que OpenClaw puede montar un MCP
  filesystem sin exponer escritura.

No recomendada como solucion final:

- Opcion C, aunque sirve como fallback operativo.

## Experimento seguro R29

Objetivo:

- demostrar materialmente una lectura exacta por Telegram usando una herramienta
  conectada de verdad, no una respuesta inventada por prompt.

Propuesta:

1. No usar Telegram real todavia.
2. Diseñar la interfaz de una tool read-only:
   - `action=find_files`
   - `action=grep_text`
   - `action=read_lines`
3. Fijar base path al repo.
4. Probar localmente la tool fuera de Telegram con casos exactos.
5. Solo cuando devuelva lineas verificables, integrarla a OpenClaw.

Criterios de aceptacion:

- devuelve rutas reales existentes;
- devuelve lineas exactas con numero de linea correcto;
- no puede leer fuera del repo;
- no puede escribir;
- la salida es corta y estable;
- el resultado de Telegram coincide con verificacion local de Codex.

## Rollback / no-op

- Si la integracion no queda clara, no tocar el runtime Telegram.
- Si un MCP filesystem no puede garantizar solo lectura, no usarlo.
- Si la tool propuesta no demuestra limites fuertes por implementacion, no
  conectarla al bot.

## Conclusion

El problema no es solo de prompt. El runtime Telegram nativo de OpenClaw hoy no
tiene filesystem conectado de forma verificable. El `anthropic-filesystem` del
repo existe, pero no esta montado en la config activa del gateway. La forma mas
correcta y segura de avanzar es diseñar primero una herramienta de lectura
estrictamente read-only y recien despues conectarla al runtime Telegram.
