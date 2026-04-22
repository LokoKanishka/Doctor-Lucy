#!/usr/bin/env python3
"""
Lucy TTS Client - AllTalk Integration
Genera y reproduce voz neural via AllTalk TTS server.
"""
import requests
import sys
import os
import subprocess
import uuid

# Configuración
LUCY_ALLTALK_URL = os.getenv("LUCY_ALLTALK_URL", "http://127.0.0.1:7854/api/generate")
""
OUTPUT_DIR = "/home/lucy-ubuntu/Archivo_proyectos/Taverna/Taverna-legacy/alltalk_tts"

def speak(text, voice="female_03.wav", language="es"):
    audio_filename = f"lucy_temp_{uuid.uuid4().hex}.wav"
    
    # Schema validado contra la API real de AllTalk TTS
    payload = {
        "text": text,
        "voice": voice,
        "language": language,
        "temperature": 0.7,
        "repetition_penalty": 5.0,
        "output_file": audio_filename
    }

    try:
        print(f"[Lucy TTS] Enviando solicitud a {LUCY_ALLTALK_URL}...")
        response = requests.post(LUCY_ALLTALK_URL, json=payload, timeout=600)
        result = response.json()
        
        if result.get("status") == "generate-success":
            audio_path = os.path.join(OUTPUT_DIR, result["data"]["audio_path"])
            print(f"[Lucy TTS] Éxito. Archivo generado en: {audio_path}")
            
            if os.path.exists(audio_path):
                print(f"[Lucy TTS] Reproduciendo {audio_path}...")
                played = False
                # Primero: ffplay (maneja concurrencia de audio sin bloqueos)
                try:
                    ret = subprocess.run(
                        ["ffplay", "-autoexit", "-nodisp", "-loglevel", "error", audio_path],
                        check=False, timeout=300
                    )
                    played = (ret.returncode == 0)
                    if not played:
                        print(f"[Lucy TTS] ffplay falló (code {ret.returncode}).")
                except FileNotFoundError:
                    print("[Lucy TTS] ffplay no encontrado.")
                except subprocess.TimeoutExpired:
                    print("[Lucy TTS] ffplay timeout (300s).")

                # Fallback: paplay con sink explícito
                if not played:
                    SINK = "alsa_output.usb-C-Media_Electronics_Inc._Redragon_Gaming_Headset_999-00.analog-stereo"
                    print(f"[Lucy TTS] Intentando paplay con sink {SINK}...")
                    try:
                        subprocess.run(["paplay", f"--device={SINK}", audio_path], check=False, timeout=30)
                    except subprocess.TimeoutExpired:
                        print("[Lucy TTS] paplay timeout (30s).")

                # Limpiar archivo temporal
                try:
                    os.remove(audio_path)
                except OSError:
                    pass
            else:
                print(f"[Lucy TTS] Error: archivo de audio no encontrado en {audio_path}", file=sys.stderr)
        else:
            print(f"[Lucy TTS] Error de API: {result}", file=sys.stderr)
            
    except requests.exceptions.Timeout:
        print("[Lucy TTS] Error: AllTalk TTS no respondió (timeout)", file=sys.stderr)
    except Exception as e:
        print(f"[Lucy TTS] Error inesperado: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 lucy_alltalk.py \"texto\" [voz] [idioma]")
        print("O: python3 lucy_alltalk.py --file [ruta_al_archivo] [voz] [idioma]")
        sys.exit(1)
    
    input_text = ""
    arg_idx = 1
    
    if sys.argv[1] == "--file":
        file_path = sys.argv[2] if len(sys.argv) > 2 else "/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/voice_payload.txt"
        try:
            with open(file_path, "r") as f:
                input_text = f.read().strip()
            arg_idx = 3 # Sugerir que voz e idioma vienen después de la ruta
        except Exception as e:
            print(f"[Lucy TTS] Error leyendo archivo {file_path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        input_text = sys.argv[1]
        arg_idx = 2

    input_voice = sys.argv[arg_idx] if len(sys.argv) > arg_idx else "Lucy_Cunningham.wav"
    input_lang = sys.argv[arg_idx + 1] if len(sys.argv) > arg_idx + 1 else "es"
    
    if not input_text:
        print("[Lucy TTS] Error: No hay texto para procesar.", file=sys.stderr)
        sys.exit(1)
        
    speak(input_text, input_voice, input_lang)
