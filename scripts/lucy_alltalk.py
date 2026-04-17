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
ALLTALK_URL = "http://127.0.0.1:7851/api/generate"
OUTPUT_DIR = "/home/lucy-ubuntu/Archivo_proyectos/Taverna/Taverna-legacy/alltalk_tts"

def speak(text, voice="Sophie_Anderson CC3.wav", language="es"):
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
        response = requests.post(ALLTALK_URL, json=payload, timeout=60)
        result = response.json()
        
        if result.get("status") == "generate-success":
            audio_path = os.path.join(OUTPUT_DIR, result["data"]["audio_path"])
            
            if os.path.exists(audio_path):
                # Reproducir usando paplay (PipeWire/PulseAudio nativo del sistema)
                ret = subprocess.run(["paplay", audio_path], check=False)
                if ret.returncode != 0:
                    # Fallback: ffplay si paplay falla
                    subprocess.run(
                        ["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", audio_path],
                        check=False
                    )
                # Limpiar archivo temporal
                os.remove(audio_path)
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
        sys.exit(1)
    
    input_text = sys.argv[1]
    input_voice = sys.argv[2] if len(sys.argv) > 2 else "Sophie_Anderson CC3.wav"
    input_lang = sys.argv[3] if len(sys.argv) > 3 else "es"
    
    speak(input_text, input_voice, input_lang)
