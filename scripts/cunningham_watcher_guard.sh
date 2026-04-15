#!/usr/bin/env bash
set -euo pipefail

project_root="${1:-/home/lucy-ubuntu/Escritorio/cunningham-naranja}"
watcher_script="$project_root/scripts/watcher_daemon.sh"

if [[ ! -d "$project_root" ]]; then
  echo "cunningham watcher guard: project root missing: $project_root"
  exit 0
fi

if [[ ! -x "$watcher_script" ]]; then
  echo "cunningham watcher guard: watcher script missing or not executable: $watcher_script"
  exit 0
fi

exec "$watcher_script" "$project_root"
