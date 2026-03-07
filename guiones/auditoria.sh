#!/usr/bin/env bash
set -euo pipefail

# Compat wrapper: mantiene retrocompatibilidad con rutas antiguas del repo.
# Ejecuta el script fuente en /scripts.
exec "$(dirname "$0")/../scripts/auditoria.sh" "$@"
