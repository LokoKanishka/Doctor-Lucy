#!/bin/bash

if [ -z "${DOCTOR_LUCY_ALLOW_LEGACY_TELEGRAM_LISTENER_SH:-}" ]; then
    echo "LEGACY BLOCKED: lucy_telegram_listener.sh duplica lucy_telegram_listener.py."
    exit 2
fi

# Lucy Telegram Listener — Daemon de escucha automática
# Polling cada 3 segundos para mensajes nuevos de Diego
# Solo responde al ID autorizado: 5154360597

BOT_TOKEN="8591918754:AAHlxsxP4olX3De2uWGH0NUUXEiHX3iUhLk"
DIEGO_ID="5154360597"
API_URL="https://api.telegram.org/bot${BOT_TOKEN}"
OFFSET=0
WORKSPACE="/home/lucy-ubuntu/Escritorio/doctor de lucy"
LOG_FILE="${WORKSPACE}/n8n_data/telegram_listener.log"

echo "[$(date)] Lucy Telegram Listener iniciado." >> "$LOG_FILE"

while true; do
    # Obtener updates con offset para no repetir mensajes
    RESPONSE=$(curl -s "${API_URL}/getUpdates?offset=${OFFSET}&timeout=10")
    
    # Verificar si hay resultados
    HAS_RESULTS=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('result',[])))" 2>/dev/null)
    
    if [ "$HAS_RESULTS" -gt 0 ] 2>/dev/null; then
        # Procesar cada update
        echo "$RESPONSE" | python3 -c "
import sys, json, subprocess, os

data = json.load(sys.stdin)
api_url = '${API_URL}'
diego_id = ${DIEGO_ID}
workspace = '${WORKSPACE}'

for update in data.get('result', []):
    update_id = update['update_id']
    msg = update.get('message', {})
    from_id = msg.get('from', {}).get('id', 0)
    text = msg.get('text', '')
    chat_id = msg.get('chat', {}).get('id', 0)
    
    # Solo responder a Diego
    if from_id != diego_id:
        print(f'[BLOQUEADO] Mensaje de ID no autorizado: {from_id}')
        continue
    
    print(f'[DIEGO] Mensaje recibido: {text}')
    
    # Procesar comandos
    response_text = ''
    
    if text.lower() in ['/start', 'hola', 'hola lucy']:
        response_text = '🩺 ¡Hola Diego! Soy Lucy Cunningham. Estoy online y escuchando. Comandos disponibles:\n/status - Estado del sistema\n/audit - Auditoría rápida\n/docker - Estado de contenedores\n/help - Lista de comandos'
    
    elif text.lower() == '/status':
        try:
            result = subprocess.run(['uptime'], capture_output=True, text=True, timeout=10)
            uptime_info = result.stdout.strip()
            result2 = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=10)
            mem_info = result2.stdout.strip()
            response_text = f'🖥️ Estado del Sistema:\n\n⏱️ {uptime_info}\n\n💾 Memoria:\n{mem_info}'
        except Exception as e:
            response_text = f'❌ Error al obtener estado: {e}'
    
    elif text.lower() == '/audit':
        try:
            result = subprocess.run(['bash', f'{workspace}/scripts/auditoria_boot.sh'], 
                                  capture_output=True, text=True, timeout=30)
            output = result.stdout.strip()[:3000]  # Limitar a 3000 chars por Telegram
            response_text = f'🔍 Auditoría Rápida:\n\n{output}'
        except Exception as e:
            response_text = f'❌ Error en auditoría: {e}'
    
    elif text.lower() == '/docker':
        try:
            result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'],
                                  capture_output=True, text=True, timeout=10)
            output = result.stdout.strip()
            response_text = f'🐳 Contenedores Docker:\n\n{output}'
        except Exception as e:
            response_text = f'❌ Error Docker: {e}'
    
    elif text.lower() == '/help':
        response_text = '🩺 Comandos de Lucy:\n\n/status - Estado del sistema (uptime, memoria)\n/audit - Auditoría completa del boot\n/docker - Estado de contenedores\n/help - Este mensaje'
    
    else:
        response_text = f'🩺 Recibí tu mensaje: \"{text}\"\nPero todavía no tengo esa habilidad. Usá /help para ver los comandos disponibles.'
    
    if response_text:
        import urllib.request, urllib.parse
        params = urllib.parse.urlencode({'chat_id': chat_id, 'text': response_text}).encode()
        req = urllib.request.Request(f'{api_url}/sendMessage', data=params)
        urllib.request.urlopen(req, timeout=10)
        print(f'[ENVIADO] Respuesta enviada a Diego')
    
    # Guardar el offset para no reprocesar
    with open(f'{workspace}/n8n_data/telegram_offset.txt', 'w') as f:
        f.write(str(update_id + 1))
" 2>> "$LOG_FILE"
        
        # Actualizar offset del último update procesado
        if [ -f "${WORKSPACE}/n8n_data/telegram_offset.txt" ]; then
            OFFSET=$(cat "${WORKSPACE}/n8n_data/telegram_offset.txt")
        fi
    fi
    
    sleep 3
done
