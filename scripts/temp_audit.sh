#!/bin/bash
echo "=== OS INFO ==="
cat /etc/os-release | grep PRETTY_NAME
uname -r
uptime -p
hostname

echo "=== CPU & RAM ==="
lscpu | grep -E "Model name|Architecture|CPU\(s\):|Thread|Socket|MHz|Cache"
free -h

echo "=== GPU ==="
nvidia-smi --query-gpu=name,memory.total,driver_version,temperature.gpu,utilization.gpu --format=csv,noheader 2>/dev/null || echo "GPU no disponible"

echo "=== DISCOS ==="
df -h | grep -E "^/dev|tmpfs"

echo "=== SERVICIOS ==="
systemctl is-active docker n8n postgresql alltalk || true

echo "=== DOCKER ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null

echo "=== OLLAMA ==="
ollama list 2>/dev/null || echo "Ollama inactivo"

echo "=== PROCESOS PESADOS ==="
ps aux --sort=-%mem | head -10 | awk '{print $2, $3, $4, $11}'
