#!/bin/bash
echo "Deteniendo instancias previas de Doctora Lucy Demon..."
pkill -f "nin_demon.py" || true
sleep 1

echo "Lanzando Doctora Lucy Demon de forma 100% aislada..."
export PYTHONUNBUFFERED=1
nohup /home/lucy-ubuntu/Escritorio/NIN/.venv/bin/python3 /home/lucy-ubuntu/Escritorio/NIN/scripts/nin_demon.py \
    > /home/lucy-ubuntu/Escritorio/NIN/logs/nin_demon_output.log 2>&1 < /dev/null &
disown

echo "¡Doctora Lucy Demon lanzado exitosamente en el fondo! (Terminal liberada)"
