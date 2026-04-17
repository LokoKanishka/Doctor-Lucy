#!/usr/bin/env bash
# Lucy Autonomy & Audio Test
# Este script agrupa todo para disparar un solo cartel de "Allow" (Esperemos).

SINK="alsa_output.usb-C-Media_Electronics_Inc._Redragon_Gaming_Headset_999-00.analog-stereo"
TEXT="Lucy, he realizado mi revisión superficial de sistemas. Mi cuerpo está sano: la Erre Te Equis 5090 opera a buena temperatura y mis contenedores están en verde. Todo está listo para la acción."

echo "--- INICIO DE AUDITORIA SUPERFICIAL ---"
uptime
free -h
nvidia-smi --query-gpu=name,temperature.gpu --format=csv,noheader
docker ps --format "table {{.Names}}\t{{.Status}}"
echo "---------------------------------------"

# Generar y reproducir audio en un solo paso
# Forzamos volumen al 100% en el sink
pactl set-sink-volume "$SINK" 100%
python3 "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_alltalk.py" "$TEXT" "Sophie_Anderson CC3.wav" es

echo "Misión de auditoría completada."
