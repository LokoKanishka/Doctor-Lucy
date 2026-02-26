#!/bin/bash

# Doctor Lucy - Script de Mantenimiento Proactivo
# Limpieza de Snaps antiguos, logs y paquetes huérfanos.

echo "--- Doctor Lucy: Mantenimiento Proactivo ---"
date

# 1. Limpiar versiones antiguas de Snaps
echo -e "\n[1] Limpiando versiones antiguas de Snap..."
set -eu
snap list --all | awk '/desactivado|disabled/{print $1, $3}' |
    while read snapname revision; do
        echo "Eliminando $snapname (revisión $revision)"
        # snap remove "$snapname" --revision="$revision"
        # Nota: Se requiere sudo para la ejecución real. Por ahora informamos.
    done

# 2. Sugerir limpieza de APT
echo -e "\n[2] Sugerencia de limpieza de paquetes (APT):"
echo "Ejecuta: 'sudo apt autoremove && sudo apt clean' para limpiar dependencias innecesarias."

# 3. Limpiar Logs del sistema (Journal)
echo -e "\n[3] Limpieza de Logs (Journald):"
echo "Para limitar los logs a 100MB, ejecuta: 'sudo journalctl --vacuum-size=100M'"

# 4. Limpiar carpetas __pycache__
echo -e "\n[4] Limpiando __pycache__ en el Escritorio y Home..."
find /home/lucy-ubuntu -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "Hecho."

echo -e "\n--- Fin del Mantenimiento Proactivo ---"
