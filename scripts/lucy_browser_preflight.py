#!/usr/bin/env python3
import subprocess
import json
import sys
import os

OPENCLAW_BIN = os.getenv("OPENCLAW_BIN", "/home/lucy-ubuntu/.npm-global/bin/openclaw")

def get_tabs():
    try:
        res = subprocess.run(
            [OPENCLAW_BIN, "browser", "--browser-profile", "chrome", "tabs", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if res.returncode == 0:
            stdout = res.stdout.strip()
            start = stdout.find("{")
            if start != -1:
                data = json.loads(stdout[start:])
                if isinstance(data, dict) and "tabs" in data:
                    return data["tabs"]
                if isinstance(data, list):
                    return data
                return [data]
    except Exception as e:
        print(f"Error getting tabs: {e}", file=sys.stderr)
    return []

def resolve_e2e_context():
    tabs = get_tabs()
    if not tabs:
        return {"ok": False, "error": "No hay pestañas Chrome adjuntas. Asegurarse de que Browser Relay esté en ON."}

    target_pattern = "127.0.0.1:8772/diagnostics/browser_telegram_e2e"
    e2e_tab = None
    for tab in tabs:
        url = tab.get("url", "")
        if target_pattern in url:
            e2e_tab = tab
            break
    
    if not e2e_tab:
        return {
            "ok": False, 
            "error": "Pestaña E2E no encontrada en Chrome", 
            "available_tabs": [{"title": t.get("title"), "url": t.get("url")} for t in tabs]
        }

    tab_id = e2e_tab.get("id")
    
    try:
        # Foco y Snapshot
        subprocess.run([OPENCLAW_BIN, "browser", "--browser-profile", "chrome", "focus", tab_id], capture_output=True, timeout=5)
        
        res_snap = subprocess.run(
            [OPENCLAW_BIN, "browser", "--browser-profile", "chrome", "snapshot", "--interactive"],
            capture_output=True,
            text=True,
            timeout=12
        )
        snapshot = res_snap.stdout.strip()
        
        return {
            "ok": True,
            "tab_id": tab_id,
            "url": e2e_tab.get("url"),
            "title": e2e_tab.get("title"),
            "snapshot": snapshot
        }
    except Exception as e:
        return {"ok": False, "error": f"Error interactuando con la pestaña: {e}", "tab_id": tab_id}

if __name__ == "__main__":
    print(json.dumps(resolve_e2e_context(), indent=2, ensure_ascii=False))
