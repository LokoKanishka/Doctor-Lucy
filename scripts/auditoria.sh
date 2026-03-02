#!/usr/bin/env bash
set -euo pipefail

# ===== Config =====
TIMEOUT_S="${TIMEOUT_S:-6}"
OUT_DIR="${OUT_DIR:-.}"
REPORT="${REPORT:-$OUT_DIR/auditoria_sistema.md}"

# Jurisdicción Docker (preferible label)
DOCKER_LABEL_KEY="${DOCKER_LABEL_KEY:-doctor_lucy}"
DOCKER_LABEL_VAL="${DOCKER_LABEL_VAL:-true}"

# Fallback por nombre (si no hay labels)
NAME_REGEX="${NAME_REGEX:-doctor|lucy|rag|qdrant|ollama}"

mkdir -p "$OUT_DIR"

have() { command -v "$1" >/dev/null 2>&1; }
run_to() { # run_to <cmd...>
  if have timeout; then timeout "$TIMEOUT_S" "$@"; else "$@"; fi
}

usage() {
  cat <<'USAGE'
Uso: ./scripts/auditoria.sh [--docker] [--docker-global] [--network] [--out FILE] [--timeout N]

Default (sin flags): NO toca Docker ni escanea puertos. Solo métricas locales + salud del proyecto.

Flags:
  --docker         Audita contenedores SOLO bajo jurisdicción (label/patrón).
  --docker-global  Audita TODOS los contenedores (host-wide).
  --network        Muestra info de red/puertos (marcado como host-wide; requiere permisos para ver procesos).
  --out FILE       Ruta del reporte (default ./auditoria_sistema.md)
  --timeout N      Timeout por comando (default 6)
USAGE
}

DO_DOCKER=0
DO_DOCKER_GLOBAL=0
DO_NETWORK=0

# ===== Argparse =====
while [ $# -gt 0 ]; do
  case "$1" in
    --docker) DO_DOCKER=1 ;;
    --docker-global) DO_DOCKER_GLOBAL=1 ;;
    --network) DO_NETWORK=1 ;;
    --out) REPORT="$2"; shift ;;
    --timeout) TIMEOUT_S="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Arg desconocido: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

ts="$(date +%Y-%m-%d\ %H:%M:%S)"
{
  echo "# Auditoría del sistema (Doctor Lucy)"
  echo
  echo "- Timestamp: \`$ts\`"
  echo "- Scope default: **PROJECT-ONLY** (sin Docker/Network salvo opt-in)"
  echo "- TIMEOUT_S: \`$TIMEOUT_S\`"
  echo
} > "$REPORT"

append() { cat >> "$REPORT"; }

# ===== 0) Métricas locales seguras =====
{
  echo "## Salud local (safe)"
  echo
  echo "### CPU / Load"
  if have uptime; then run_to uptime || true; fi
  echo
  echo "### Memoria"
  if have free; then run_to free -h || true; fi
  echo
  echo "### Disco"
  if have df; then run_to df -h / || true; fi
  echo
} | append

# ===== 1) Salud del proyecto (RAG local típico) =====
{
  echo "## Salud del proyecto (RAG local)"
  echo
  # Ollama
  if have curl; then
    echo "### Ollama (127.0.0.1:11434)"
    if run_to curl -fsS --max-time "$TIMEOUT_S" "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
      echo "- Estado: OK"
    else
      echo "- Estado: WARN/FAIL (no responde en ${TIMEOUT_S}s)"
    fi
    echo
  fi

  # Qdrant (si aplica; intenta 6333 por defecto, no “descubre” nada global)
  if have curl; then
    echo "### Qdrant (127.0.0.1:6333)"
    if run_to curl -fsS --max-time "$TIMEOUT_S" "http://127.0.0.1:6333/readyz" >/dev/null 2>&1; then
      echo "- Estado: OK"
    else
      echo "- Estado: WARN/FAIL (no responde en ${TIMEOUT_S}s)"
    fi
    echo
  fi
} | append

# ===== 2) Docker (opt-in) =====
if [ "$DO_DOCKER" -eq 1 ] || [ "$DO_DOCKER_GLOBAL" -eq 1 ]; then
  {
    echo "## Docker (OPT-IN)"
    echo
    if ! have docker; then
      echo "- Docker: no instalado"
      echo
    else
      if [ "$DO_DOCKER_GLOBAL" -eq 1 ]; then
        echo "- Scope: **HOST-WIDE** (docker global habilitado explícitamente)"
        echo
        run_to docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' || true
      else
        echo "- Scope: **PROJECT-ONLY** (jurisdicción por label/patrón)"
        echo "- Label objetivo: \`${DOCKER_LABEL_KEY}=${DOCKER_LABEL_VAL}\`"
        echo "- Fallback name regex: \`$NAME_REGEX\`"
        echo
        # Primero intenta por label (si hay contenedores etiquetados)
        if run_to docker ps --filter "label=${DOCKER_LABEL_KEY}=${DOCKER_LABEL_VAL}" --format '{{.ID}}' | grep -q .; then
          run_to docker ps --filter "label=${DOCKER_LABEL_KEY}=${DOCKER_LABEL_VAL}" \
            --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' || true
        else
          # Fallback: filtra por nombre
          run_to docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' \
            | awk -v re="$NAME_REGEX" 'BEGIN{IGNORECASE=1} $0 ~ re {print}' \
            | { echo -e "NAMES\tIMAGE\tSTATUS\tPORTS"; cat; } || true
          echo
          echo "> Nota: No encontré labels \`${DOCKER_LABEL_KEY}=${DOCKER_LABEL_VAL}\`. Considerá etiquetar contenedores del proyecto."
        fi
      fi
      echo
    fi
  } | append
fi

# ===== 3) Network (opt-in) =====
if [ "$DO_NETWORK" -eq 1 ]; then
  {
    echo "## Network / Puertos (OPT-IN)"
    echo
    echo "- Scope: **HOST-WIDE** (red/puertos son globales por naturaleza)"
    echo "- Nota: \`ss -tulpn\` puede requerir permisos para ver procesos."
    echo
    if have ss; then
      run_to ss -tulpn || true
    elif have netstat; then
      run_to netstat -tulpn || true
    else
      echo "- No hay \`ss\` ni \`netstat\`."
    fi
    echo
  } | append
fi

# ===== Footer =====
{
  echo "---"
  echo "Fin del reporte."
} | append

echo "OK: reporte generado en $REPORT"
