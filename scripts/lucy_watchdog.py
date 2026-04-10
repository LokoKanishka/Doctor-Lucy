#!/usr/bin/env python3
import time
import os
import sys
import json
import subprocess
import argparse
from datetime import datetime

# Rutas globales
BASE_DIR = "/home/lucy-ubuntu/Escritorio/doctor de lucy"
STATUS_FILE = os.path.join(BASE_DIR, "Cerebro/multiagent_status.json")
SOUND_FILE = "/usr/share/sounds/Yaru/stereo/complete.oga"

def log_status(agent_path, status, progress=0):
    agent_name = os.path.basename(agent_path.strip("/"))
    data = {}
    
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                data = json.load(f)
        except:
            pass
    
    data[agent_name] = {
        "status": status,
        "progress": progress,
        "last_update": datetime.now().isoformat(),
        "path": agent_path
    }
    
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def play_notification():
    try:
        subprocess.run(["paplay", SOUND_FILE], check=False)
    except:
        print("\a") # Beep de sistema fallback

def get_progress(agent_path):
    task_file = os.path.join(agent_path, "task.md")
    if not os.path.exists(task_file):
        return 0
    try:
        with open(task_file, "r") as f:
            content = f.read()
            total = content.count("[ ]") + content.count("[x]") + content.count("[/]")
            done = content.count("[x]")
            if total == 0: return 0
            return int((done / total) * 100)
    except:
        return 0

def monitor(agent_path, report_filename="LUCY_REPORT.md", interval=60):
    report_file = os.path.join(agent_path, report_filename)
    print(f"[*] Iniciando vigilancia en: {agent_path}")
    
    while True:
        if os.path.exists(report_file):
            print(f"[!] Reporte detectado en {agent_path}")
            log_status(agent_path, "COMPLETADO", 100)
            play_notification()
            break
        
        progress = get_progress(agent_path)
        log_status(agent_path, "EN_PROGRESO", progress)
        print(f"[-] Monitoreando... Progreso: {progress}%")
        
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watchdog de Lucy para Sub-Agentes")
    parser.add_argument("--path", required=True, help="Ruta al proyecto del sub-agente")
    parser.add_argument("--interval", type=int, default=60, help="Intervalo de sondeo en segundos")
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: La ruta {args.path} no existe.")
        sys.exit(1)
        
    monitor(args.path, interval=args.interval)
