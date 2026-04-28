#!/bin/bash

if [ -z "${DOCTOR_LUCY_ALLOW_LEGACY_NIN_DEMON:-}" ]; then
    echo "LEGACY BLOCKED: start_demon.sh apunta a NIN y no debe ejecutarse desde Doctor-Lucy."
    echo "Para forzar ejecución, use: DOCTOR_LUCY_ALLOW_LEGACY_NIN_DEMON=1 ./scripts/start_demon.sh"
    exit 2
fi

echo "Deteniendo instancias previas de NiN..."
pkill -f "nin_demon.py" || true
sleep 1

echo "Lanzando NiN-Demon de forma 100% aislada..."
export PYTHONUNBUFFERED=1
nohup /home/lucy-ubuntu/Escritorio/NIN/.venv/bin/python3 /home/lucy-ubuntu/Escritorio/NIN/scripts/nin_demon.py \
    > /home/lucy-ubuntu/Escritorio/NIN/logs/nin_demon_output.log 2>&1 < /dev/null &
disown

echo "¡NiN-Demon lanzado exitosamente en el fondo! (Terminal liberada)"
