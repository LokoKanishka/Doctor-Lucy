#!/usr/bin/env bash
set -euo pipefail

# Compat wrapper: mantiene retrocompatibilidad con rutas antiguas del repo.
exec "$(dirname "$0")/../scripts/cleanup.sh" "$@"
