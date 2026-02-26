#!/bin/bash

# Doctor Lucy - Script de Auditoría de Seguridad
# Revisa puertos, servicios y estado de "salud" defensiva.

echo "--- Doctor Lucy: Reporte de Seguridad ---"
date

echo -e "\n[1] Puertos Abiertos (Escuchando):"
# Filtramos para mostrar solo los puertos IPv4 significativos
ss -tulpn | grep LISTEN | grep -v "127.0.0.1" | awk '{print $5, $7}' | sort -u
echo "Nota: Puertos como 47989 (Sunshine) y 11434 (Ollama) son normales según tu configuración."

echo -e "\n[2] Estado del Firewall (UFW):"
if command -v ufw >/dev/null; then
    echo "UFW está instalado. Para ver el estado detallado usa 'sudo ufw status'."
else
    echo "ADVERTENCIA: UFW (Firewall) no detectado o no accesible."
fi

echo -e "\n[3] Antivirus (ClamAV):"
if command -v clamscan >/dev/null; then
    echo "ClamAV está instalado."
else
    echo "ClamAV no está instalado. En Linux es opcional pero se puede instalar si deseas escaneos periódicos."
fi

echo -e "\n[4] Integridad de Usuarios:"
who
echo "Usuarios con procesos activos (Top 3):"
ps -eo user | sort | uniq -c | sort -nr | head -n 3

echo -e "\n--- Fin del Reporte de Seguridad ---"
