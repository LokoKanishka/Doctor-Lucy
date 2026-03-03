# Protocolo Anti-Hang para Agentes AI (VS Code)

**Problema Detectado:**
Cualquier Agente AI que opere dentro de la terminal integrada de VS Code (Antigravity, Cursor, etc.) hereda el entorno `ANTIGRAVITY_AGENT=1`. Esto significa que la terminal **jamas se liberará** si el agente levanta un proceso en segundo plano (ej. un servidor de Python, n8n, demonios) que mantenga abiertos los descriptores de salida (`stdout`/`stderr`), incluso si usa `&` o `nohup`.
Esto resulta en un estado de "Running..." infinito en la interfaz del usuario.

**La Regla de Oro (Directiva del Doctor Lucy):**
> 🚫 **NUNCA** uses comandos directos como `nohup python3 script.py &` para levantar servidores o demonios persistentes.
> ✅ **SIEMPRE** debes usar un script lanzador (launcher) que encapsule la salida aislando los file descriptors de la terminal del agente.

## Plantilla Universal del Lanzador (.sh)
Siempre que necesites dejar un proceso vivo y devolverle el control a la interfaz de chat del usuario en menos de 1 segundo, debes crear un archivo `.sh` con **esta estructura exacta** y luego ejecutarlo con `bash script.sh`:

```bash
#!/bin/bash
export PYTHONUNBUFFERED=1

# 1. Matar instancias previas si aplica
pkill -f "nombre_del_script.py" || true
sleep 1

# 2. La Magia: Redirigir salidas y cerrar el canal de entrada (< /dev/null)
nohup /usr/bin/python3 /ruta/absoluta/al/nombre_del_script.py \
    > /ruta/absoluta/a/los/logs/output.log 2>&1 < /dev/null &

# 3. Desvincular del shell padre
disown

echo "OK: Proceso lanzado y terminal liberada."
```

## Por qué funciona:
- `< /dev/null`: Engaña al proceso para que cierre su canal de espera de Input, soltando el enganche de VS Code.
- `2>&1`: Unifica errores y consola al archivo `.log`.
- `disown`: Le dice al shell que el proceso ya no es su hijo, por lo que no espera su cierre.

Si sigues este protocolo, tu panel de Agente jamás volverá a quedarse "clavado".
