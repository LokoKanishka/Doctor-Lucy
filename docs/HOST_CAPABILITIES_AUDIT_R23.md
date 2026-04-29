# Host Capabilities Audit R23

Fecha: 2026-04-29

## Alcance

- Auditoria de solo lectura sobre capacidades host de LucyClaw/OpenClaw.
- No se modificaron archivos del sistema.
- No se ejecutaron acciones de escritorio.
- No se tocaron tokens ni `~/.openclaw`.
- No se reiniciaron servicios.

## Estado

- Rama: `memoria/bunker`.
- HEAD previo: `97db434 docs(lucy): record native telegram smoke`.
- `git status --short`: solo no trackeados previos ajenos a este tramo.

## Configuracion OpenClaw observada

Metadatos seguros leidos desde configuracion:

- Agentes configurados: `main`, `fusion-research`.
- `agents.defaults.sandbox.mode`: `all`.
- `agents.defaults.sandbox.workspaceAccess`: `none`.
- `commands.native`: `auto`.
- `commands.nativeSkills`: `auto`.
- `tools.deny`: `group:web`, `browser`.
- `session.dmScope`: `per-peer`.

Interpretacion conservadora:

- Browser/web: explicitamente restringido para este runtime.
- Desktop/X11: no aparece como capability habilitada en la configuracion leida.
- Shell/comandos nativos: hay indicio fuerte por `commands.native=auto`.
- Filesystem: no aparece habilitado de forma explicita en `openclaw.json`; el
  `workspaceAccess=none` sugiere que no hay acceso libre al workspace por esa via.

## Evidencia en el repo

Hallazgos relevantes de solo lectura:

- `mcp_config.json` define `anthropic-filesystem` apuntando a
  `/home/lucy-ubuntu/Escritorio`, lo que muestra una capacidad potencial de
  lectura/escritura por MCP fuera de OpenClaw Telegram nativo.
- `diagnostics/openclaw_audit_20260426.md` documenta:
  - sandbox en modo `all`;
  - web/browser deshabilitado via `tools.deny`.
- `scripts/nin_ojo.py` usa `pyautogui.screenshot()`, lo que prueba que en el repo
  existe codigo legacy para captura de pantalla.
- No se encontro evidencia en la configuracion auditada de que Telegram nativo
  tenga hoy habilitado control de mouse, teclado o ventanas.

## Prueba read-only por bridge

Consulta enviada al bridge:

```text
Decime si tenes herramientas para listar archivos locales. No ejecutes nada; solo responde capabilities.
```

Respuesta:

```json
{
  "name": "capabilities",
  "arguments": {
    "read": true,
    "exec": true,
    "browser": false,
    "desktop": false
  }
}
```

Interpretacion:

- Afirma poder leer archivos locales: si.
- Afirma poder ejecutar comandos: si.
- Afirma browser: no.
- Afirma desktop/X11: no.

## Limites de la evidencia

- `read=true` y `exec=true` son una declaracion del agente via bridge, no una
  prueba material de ejecucion real en este tramo.
- La configuracion de OpenClaw respalda fuertemente `browser=false`.
- La configuracion y el repo no muestran una habilitacion actual de desktop/X11
  para Telegram nativo, aunque existan scripts legacy relacionados.
- La combinacion `sandbox.mode=all` con `workspaceAccess=none` sugiere que el
  acceso a archivos no es libre por workspace y podria depender de herramientas
  nativas o MCPs puntuales.

## Conclusion

Estado mas probable hoy para LucyClaw/OpenClaw via Telegram nativo:

- Filesystem: posible, pero todavia sin prueba material en este tramo.
- Shell: posible, con indicio fuerte de configuracion.
- Desktop/X11: no habilitado en la superficie auditada.
- Browser/web: deshabilitado.
- Sandbox: presente, con `workspaceAccess=none`.

## Proximo paso recomendado

- Si se quiere validar filesystem seguro: prueba R24 buscando un archivo por nombre
  en una ruta acotada y solo lectura.
- Si se quiere validar shell seguro: prueba R24 con un comando read-only limitado,
  por ejemplo `find` o `ls` sobre un directorio controlado.
- Si se quiere explorar desktop/X11: dejarlo para despues y empezar por captura
  de pantalla, nunca mouse o teclado.
