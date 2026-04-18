#!/bin/bash
# Doctor Lucy - Unified Voice Starter (Port 7854)
# Protege el puerto 7852 (Fusion) y se aisla en 7854.

PORT=7854
echo "[Lucy Voice] Iniciando sistema de voz en puerto $PORT..."

# 1. Limpieza segura y Forzado de CPU (Estabilidad Blackwell)
export CUDA_VISIBLE_DEVICES=""
if fuser $PORT/tcp >/dev/null 2>&1; then
    echo "[Lucy Voice] Puerto $PORT ocupado. Reiniciando proceso..."
    fuser -k $PORT/tcp || true
    sleep 2
fi

# 2. Definir rutas del entorno Estable (Blackwell-Ready)
# Nota: Se usa ebook2audiobook/python_env porque tiene Torch 2.7.1, compatible con SM_120.
VENV_PATH="/home/lucy-ubuntu/ebook2audiobook/python_env"
PYTHON_BIN="$VENV_PATH/bin/python3"
UVICORN_BIN="$VENV_PATH/bin/python3 -m uvicorn"
ALLTALK_DIR="/home/lucy-ubuntu/Archivo_proyectos/Taverna/Taverna-legacy/alltalk_tts"

# 3. Configurar librerías críticas para RTX 5090 (SM_120 / Torch 2.6)
export LD_LIBRARY_PATH="$VENV_PATH/lib/python3.11/site-packages/nvidia/cudnn/lib:$VENV_PATH/lib/python3.11/site-packages/nvidia/nccl/lib:$VENV_PATH/lib/python3.11/site-packages/nvidia/cublas/lib:$LD_LIBRARY_PATH"

# 4. Lanzamiento
cd "$ALLTALK_DIR"
echo "[Lucy Voice] Lanzando AllTalk en $PORT..."

# Usar nohup para persistencia y redirigir logs
nohup $PYTHON_BIN -m uvicorn tts_server:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers > "/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/voice_server.log" 2>&1 &

sleep 5
echo "[Lucy Voice] Servidor lanzado en segundo plano (PID: $!)."
echo "[Lucy Voice] Verificación: curl -s http://127.0.0.1:$PORT/api/ready"
