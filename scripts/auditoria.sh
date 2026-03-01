#!/bin/bash
set -euo pipefail

# Doctor Lucy - Auditoría rápida del sistema
# Genera un informe en Markdown con datos de salud y seguridad básicos.

OUTPUT_FILE="${1:-auditoria_sistema.md}"
NOW="$(date '+%Y-%m-%d %H:%M:%S %Z')"
HOST="$(hostname)"
USER_NAME="$(whoami)"
KERNEL="$(uname -r)"
OS_PRETTY="$(grep '^PRETTY_NAME=' /etc/os-release 2>/dev/null | cut -d= -f2- | tr -d '"')"

TMP_PORTS="$(mktemp)"
TMP_DOCKER="$(mktemp)"
trap 'rm -f "$TMP_PORTS" "$TMP_DOCKER"' EXIT

{
  echo "# 🔍 Auditoría del Sistema — Doctor Lucy"
  echo "**Última actualización:** ${NOW}"
  echo "**Host:** ${HOST} | **Usuario:** ${USER_NAME}"
  echo
  echo "---"
  echo
  echo "## 💻 Estado del Sistema"
  echo "- **OS:** ${OS_PRETTY:-No detectado}"
  echo "- **Kernel:** ${KERNEL}"
  echo "- **Uptime:** $(uptime -p 2>/dev/null || echo 'No disponible')"
  echo "- **Carga promedio:** $(uptime | awk -F'load average: ' '{print $2}' 2>/dev/null || echo 'No disponible')"
  echo
  echo "## ⚙️ Recursos"
  echo "- **Memoria (free -h):**"
  echo '```'
  free -h || true
  echo '```'
  echo "- **Disco raíz (df -h /):**"
  echo '```'
  df -h / || true
  echo '```'
  echo
  echo "## 🔒 Seguridad básica"
  echo "### Puertos en escucha no-localhost"
  if ss -tulpn 2>/dev/null | awk 'NR>1 {print $1,$5,$7}' | grep -E '0\.0\.0\.0|\[::\]' > "$TMP_PORTS"; then
    echo '```'
    cat "$TMP_PORTS"
    echo '```'
  else
    echo "No se detectaron puertos públicos en escucha."
  fi
  echo
  echo "### Firewall"
  if command -v ufw >/dev/null 2>&1; then
    echo "- UFW instalado. Estado:"
    echo '```'
    ufw status 2>/dev/null || echo "Sin permisos para consultar ufw status"
    echo '```'
  else
    echo "- UFW no instalado."
  fi
  echo
  echo "### Antivirus"
  if command -v clamscan >/dev/null 2>&1; then
    echo "- ClamAV detectado (clamscan disponible)."
  else
    echo "- ClamAV no detectado."
  fi
  echo
  echo "## 🐳 Docker"
  if command -v docker >/dev/null 2>&1; then
    if docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' > "$TMP_DOCKER" 2>/dev/null; then
      echo '```'
      cat "$TMP_DOCKER"
      echo '```'
    else
      echo "Docker instalado pero sin permisos para listar contenedores."
    fi
  else
    echo "Docker no instalado."
  fi
  echo
  echo "## ✅ Recomendaciones rápidas"
  echo "- Revisar puertos expuestos a 0.0.0.0 / [::] y cerrar los no necesarios."
  echo "- Si hay poco espacio en /, correr limpieza de paquetes y cachés."
  echo "- Validar que servicios críticos de Docker estén en estado healthy."
  echo
  echo "---"
  echo "*Auditoría generada automáticamente por scripts/auditoria.sh*"
} > "$OUTPUT_FILE"

echo "Reporte generado en: $OUTPUT_FILE"
