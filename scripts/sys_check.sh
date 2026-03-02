#!/usr/bin/env bash
set -euo pipefail

# Doctor Lucy - System Health Check Script (Safe Opt-in wrapper)

FULL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --full) FULL=1 ;;
    -h|--help)
      echo "Uso: ./scripts/sys_check.sh [--full]"
      exit 0
      ;;
    *) echo "Arg desconocido: $1" >&2; exit 2 ;;
  esac
  shift
done

echo "--- Doctor Lucy: System Health Check ---"
date

if [ "$FULL" -eq 1 ]; then
  echo "[Modo FULL] Ejecutando auditoría con alcance de host (Docker & Network opt-in activado)..."
  ./scripts/auditoria.sh --docker --network
else
  echo "[Modo DEFAULT] Ejecutando auditoría de proyecto local segura..."
  ./scripts/auditoria.sh
fi

echo -e "\n--- End of Health Check ---"
