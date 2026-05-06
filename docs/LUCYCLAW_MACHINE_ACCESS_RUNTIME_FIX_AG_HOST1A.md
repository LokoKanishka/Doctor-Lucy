# LucyClaw Machine Access Runtime Fix (AG-HOST1A)

## Diagnóstico
Los comandos de acceso a la máquina (`/machine_downloads`, `/machine_ls`, `/machine_stat`) no estaban siendo despachados correctamente por el gateway de OpenClaw. Esto se debía a que el plugin utilizaba una estructura no estándar con múltiples archivos `.js` declarados en `package.json` pero sin un punto de entrada `index.js` que registrara los comandos explícitamente en la API de OpenClaw.

## Corrección Aplicada
1. **Unificación**: Se consolidaron los manejadores en un único archivo `index.js`.
2. **Registro Explícito**: Se implementó la función `register(api)` que utiliza `api.registerCommand` para dar de alta los tres comandos:
   - `machine_downloads` (sin argumentos)
   - `machine_ls` (acepta un argumento opcional de ruta)
   - `machine_stat` (requiere un argumento de ruta)
3. **Normalización**: Se ajustaron `package.json` y `openclaw.plugin.json` para seguir el estándar de plugins de OpenClaw.
4. **Sincronización de Commit**: Se normalizó el `target_commit` de AG-HOST1A a `4c19625` en toda la documentación y registros.

## Cómo Probar desde Telegram/OpenClaw
Una vez reiniciado el gateway, los siguientes comandos deberían funcionar directamente desde el cliente:

- `/machine_downloads`
- `/machine_ls ~/Descargas`
- `/machine_stat /home/lucy-ubuntu`

## Estado Actual
- El despacho al plugin está corregido.
- La lógica de acceso a archivos sigue siendo estrictamente de lectura y limitada a rutas seguras definidas en el wrapper Python.
- No se han agregado capacidades de escritura ni lectura de contenido de documentos en esta fase.
