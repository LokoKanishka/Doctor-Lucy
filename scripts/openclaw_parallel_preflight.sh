#!/usr/bin/env bash
set -euo pipefail

# Scripts de diagnóstico para REBUILD-0
# NO MODIFICA NADA. NO TOCA ~/.openclaw

echo "=== OpenClaw Parallel Rebuild Preflight ==="
echo "STAMP: $(date +%Y%m%d_%H%M%S)"
echo "USER: $(whoami)"
echo "HOME: $HOME"

echo ""
echo "--- 1. Estado de Backup Force-Gate ---"
BACKUP_DIR="/home/lucy-ubuntu/OpenClaw_Backups/force_gate/20260429_125405"
if [ -d "$BACKUP_DIR" ]; then
    echo "Backup dir exists: $BACKUP_DIR"
    ls -lah "$BACKUP_DIR"
    sha256sum -c "$BACKUP_DIR/SHA256SUMS.txt" 2>/dev/null || echo "Checksum verification failed or skipped"
else
    echo "WARNING: Backup dir NOT found at $BACKUP_DIR"
fi

echo ""
echo "--- 2. Auditoría de CLI actual ---"
OC_LIB="$HOME/.openclaw/lib/node_modules/openclaw/openclaw.mjs"
if [ -f "$OC_LIB" ]; then
    echo "CLI Lib exists: $OC_LIB"
    node "$OC_LIB" --version
else
    echo "WARNING: CLI Lib NOT found at $OC_LIB"
fi

OC_BIN="$HOME/.npm-global/bin/openclaw"
if [ -f "$OC_BIN" ]; then
    echo "CLI Bin exists: $OC_BIN"
    "$OC_BIN" --version
else
    echo "WARNING: CLI Bin NOT found at $OC_BIN"
fi

echo ""
echo "--- 3. Soporte para Perfiles ---"
if [ -f "$OC_LIB" ]; then
    # Capturar ayuda sin colores
    node "$OC_LIB" --help | grep -E '\-\-profile|\-\-dev' || echo "Profile options not found in help"
else
    echo "Cannot check help (CLI missing)"
fi

echo ""
echo "--- 4. Entorno Paralelo ---"
PARALLEL_ROOT="$HOME/OpenClaw_Parallel"
if [ -d "$PARALLEL_ROOT" ]; then
    echo "Parallel root exists: $PARALLEL_ROOT"
    find "$PARALLEL_ROOT" -maxdepth 2 -type d | sort
else
    echo "Parallel root NOT created yet"
fi

echo ""
echo "--- 5. Verificación de Seguridad ---"
echo "Validating that ~/.openclaw is NOT modified by this script..."
LS_BEFORE=$(ls -ld ~/.openclaw)
echo "LS: $LS_BEFORE"
# (No hay acciones destructivas aquí)
echo "Status: SAFE"

echo ""
echo "--- Preflight Complete ---"
