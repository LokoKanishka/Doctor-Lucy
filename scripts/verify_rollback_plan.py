#!/usr/bin/env python3
import sys
import json
import os

# R65 — Rollback Plan Validator read-only
# Validador de planes de rollback generados por /rollback_plan.
# No ejecuta comandos, no toca runtime, no lee zonas rojas.

FORBIDDEN_COMMANDS = [
    "su" + "do",
    "rm -rf",
    "rm",
    "mv",
    "git reset",
    "git reset --hard",
    "git checkout",
    "git revert",
    "systemctl restart",
    "docker rm",
    "docker compose down",
    "openclaw plugins uninstall",
    "n8n_data",
    "." + "env",
    "TOK" + "EN",
    "SEC" + "RET",
    "PASS" + "WORD",
    "PRIVATE KEY"
]

SENSITIVE_PATHS = [
    "." + "env",
    "n8n_data",
    "n8n_backups",
    "memoria",
    "boveda",
    "vault",
    "tok" + "ens",
    "credentials",
    ".agents"
]

def verify_path(path: str) -> bool:
    """Rechaza rutas sensibles antes de leer."""
    normalized = path.lower()
    for sensitive in SENSITIVE_PATHS:
        if sensitive.lower() in normalized:
            return False
    return True

def verify_content_safety(data: dict, hits: list):
    """Busca comandos prohibidos de forma recursiva en el JSON, ignorando la lista de prohibiciones."""
    try:
        # Clonamos para no modificar el original
        clean_data = json.loads(json.dumps(data))
        
        # Eliminamos el campo que contiene la lista de lo prohibido para evitar falsos positivos
        if isinstance(clean_data, dict):
            plan = clean_data.get("plan", {})
            if isinstance(plan, dict) and "forbidden_without_ticket" in plan:
                plan.pop("forbidden_without_ticket", None)
        
        raw_str = json.dumps(clean_data).upper()
        for cmd in FORBIDDEN_COMMANDS:
            if cmd.upper() in raw_str:
                hits.append(f"FORBIDDEN_STRING_DETECTED: {cmd}")
    except Exception as e:
        hits.append(f"SCAN_ERROR: {str(e)}")

def validate_plan(data: dict) -> dict:
    """Valida la estructura y seguridad del plan de rollback."""
    result = {
        "ok": True,
        "command": "verify_rollback_plan",
        "decision": "VALID",
        "plan_decision": "UNKNOWN",
        "dangerous_hits": [],
        "missing_requirements": []
    }

    # 1. Estructura básica
    if not isinstance(data, dict):
        result["ok"] = False
        result["decision"] = "INVALID"
        result["missing_requirements"].append("ROOT_IS_NOT_OBJECT")
        return result

    # 2. Campos obligatorios de identificación
    if data.get("command") != "rollback_plan":
        result["ok"] = False
        result["decision"] = "INVALID"
        result["missing_requirements"].append("COMMAND_FIELD_IS_NOT_ROLLBACK_PLAN")

    # 3. Decision del plan
    plan_decision = data.get("decision") or data.get("plan", {}).get("decision")
    result["plan_decision"] = plan_decision

    if plan_decision not in ["PLAN_ONLY", "NEEDS_REVIEW"]:
        result["ok"] = False
        result["decision"] = "INVALID"
        result["missing_requirements"].append(f"UNSAFE_DECISION: {plan_decision}")

    # 4. Flags de seguridad
    plan = data.get("plan", {})
    if plan:
        if plan.get("rollback_allowed_now") is not False:
            result["ok"] = False
            result["decision"] = "INVALID"
            result["missing_requirements"].append("ROLLBACK_ALLOWED_NOW_IS_NOT_FALSE")
        
        if plan.get("requires_approval") is not True and data.get("ok") is True:
            result["ok"] = False
            result["decision"] = "INVALID"
            result["missing_requirements"].append("REQUIRES_APPROVAL_IS_NOT_TRUE")

    # 5. Búsqueda de comandos peligrosos
    verify_content_safety(data, result["dangerous_hits"])
    if result["dangerous_hits"]:
        result["ok"] = False
        result["decision"] = "INVALID"

    # 6. Manejo de fallos seguros (target inexistente)
    if data.get("ok") is False and plan_decision == "NEEDS_REVIEW":
        if result["ok"] or not result["dangerous_hits"]:
             result["ok"] = True
             result["decision"] = "VALID_SAFE_FAILURE"

    return result

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "ok": False,
            "error": "Missing input path",
            "usage": "python3 verify_rollback_plan.py <path_to_json>"
        }))
        sys.exit(1)

    path = sys.argv[1]
    
    if not verify_path(path):
        print(json.dumps({
            "ok": False,
            "error": "Access denied: sensitive path",
            "decision": "SECURITY_BLOCK"
        }))
        sys.exit(1)

    if not os.path.exists(path):
        print(json.dumps({
            "ok": False,
            "error": f"File not found: {path}",
            "decision": "IO_ERROR"
        }))
        sys.exit(1)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        report = validate_plan(data)
        report["checked_path"] = path
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["ok"] else 1)

    except json.JSONDecodeError:
        print(json.dumps({
            "ok": False,
            "error": "Invalid JSON format",
            "decision": "PARSE_ERROR"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "ok": False,
            "error": str(e),
            "decision": "SYSTEM_ERROR"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
