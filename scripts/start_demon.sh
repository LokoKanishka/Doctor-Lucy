#!/bin/bash
echo "Deteniendo instancias previas de NiN..."
pkill -f "nin_demon.py" || true
sleep 1

echo "Lanzando NiN-Demon de forma 100% aislada..."
export PYTHONUNBUFFERED=1
nohup /usr/bin/python3 /home/lucy-ubuntu/Escritorio/NIN/scripts/nin_demon.py \
    > /home/lucy-ubuntu/Escritorio/NIN/logs/nin_demon_output.log 2>&1 < /dev/null &
disown

echo "¡NiN-Demon lanzado exitosamente en el fondo! (Terminal liberada)"
