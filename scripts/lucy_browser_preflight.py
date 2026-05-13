#!/usr/bin/env python3
import subprocess
import json
import sys
import os

OPENCLAW_BIN = os.getenv("OPENCLAW_BIN", "/home/lucy-ubuntu/.npm-global/bin/openclaw")
TARGET_PATTERN = "127.0.0.1:8772/diagnostics/browser_telegram_e2e"

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
        return {
            "ok": False,
            "error": "No pude listar pestañas Chrome adjuntas",
            "returncode": res.returncode,
            "stderr": res.stderr.strip(),
        }
    except Exception as e:
        return {"ok": False, "error": f"Error getting tabs: {e}"}
    return {"ok": False, "error": "Respuesta inesperada al listar pestañas Chrome adjuntas"}

def normalize_tabs(raw_tabs):
    if isinstance(raw_tabs, dict) and raw_tabs.get("ok") is False:
        return raw_tabs
    if isinstance(raw_tabs, list):
        return raw_tabs
    return []

def resolve_tab_target_id(tab):
    for key in ("suggestedTargetId", "targetId", "id", "tabId"):
        value = tab.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None

def tab_summary(tab):
    return {
        "title": tab.get("title"),
        "url": tab.get("url"),
        "suggestedTargetId": tab.get("suggestedTargetId"),
        "targetId": tab.get("targetId"),
        "id": tab.get("id"),
        "tabId": tab.get("tabId"),
    }

def resolve_e2e_context():
    tabs_result = get_tabs()
    tabs = normalize_tabs(tabs_result)
    if isinstance(tabs, dict) and tabs.get("ok") is False:
        return tabs
    if not tabs:
        return {
            "ok": False,
            "error": "No hay pestañas Chrome adjuntas. Asegurarse de que Browser Relay esté en ON.",
            "available_tabs": [],
        }

    e2e_tab = None
    for tab in tabs:
        url = tab.get("url", "")
        if TARGET_PATTERN in url:
            e2e_tab = tab
            break
    
    if not e2e_tab:
        return {
            "ok": False, 
            "error": "Pestaña E2E no encontrada en Chrome", 
            "available_tabs": [tab_summary(t) for t in tabs]
        }

    url = e2e_tab.get("url", "")
    if TARGET_PATTERN not in url:
        return {
            "ok": False,
            "error": "La pestaña encontrada no pertenece al E2E local autorizado",
            "url": url,
        }

    tab_id = resolve_tab_target_id(e2e_tab)
    if not tab_id:
        return {
            "ok": False,
            "error": "Pestaña E2E encontrada, pero sin target id utilizable",
            "tab": tab_summary(e2e_tab),
        }
    
    try:
        # Foco y Snapshot
        focus_res = subprocess.run(
            [OPENCLAW_BIN, "browser", "--browser-profile", "chrome", "focus", tab_id],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if focus_res.returncode != 0:
            return {
                "ok": False,
                "error": "No pude enfocar la pestaña E2E",
                "tab_id": tab_id,
                "stderr": focus_res.stderr.strip(),
            }
        
        res_snap = subprocess.run(
            [
                OPENCLAW_BIN,
                "browser",
                "--browser-profile",
                "chrome",
                "snapshot",
                "--interactive",
                "--target-id",
                tab_id,
            ],
            capture_output=True,
            text=True,
            timeout=12
        )
        snapshot = res_snap.stdout.strip()
        if res_snap.returncode != 0 or not snapshot:
            return {
                "ok": False,
                "error": "No pude obtener snapshot de la pestaña E2E",
                "tab_id": tab_id,
                "returncode": res_snap.returncode,
                "stderr": res_snap.stderr.strip(),
            }
        
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
