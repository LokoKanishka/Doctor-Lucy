#!/usr/bin/env bash
# ============================================================================
# lucy_exec.sh — Wrapper Universal Anti-Cartel Azul
# ============================================================================
# Toma un comando complejo (pipes, &&, grep, etc.), lo encapsula en un script
# temporal, lo ejecuta y lo limpia. Esto garantiza que el IDE solo vea un
# comando limpio: ./scripts/lucy_exec.sh "..."
#
# Uso:
#   ./scripts/lucy_exec.sh "cat /etc/os-release && uname -r && uptime"
#   ./scripts/lucy_exec.sh --file /ruta/a/script_temporal.sh
#
# Regla: El IDE nunca verá pipes ni cadenas largas. Solo verá la invocación
# de este wrapper, que es un comando simple y corto.
# ============================================================================

set -euo pipefail

SCRATCH_DIR="/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/.scratch"
mkdir -p "$SCRATCH_DIR"

# Modo archivo: ejecutar un script existente
if [[ "${1:-}" == "--file" ]]; then
    SCRIPT_PATH="${2:?Error: --file requiere una ruta al script}"
    if [[ ! -f "$SCRIPT_PATH" ]]; then
        echo "[lucy_exec] ERROR: Archivo no encontrado: $SCRIPT_PATH" >&2
        exit 1
    fi
    chmod +x "$SCRIPT_PATH"
    bash "$SCRIPT_PATH"
    exit $?
fi

# Modo inline: encapsular comando en script temporal
COMMAND="${1:?Error: Se requiere un comando como argumento}"
TEMP_SCRIPT="$SCRATCH_DIR/_exec_$(date +%s)_$$.sh"

cat > "$TEMP_SCRIPT" << 'HEREDOC_HEADER'
#!/usr/bin/env bash
set -euo pipefail
HEREDOC_HEADER

echo "$COMMAND" >> "$TEMP_SCRIPT"
chmod +x "$TEMP_SCRIPT"

# Ejecutar y capturar exit code
EXIT_CODE=0
bash "$TEMP_SCRIPT" || EXIT_CODE=$?

# Limpiar script temporal
rm -f "$TEMP_SCRIPT"

exit $EXIT_CODE
