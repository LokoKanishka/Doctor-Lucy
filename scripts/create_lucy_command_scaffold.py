#!/usr/bin/env python3
"""Generate a safe LucyClaw command scaffold without touching runtime."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9_]+$")
COMMAND_TIMEOUT_MS = 10000
COMPAT_PLUGIN_API = ">=2026.3.24-beta.2"
COMPAT_GATEWAY = "2026.3.24-beta.2"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def validate_name(raw: str) -> str:
    if not NAME_RE.fullmatch(raw):
        raise ValueError("name must use only lowercase letters, numbers, and underscores")
    return raw


def kebab_name(name: str) -> str:
    return name.replace("_", "-")


def title_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("_"))


def wrapper_path(root: Path, name: str) -> Path:
    return root / "scripts" / f"lucy_{name}_command.py"


def plugin_dir(root: Path, name: str) -> Path:
    return root / "openclaw_plugins" / f"lucy-{kebab_name(name)}-command"


def doc_path(root: Path, name: str, stage: str) -> Path:
    return root / "docs" / f"LUCYCLAW_{name.upper()}_{stage}.md"


def build_wrapper(name: str, stage: str, description: str) -> str:
    return f"""#!/usr/bin/env python3
\"\"\"{description}\"\"\"

from __future__ import annotations

import json
import sys


PAYLOAD = {{
    "ok": True,
    "command": "{name}",
    "stage": "{stage}",
    "message": "{description}",
}}


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        return emit(
            {{
                "ok": False,
                "command": "{name}",
                "error": "arguments are not supported",
            }},
            2,
        )
    return emit(PAYLOAD)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
"""


def build_package_json(name: str) -> str:
    plugin_name = f"lucy-{kebab_name(name)}-command"
    payload = {
        "name": plugin_name,
        "version": "1.0.0",
        "type": "module",
        "private": True,
        "openclaw": {
            "extensions": ["./index.js"],
            "compat": {
                "pluginApi": COMPAT_PLUGIN_API,
                "minGatewayVersion": COMPAT_GATEWAY,
            },
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def build_plugin_json(name: str, description: str) -> str:
    plugin_id = f"lucy-{kebab_name(name)}-command"
    payload = {
        "id": plugin_id,
        "name": f"Lucy {title_name(name)} Command",
        "description": description,
        "main": "./index.js",
        "configSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {},
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def build_index_js(name: str, description: str) -> str:
    plugin_id = f"lucy-{kebab_name(name)}-command"
    python_script = f"lucy_{name}_command.py"
    return f"""import {{ spawn }} from "node:child_process";
import {{ dirname, resolve }} from "node:path";
import {{ fileURLToPath }} from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/{python_script}");
const TIMEOUT_MS = {COMMAND_TIMEOUT_MS};

function runCommand() {{
  return new Promise((resolve, reject) => {{
    const child = spawn("python3", [COMMAND], {{
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      timeout: TIMEOUT_MS,
    }});
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {{
      stdout += chunk;
    }});
    child.stderr.on("data", (chunk) => {{
      stderr += chunk;
    }});
    child.on("error", reject);
    child.on("close", (code) => {{
      const text = stdout.trim();
      if (!text) {{
        reject(new Error(stderr.trim() || `{name} exited ${{code}}`));
        return;
      }}
      resolve(text);
    }});
  }});
}}

export default {{
  id: "{plugin_id}",
  name: "Lucy {title_name(name)} Command",
  description: "{description}",
  register(api) {{
    api.registerCommand({{
      name: "{name}",
      description: "{description}",
      acceptsArgs: false,
      async handler() {{
        try {{
          const text = await runCommand();
          return {{ text }};
        }} catch (error) {{
          return {{
            text: JSON.stringify({{
              ok: false,
              command: "{name}",
              error: error instanceof Error ? error.message : String(error),
            }}),
          }};
        }}
      }},
    }});
  }},
}};
"""


def build_doc(name: str, stage: str, description: str) -> str:
    slash = f"/{name}"
    plugin_id = f"lucy-{kebab_name(name)}-command"
    return f"""# LucyClaw {title_name(name)} - {stage}

Date: 2026-05-01

## Objective

Scaffold template for `{slash}` using the safe LucyClaw command pattern.

## Command

- slash command: `{slash}`
- plugin id: `{plugin_id}`
- wrapper: `scripts/lucy_{name}_command.py`
- description: {description}

## Design

- Python wrapper with compact JSON output
- separate OpenClaw plugin
- relative path resolution via `import.meta.url` + `resolve`
- `spawn(..., shell:false)`
- bounded timeout
- `acceptsArgs:false` by default

## Security Limits

- no shell freedom
- no sudo
- no `.env`
- no memory
- no n8n workflows
- no automatic repair
- no runtime mutation

## Tests

- `python3 -m py_compile scripts/lucy_{name}_command.py`
- `node --check openclaw_plugins/{plugin_id}/index.js`
- `python3 scripts/verify_lucyclaw_green_commands.py`
- `python3 scripts/verify_lucyclaw_security_policy.py`

## Reload / Rollback

- plugin installation is not part of this scaffold tranche
- gateway restart requires explicit yellow authorization
- rollback is file-level revert before installation

## No-Mutation Note

This scaffold does not install plugins, restart OpenClaw, or add a live capability by itself.

## QA Gates

After generating and adapting a real command, run:

```bash
python3 scripts/verify_lucyclaw_green_commands.py
python3 scripts/verify_lucyclaw_security_policy.py
```
"""


def planned_files(root: Path, name: str, stage: str) -> list[Path]:
    plugdir = plugin_dir(root, name)
    return [
        wrapper_path(root, name),
        plugdir / "package.json",
        plugdir / "openclaw.plugin.json",
        plugdir / "index.js",
        doc_path(root, name, stage),
    ]


def ensure_writable(paths: list[Path], force: bool) -> None:
    if force:
        return
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite existing files: {', '.join(existing)}")


def write_files(root: Path, name: str, stage: str, description: str, force: bool) -> list[str]:
    paths = planned_files(root, name, stage)
    ensure_writable(paths, force)
    contents = {
        paths[0]: build_wrapper(name, stage, description),
        paths[1]: build_package_json(name),
        paths[2]: build_plugin_json(name, description),
        paths[3]: build_index_js(name, description),
        paths[4]: build_doc(name, stage, description),
    }
    for path, content in contents.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return [str(path.relative_to(root).as_posix()) for path in paths]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a safe LucyClaw command scaffold.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--output-root", default=str(ROOT))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv[1:])
        name = validate_name(args.name)
        stage = args.stage.strip()
        description = args.description.strip()
        if not stage:
            raise ValueError("stage must not be empty")
        if not description:
            raise ValueError("description must not be empty")
        output_root = Path(args.output_root).resolve()
        files = [str(path.relative_to(output_root).as_posix()) for path in planned_files(output_root, name, stage)]
        plugin_id = f"lucy-{kebab_name(name)}-command"
        payload = {
            "ok": True,
            "command": "create_lucy_command_scaffold",
            "dry_run": args.dry_run,
            "plugin_id": plugin_id,
            "slash_command": f"/{name}",
            "files_planned": files,
        }
        if args.dry_run:
            return emit(payload)
        payload["files_created"] = write_files(output_root, name, stage, description, args.force)
        return emit(payload)
    except (ValueError, FileExistsError) as exc:
        return emit({"ok": False, "command": "create_lucy_command_scaffold", "error": str(exc)}, 2)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
