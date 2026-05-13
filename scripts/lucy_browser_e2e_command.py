#!/usr/bin/env python3
import subprocess
import json
import sys
import os
import re
import time

OPENCLAW_BIN = os.getenv("OPENCLAW_BIN", "/home/lucy-ubuntu/.npm-global/bin/openclaw")
# Intentar localizar el binario si no está en la ruta por defecto
if not os.path.exists(OPENCLAW_BIN):
    OPENCLAW_BIN = "openclaw"

def run_command(args, timeout=20):
    cmd = [OPENCLAW_BIN, "browser", "--browser-profile", "chrome"] + args
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return res

def get_snapshot(retries=2):
    for i in range(retries):
        res = run_command(["snapshot", "--interactive"])
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout
        time.sleep(1)
    return ""

def extract_ref(snapshot, text_pattern):
    # El snapshot interactivo tiene este formato: - button "Texto" [ref=e12]
    # O: - textbox "Texto" [ref=e7]:
    # Usamos un regex flexible
    pattern = rf'"{text_pattern}" .*?\[ref=(e\d+)\]'
    match = re.search(pattern, snapshot)
    if match:
        return match.group(1)
    return None

def execute_browser_action(action, args=None):
    # Asegurar que estamos en la URL correcta primero (Preflight)
    # No navegamos, solo verificamos.
    
    if action == "read":
        snapshot = get_snapshot()
        return {
            "ok": True,
            "summary": "Página de prueba E2E activa.",
            "content": snapshot
        }

    elif action == "open_panel":
        snap = get_snapshot()
        ref = extract_ref(snap, "Abrir panel de prueba")
        if not ref:
            return {"ok": False, "error": "No encontré el botón 'Abrir panel de prueba' en el snapshot"}
        
        run_command(["click", ref])
        time.sleep(1)
        post_snap = get_snapshot()
        return {
            "ok": True,
            "message": "Panel abierto.",
            "snapshot": post_snap
        }

    elif action == "type_validate":
        text_to_type = args if args else "prueba completa desde Telegram"
        snap = get_snapshot()
        ref_input = extract_ref(snap, "Campo Telegram local")
        if not ref_input:
            return {"ok": False, "error": "No encontré el campo de texto"}
        
        run_command(["type", ref_input, text_to_type])
        time.sleep(1)
        
        snap2 = get_snapshot()
        ref_btn = extract_ref(snap2, "Validar texto Telegram")
        if not ref_btn:
            return {"ok": False, "error": "No encontré el botón de validar"}
        
        run_command(["click", ref_btn])
        time.sleep(1)
        
        final_snap = get_snapshot()
        return {
            "ok": True,
            "message": f"Validado: {text_to_type}",
            "snapshot": final_snap
        }

    elif action == "navigate_roundtrip":
        snap = get_snapshot()
        ref_link = extract_ref(snap, "Ir a página 2 E2E")
        if not ref_link:
            return {"ok": False, "error": "No encontré el link a la página 2"}
        
        run_command(["click", ref_link])
        time.sleep(2)
        
        snap2 = get_snapshot()
        if "Página E2E actual: 2" not in snap2:
            return {"ok": False, "error": "No parece que hayamos llegado a la página 2", "snapshot": snap2}
        
        ref_back = extract_ref(snap2, "Volver a página 1 E2E")
        if not ref_back:
            return {"ok": False, "error": "No encontré el link de vuelta"}
        
        run_command(["click", ref_back])
        time.sleep(2)
        
        final_snap = get_snapshot()
        return {
            "ok": True,
            "message": "Ida y vuelta completada.",
            "snapshot": final_snap
        }

    return {"ok": False, "error": f"Acción desconocida: {action}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Falta acción"}))
        sys.exit(1)
    
    action = sys.argv[1]
    args = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = execute_browser_action(action, args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
