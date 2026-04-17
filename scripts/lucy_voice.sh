#!/bin/bash
# Lucy Voice Feedback Wrapper (Neural Upgrade)
# Uso: ./scripts/lucy_voice.sh "Mensaje a decir"

MESSAGE=$1
VOICE=${2:-"female_01.wav"}
LANGUAGE=${3:-"es"}

# Nueva ruta del motor neural AllTalk
SCRIPT_DIR="$(dirname "$0")"
python3 "$SCRIPT_DIR/lucy_alltalk.py" "$MESSAGE" "$VOICE" "$LANGUAGE"
