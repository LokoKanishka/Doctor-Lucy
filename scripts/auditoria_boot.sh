#!/usr/bin/env bash
# ============================================================================
# auditoria_boot.sh — Auditoría Rápida de Signos Vitales (Boot)
# ============================================================================
# Script pre-armado para el protocolo de arranque de Lucy.
# Se ejecuta como un solo comando limpio: ./scripts/auditoria_boot.sh
# Elimina la necesidad de cadenas complejas de bash durante el boot.
# ============================================================================

set -euo pipefail

echo "=========================================="
echo " AUDITORÍA BOOT — $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

echo ""
echo "--- OS & UPTIME ---"
cat /etc/os-release 2>/dev/null | grep -E "^(NAME|VERSION)=" || true
uname -r
uptime
hostname

echo ""
echo "--- CPU ---"
lscpu 2>/dev/null | grep -E "Model name|Architecture|CPU\(s\)|Thread|Socket" || true

echo ""
echo "--- RAM ---"
free -h

echo ""
echo "--- GPU (NVIDIA) ---"
nvidia-smi --query-gpu=name,memory.total,memory.used,driver_version,temperature.gpu,utilization.gpu --format=csv,noheader 2>/dev/null || echo "GPU no disponible"

echo ""
echo "--- DISCOS ---"
df -h --output=source,size,used,avail,pcent,target 2>/dev/null | head -15 || df -h | head -15

echo ""
echo "--- PUERTOS ACTIVOS (escuchando) ---"
ss -tulpn 2>/dev/null | head -30 || true

echo ""
echo "--- DOCKER ---"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker no disponible"

echo ""
echo "--- TOP 10 PROCESOS (por RAM) ---"
ps aux --sort=-%mem 2>/dev/null | head -11 || true

echo ""
echo "--- OLLAMA ---"
ollama list 2>/dev/null || echo "Ollama no disponible"

echo ""
echo "=========================================="
echo " FIN AUDITORÍA BOOT"
echo "=========================================="
