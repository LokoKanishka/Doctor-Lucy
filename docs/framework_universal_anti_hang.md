# Framework Antigravity: Regla Universal de Ejecución Asíncrona (Escudo Anti-Hang)

## El Problema Estructural
Los Agentes Inteligentes que operan dentro de entornos integrados (VS Code, Cursor, Antigravity, Roo) se comunican mediante pseudoterminales inyectadas (`shellIntegration-bash.sh` u otros envoltorios de RPC/IPC). El Agente, por diseño, bloquea su bucle cognitivo (mostrando el estado infinito *"Running..."*) hasta que la terminal confirme que el comando emitió un "Exit Code" y todos los canales de lectura de texto (STDOUT/STDERR) se hayan vaciado y cerrado.

Por lo tanto, si un Agente utiliza comandos convencionales como `&`, `nohup` o `bg` para levantar cualquier programa u orden que no termina matemáticamente en el instante o sigue generando texto (Ej: demonios, servidores locales Web, workers de cola, túneles ngrok), **la terminal anfitriona jamás cerrará los file descriptors y el Agente se colgará permanentemente esperando la conclusión**.

## La Regla Fundamental (Tolerancia Cero)
Para CUALQUIER Agente de Inteligencia Artificial que deba invocar un proceso largo o persistente en CUALQUIER proyecto:

**ESTÁ ESTRICTAMENTE PROHIBIDO** ejecutar comandos directos de lanzamiento en segundo plano en la línea de comandos principal. 

### El Único Patrón de Diseño Permitido (Disown & Nullification)
Si el Agente se ve en la obligación ineludible de levantar un servicio de fondo, DEBE crear un **script lanzador (wrapper script)** que contenga obligatoriamente la siguiente arquitectura de desvinculación asíncrona a nivel de kernel:

```bash
#!/bin/bash
# 1. Fuerza la salida sin buffer del lenguaje (Ej: Python o Node)
export PYTHONUNBUFFERED=1

# 2. Re-direccionamiento absoluto nulo y cierre estándar
# EXPLICACIÓN TÉCNICA:
# - < /dev/null : Evita que el programa padre espere input de la consola.
# - > logs.log 2>&1 : Redirige toda la salida estándar y errores a un archivo (desvinculando los descriptores de la UI).
# - & : Lo pasa al fondo en tiempo de ejecución de Bash.
comando_a_levantar > archivo_de_logs.log 2>&1 < /dev/null &

# 3. Corte de cordón umbilical del shell
# EXPLICACIÓN TÉCNICA: Elimina el trabajo de la tabla de procesos activos de este shell, 
# engañando a VS Code haciéndole creer que el comando finalizó instantáneamente con Exit Code 0.
disown

echo "Éxito: Terminal liberada."
```

## Mandato para Agentes Coder
Cuando asumas el control de un proyecto nuevo o recibas una orden de ejecutar un proceso que sospechas durará más de 3 segundos o no tiene final:
1. Jamás escribas el comando crudo en tu terminal.
2. Genera un archivo `.sh` aplicando el formato exacto detallado arriba.
3. Concede permisos de ejecución (`chmod +x`).
4. Invoca estrictamente ese Wrapper mediante `bash archivo.sh`.

Al aplicar este diseño agnóstico a cualquier stack tecnológico (Python, Node, Go, Bash), el entorno del Agente recuperará inmediatamente la voz y vista gráficas independientemente del ciclo vital subyacente del programa lanzado.
