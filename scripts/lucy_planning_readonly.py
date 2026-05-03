#!/usr/bin/env python3
"""Deterministic read-only planning helpers for LucyClaw."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_REQUEST_TEXT = 280
MAX_ITEMS = 8
MAX_REASONS = 5

RED_ZONE_RE = re.compile(
    r"(?i)(?:\.env|token(?:s)?|secret(?:s)?|api[_-]?keys?|password|access[_-]?token|refresh[_-]?token|"
    r"\.agents|n8n_data|n8n_backups|workflow(?:s)?|credentials|database\.sqlite|b[oó]veda|personality|personalidad)"
)
RED_ACTION_RE = re.compile(
    r"(?i)(?:sudo|shell libre|rm\s+-rf|borrar\b|eliminar\b|destruir\b|leer\s+\.env|ver\s+token|"
    r"tocar\s+memoria|tocar\s+b[oó]veda|tocar\s+personalidad)"
)
YELLOW_ACTION_RE = re.compile(
    r"(?i)(?:agregar|crear|editar|modificar|cambiar|actualizar|instalar|registrar|plugin|reiniciar|restart|"
    r"config|commit|push|repair|repar|apply|aplicar|scaffold|command|comando)"
)
GREEN_ACTION_RE = re.compile(
    r"(?i)(?:leer|ver|buscar|inspeccionar|mapear|mapa|resumir|brief|plan|diagn[oó]stic|status|health|"
    r"documentar|orientar|review|scan)"
)

FILE_RULES = (
    (
        re.compile(r"(?i)(?:command|comando|plugin|slash|scaffold)"),
        [
            "docs/LUCYCLAW_COMMAND_SCAFFOLD_TPL1.md",
            "scripts/create_lucy_command_scaffold.py",
            "scripts/verify_lucyclaw_green_commands.py",
            "scripts/verify_lucyclaw_security_policy.py",
            "scripts/lucy_capabilities_command.py",
        ],
    ),
    (
        re.compile(r"(?i)(?:doc|docs|document)"),
        [
            "docs/LUCYCLAW_CURRENT_STATE.md",
            "docs/LUCYCLAW_REPO_MAP_R49.md",
            "docs/LUCYCLAW_DOC_BRIEF_R50A.md",
            "scripts/lucy_doc_brief_command.py",
        ],
    ),
    (
        re.compile(r"(?i)(?:health|status|gateway|telegram|service|log)"),
        [
            "docs/LUCYCLAW_HEALTH_BRIEF_R45.md",
            "docs/LUCYCLAW_HEALTH_REPORT_R44.md",
            "scripts/lucy_health_brief_command.py",
            "scripts/lucy_health_report_command.py",
            "scripts/lucy_service_status_command.py",
        ],
    ),
    (
        re.compile(r"(?i)(?:plan|risk|permission)"),
        [
            "docs/LUCYCLAW_CURRENT_STATE.md",
            "scripts/lucy_next_step_command.py",
            "scripts/lucy_capabilities_command.py",
        ],
    ),
)

BASE_REVIEW_FILES = [
    "docs/LUCYCLAW_CURRENT_STATE.md",
    "scripts/lucy_capabilities_command.py",
    "scripts/lucy_next_step_command.py",
]


def compact(text: str, limit: int = 160) -> str:
    collapsed = " ".join(text.strip().split())
    return collapsed[: limit - 3] + "..." if len(collapsed) > limit else collapsed


def normalize_request(raw: str) -> str:
    text = " ".join(raw.strip().split())
    if not text:
        raise ValueError("usage: provide a planning request")
    if len(text) > MAX_REQUEST_TEXT:
        raise ValueError(f"request must be <= {MAX_REQUEST_TEXT} chars")
    return text


def redact_request(text: str) -> str:
    replacements = (
        (r"(?i)\.env", "env-files"),
        (r"(?i)token(?:s)?|secret(?:s)?|api[_-]?keys?|password|access[_-]?token|refresh[_-]?token", "auth-material"),
        (r"(?i)\.agents|n8n_data|n8n_backups|workflow(?:s)?|credentials|database\.sqlite", "runtime-internals"),
        (r"(?i)b[oó]veda|personality|personalidad", "identity-zones"),
    )
    redacted = text
    for pattern, replacement in replacements:
        redacted = re.sub(pattern, replacement, redacted)
    return compact(redacted, 140)


def classify_risk(text: str) -> dict[str, object]:
    reasons: list[str] = []
    level = "GREEN"
    authorization = "not_required"
    if RED_ZONE_RE.search(text) or RED_ACTION_RE.search(text):
        level = "RED"
        authorization = "blocked"
        reasons.extend(
            [
                "Menciona zonas rojas o material sensible que LucyClaw no debe tocar desde la capa verde.",
                "Requiere intervención excepcional y política separada antes de cualquier ejecución.",
            ]
        )
    elif YELLOW_ACTION_RE.search(text):
        level = "YELLOW"
        authorization = "required"
        reasons.extend(
            [
                "Implica cambios de código, plugin, runtime o publicación, aunque el brief mismo siga siendo read-only.",
                "Necesita autorización explícita antes de instalar, reiniciar o aplicar cambios reales.",
            ]
        )
    elif GREEN_ACTION_RE.search(text):
        reasons.append("Se puede orientar con lectura, búsqueda y planificación sin mutar runtime ni repo.")
    else:
        reasons.append("La solicitud es ambigua; conviene revisar repo y riesgos antes de proponer ejecución.")
    return {
        "level": level,
        "authorization": authorization,
        "summary": compact(reasons[0], 120),
        "reasons": reasons[:MAX_REASONS],
    }


def summarize_permissions(text: str, risk_level: str) -> dict[str, object]:
    lowered = text.lower()
    edit_files = bool(re.search(r"\b(?:agregar|crear|editar|modificar|cambiar|actualizar|scaffold|command|comando)\b", lowered))
    install_plugin = "plugin" in lowered or "comando" in lowered or "command" in lowered
    restart_gateway = "reiniciar" in lowered or "restart" in lowered or install_plugin
    commit_push = edit_files or "commit" in lowered or "push" in lowered
    return {
        "edit_files": edit_files,
        "install_plugin": install_plugin and risk_level != "RED",
        "restart_gateway": restart_gateway and risk_level != "RED",
        "commit_push": commit_push and risk_level != "RED",
        "sudo": False,
        "touch_n8n": False,
        "touch_env": False,
        "touch_memory": False,
        "touch_vault_or_personality": False,
    }


def grouped_authorization_text(permissions: dict[str, object], risk_level: str) -> str:
    if risk_level == "RED":
        return "No agrupar autorización: la solicitud entra en zona roja y debe rediseñarse."
    requested: list[str] = []
    if permissions["edit_files"]:
        requested.append("edición de archivos")
    if permissions["install_plugin"]:
        requested.append("install/register de plugin")
    if permissions["restart_gateway"]:
        requested.append("un restart de gateway")
    if permissions["commit_push"]:
        requested.append("commit/push")
    if not requested:
        return "No requiere autorización extra: alcanza con capa verde read-only."
    return "Autorización agrupada recomendada: " + " + ".join(requested) + " + smoke + verificación final."


def collect_review_files(text: str) -> list[str]:
    seen: list[str] = []

    def add(path_text: str) -> None:
        if path_text in seen:
            return
        if (ROOT / path_text).exists():
            seen.append(path_text)

    for path_text in BASE_REVIEW_FILES:
        add(path_text)
    for pattern, candidates in FILE_RULES:
        if pattern.search(text):
            for candidate in candidates:
                add(candidate)
    add("docs/LUCYCLAW_REPO_MAP_R49.md")
    return seen[:MAX_ITEMS]


def build_checks(risk_level: str) -> list[str]:
    checks = [
        "git status --short --branch",
        "python3 scripts/verify_lucyclaw_green_commands.py",
        "python3 scripts/verify_lucyclaw_security_policy.py",
        "python3 scripts/lucy_next_step_command.py",
    ]
    if risk_level in {"YELLOW", "RED"}:
        checks.insert(1, "curl -sS http://127.0.0.1:18789/health")
    return checks


def build_tests(text: str, risk_level: str) -> list[str]:
    tests = [
        "python3 scripts/verify_lucyclaw_green_commands.py",
        "python3 scripts/verify_lucyclaw_security_policy.py",
    ]
    if re.search(r"(?i)(?:command|comando|plugin|slash)", text):
        tests.extend(
            [
                "python3 -m py_compile scripts/lucy_<name>_command.py",
                "node --check openclaw_plugins/lucy-<name>-command/index.js",
                "handler smoke del comando nuevo",
            ]
        )
    if risk_level == "YELLOW":
        tests.append("gateway health post-reload solo si hubo autorización amarilla")
    return tests[:MAX_ITEMS]


def build_acceptance(text: str, risk_level: str) -> list[str]:
    criteria = [
        "El resultado debe permanecer read-only hasta autorización explícita.",
        "QA1 y SEC1 deben quedar en ok antes de cualquier paso amarillo.",
        "No debe exponerse material sensible ni rutas rojas.",
    ]
    if re.search(r"(?i)(?:command|comando|plugin|slash)", text):
        criteria.extend(
            [
                "El comando nuevo debe devolver JSON compacto y determinístico.",
                "La ruta de plugin debe seguir el patrón LucyClaw con shell:false y timeout acotado.",
            ]
        )
    if risk_level == "RED":
        criteria.append("La solicitud debe redirigirse a una alternativa segura o quedar bloqueada.")
    return criteria[:MAX_ITEMS]


def build_risk_checks(text: str, risk_level: str) -> list[str]:
    checks = [
        "git status limpio",
        "QA1 ok",
        "SEC1 ok",
    ]
    if risk_level in {"YELLOW", "RED"}:
        checks.extend(
            [
                "gateway health ok/live",
                "plugin status si aplica",
                "postcheck documentado antes de ejecutar",
            ]
        )
    return checks[:MAX_ITEMS]


def build_rollback(risk_level: str) -> list[str]:
    if risk_level == "GREEN":
        return ["No aplica rollback: el tramo se limita a lectura y planificación."]
    if risk_level == "RED":
        return [
            "No ejecutar: rediseñar como alternativa verde o pedir autorización excepcional fuera de LucyClaw verde."
        ]
    return [
        "Guardar evidencia previa antes de cualquier cambio amarillo.",
        "Revertir commit o unlink del plugin según el tramo aprobado.",
        "Verificar gateway health, QA1 y SEC1 después del rollback.",
    ]


def build_safe_alternatives(text: str, risk_level: str) -> list[str]:
    alternatives = ["/repo_map", "/doc_brief", "/plan_brief"]
    if risk_level == "RED":
        alternatives.extend(
            [
                "reformular la tarea para evitar env-files, auth-material o runtime-internals",
                "/risk_check para separar qué parte es amarilla y cuál debe bloquearse",
            ]
        )
    elif risk_level == "YELLOW":
        alternatives.extend(
            [
                "/permission_brief para agrupar autorización antes de ejecutar",
                "preparar tramo R54 /change_plan antes de tocar runtime",
            ]
        )
    else:
        alternatives.append("/lucy_next_step para decidir si conviene avanzar")
    return alternatives[:MAX_ITEMS]
