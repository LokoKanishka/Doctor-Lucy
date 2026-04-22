#!/bin/bash
# ============================================================
# switch_agent.sh — Conmutador de roles del sistema multi-agente
# Uso: ./scripts/switch_agent.sh <nombre_del_rol>
# Roles válidos: n8n_researcher, doctora_lucy
# ============================================================

WORKSPACE="/home/lucy-ubuntu/Escritorio/doctor de lucy"
ACTIVE_ROLE_FILE="$WORKSPACE/.agents/ACTIVE_ROLE"
ROLES_DIR="$WORKSPACE/.agents/roles"
LOG_FILE="$WORKSPACE/n8n_data/agent_transitions.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Mapeo de nombres cortos a archivos de rol
declare -A ROLE_MAP
ROLE_MAP[n8n_researcher]="LUCY_N8N_RESEARCHER.md"
ROLE_MAP[supervisor_fusion]="LUCY_SUPERVISOR_FUSION.md"

# --- Validación de argumento ---
if [ -z "$1" ]; then
    echo "[switch_agent] ERROR: Falta argumento. Uso: $0 <n8n_researcher|doctora_lucy>"
    exit 1
fi

ROLE="$1"

# --- Modo: Volver a Doctora Lucy (rectora) ---
if [ "$ROLE" = "doctora_lucy" ]; then
    if [ -f "$ACTIVE_ROLE_FILE" ]; then
        PREV_ROLE=$(cat "$ACTIVE_ROLE_FILE")
        rm -f "$ACTIVE_ROLE_FILE"
        echo "[$TIMESTAMP] SWITCH: $PREV_ROLE → doctora_lucy (rectora)" >> "$LOG_FILE"
        echo "[switch_agent] ✅ Control devuelto a Doctora Lucy (rectora). Rol anterior: $PREV_ROLE"
    else
        echo "[switch_agent] ℹ️  Ya estás en modo Doctora Lucy (rectora). No hay rol activo."
    fi
    exit 0
fi

# --- Modo: Activar un sub-agente ---
ROLE_FILE="${ROLE_MAP[$ROLE]}"

if [ -z "$ROLE_FILE" ]; then
    echo "[switch_agent] ERROR: Rol '$ROLE' no reconocido."
    echo "[switch_agent] Roles disponibles: ${!ROLE_MAP[*]}, doctora_lucy"
    exit 1
fi

if [ ! -f "$ROLES_DIR/$ROLE_FILE" ]; then
    echo "[switch_agent] ERROR: Archivo de rol no encontrado: $ROLES_DIR/$ROLE_FILE"
    exit 1
fi

# Registrar rol anterior si existe
PREV_ROLE="doctora_lucy"
if [ -f "$ACTIVE_ROLE_FILE" ]; then
    PREV_ROLE=$(cat "$ACTIVE_ROLE_FILE")
fi

# Activar nuevo rol
echo "$ROLE" > "$ACTIVE_ROLE_FILE"
echo "[$TIMESTAMP] SWITCH: $PREV_ROLE → $ROLE ($ROLE_FILE)" >> "$LOG_FILE"
echo "[switch_agent] ✅ Rol activado: $ROLE (archivo: $ROLE_FILE)"
echo "[switch_agent] 📄 Archivo de instrucciones: $ROLES_DIR/$ROLE_FILE"
