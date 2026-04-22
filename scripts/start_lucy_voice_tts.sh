#!/bin/bash
# Doctor Lucy - Unified Voice Starter (Port 7854)
# Protege el puerto 7853 (Fusion Reader v2) y se aisla en 7854.

PORT="${LUCY_TTS_PORT:-7854}"
if [[ "$PORT" == "7853" || "$PORT" == "7852" ]]; then
    echo "[Lucy Voice] ERROR: puerto $PORT reservado/no asignado. Lucy usa 7854; Fusion usa 7853." >&2
    exit 2
fi
echo "[Lucy Voice] Iniciando sistema de voz en puerto $PORT..."

# 1. Limpieza segura y Forzado de CPU (Estabilidad Blackwell)
export CUDA_VISIBLE_DEVICES=""
if fuser $PORT/tcp >/dev/null 2>&1; then
    echo "[Lucy Voice] Puerto $PORT ocupado. Reiniciando proceso..."
    fuser -k $PORT/tcp || true
    sleep 2
fi

# 2. Definir rutas del entorno Estable (Blackwell-Ready)
# Nota: se usa el entorno de voz aislado de Antigravity; no tocar el entorno de Fusion.
VENV_PATH="${LUCY_VOICE_ENV:-/home/lucy-ubuntu/.gemini/antigravity/voice_env}"
PYTHON_BIN="$VENV_PATH/bin/python3"
ALLTALK_DIR="/home/lucy-ubuntu/Archivo_proyectos/Taverna/Taverna-legacy/alltalk_tts"
LOG_FILE="/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/voice_server.log"

# 3. Configurar librerías del entorno sin depender de rutas Python hardcodeadas.
SITE_PACKAGES="$("$PYTHON_BIN" - <<'PY'
import site
print(site.getsitepackages()[0])
PY
)"
VOICE_LIB_PATH=""
for libdir in "$SITE_PACKAGES"/nvidia/*/lib; do
    if [[ -d "$libdir" ]]; then
        VOICE_LIB_PATH="${VOICE_LIB_PATH:+$VOICE_LIB_PATH:}$libdir"
    fi
done
if [[ -n "$VOICE_LIB_PATH" ]]; then
    export LD_LIBRARY_PATH="$VOICE_LIB_PATH${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

# 4. Lanzamiento
cd "$ALLTALK_DIR"
echo "[Lucy Voice] Lanzando AllTalk en $PORT..."

# Usar setsid para persistencia y redirigir logs (PYTHONUNBUFFERED para logs en tiempo real)
export PYTHONUNBUFFERED=1
mkdir -p "$(dirname "$LOG_FILE")"
setsid "$PYTHON_BIN" -m uvicorn tts_server:app --host 127.0.0.1 --port "$PORT" --workers 1 --proxy-headers > "$LOG_FILE" 2>&1 < /dev/null &
SERVER_PID=$!

for i in $(seq 1 90); do
    if curl -fsS --max-time 2 "http://127.0.0.1:$PORT/api/ready" >/dev/null 2>&1; then
        echo "[Lucy Voice] Servidor listo en http://127.0.0.1:$PORT (PID: $SERVER_PID, ${i}s)."
        exit 0
    fi
    if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
        echo "[Lucy Voice] ERROR: el servidor terminó antes de estar listo. Últimas líneas:" >&2
        tail -n 80 "$LOG_FILE" >&2 || true
        exit 1
    fi
    sleep 1
done

echo "[Lucy Voice] ERROR: servidor lanzado (PID: $SERVER_PID) pero no respondió Ready en 90s." >&2
tail -n 80 "$LOG_FILE" >&2 || true
exit 1
