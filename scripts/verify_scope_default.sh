#!/usr/bin/env bash
set -euo pipefail

# Módulo de Validación Automática de Fronteras de Doctor Lucy
# Garantiza que la auditoría por defecto NO intente curiosear docker ni puertos host-wide.

OUT="diagnostics/_scope_test.md"
mkdir -p diagnostics

# 1. Ejecutamos la auditoría con los parámetros por defecto (Seguros)
./scripts/auditoria.sh --out "$OUT" --timeout 3 >/dev/null

# 2. Buscamos cualquier intrusión en el reporte salvado
if grep -qE "docker ps|ss -tulpn|mismatching encryption|n8n" "$OUT" 2>/dev/null; then
  echo "FAIL: El reporte default contiene trazas fuera de jurisdicción o comandos host-wide no autorizados."
  echo "Revise $OUT"
  exit 1
fi

echo "OK: Scope default limpio (Sin invasiones globales a Docker, Network o n8n)."
