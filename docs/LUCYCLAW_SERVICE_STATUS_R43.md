# LucyClaw Service Status R43

Date: 2026-04-30

## Objective

Implement deterministic Green-level service and bounded-log commands for LucyClaw over OpenClaw Telegram, without enabling shell freedom, repairs, write access, or sensitive Doctora Lucy access.

R43 extends R41/R42 by adding host service visibility after the R42 machine-status commands proved the read-only plugin pattern.

## Commands Implemented

The following Telegram/OpenClaw plugin commands were added:

- `/openclaw_health`
- `/docker_status`
- `/ollama_status`
- `/n8n_health`
- `/service_status`
- `/log_tail`

## Wrapper

Created:

- `scripts/lucy_service_status_command.py`

Supported local invocations:

```bash
python3 scripts/lucy_service_status_command.py openclaw_health
python3 scripts/lucy_service_status_command.py docker_status
python3 scripts/lucy_service_status_command.py ollama_status
python3 scripts/lucy_service_status_command.py n8n_health
python3 scripts/lucy_service_status_command.py service_status
python3 scripts/lucy_service_status_command.py log_tail
```

Design constraints:

- Python stdlib first
- fixed read-only subprocess calls only
- `shell=False` always
- bounded timeouts
- compact JSON output
- no write path
- no `.env`
- no tokens
- no workflow or credential reads
- no repair actions

## Data Returned

### `/openclaw_health`

Returns:

- gateway health from `http://127.0.0.1:18789/health`
- `systemctl --user` status for `openclaw-gateway.service` when available
- model status from `openclaw models status --json` when available without secrets
- general status: `ok`, `warn`, or `error`

### `/docker_status`

Returns:

- Docker CLI availability
- Docker daemon response state
- bounded container rows with name, status, image, and ports

No containers are started, stopped, modified, or inspected deeply.

### `/ollama_status`

Returns:

- local port `11434` response state
- `/api/tags` response state
- up to ten detected model names

No models are loaded, pulled, or downloaded.

### `/n8n_health`

Returns:

- visible n8n container/service hints
- local HTTP response state on known n8n ports
- basic status only

No workflows, credentials, databases, or n8n internals are read.

### `/service_status`

Returns status for a fixed allowlist only:

- `openclaw-gateway.service`
- `docker`
- `ollama`
- `n8n`

It does not accept arbitrary service names.

### `/log_tail`

Returns sanitized bounded logs only for:

- `openclaw-gateway.service`

Limits:

- maximum 80 lines
- long lines truncated
- sensitive key names redacted
- no full logs

## Plugin

Created:

- `openclaw_plugins/lucy-service-status-command/package.json`
- `openclaw_plugins/lucy-service-status-command/openclaw.plugin.json`
- `openclaw_plugins/lucy-service-status-command/index.js`

The plugin registers deterministic slash commands only.

It does not expose:

- `/bash`
- `/exec`
- `/mcp`
- write helpers
- free-form shell execution
- arbitrary service/log arguments

Each command calls the Python wrapper with a fixed subcommand and no arbitrary shell arguments.

## Backup

Before updating OpenClaw principal config, create a backup under:

```text
~/.openclaw/backups-r43-service-status/<timestamp>
```

Back up:

- `openclaw.json.bak`
- `agents-auth-profiles.tgz` when `~/.openclaw/agents` exists

Rollback path:

```bash
cp -a ~/.openclaw/backups-r43-service-status/<timestamp>/openclaw.json.bak ~/.openclaw/openclaw.json
openclaw gateway restart
```

Do not restore `agents-auth-profiles.tgz` unless explicitly authorized.

Backup created during R43:

```text
~/.openclaw/backups-r43-service-status/20260430_123740
```

OpenClaw also wrote its own immediate config backup:

```text
~/.openclaw/openclaw.json.bak
```

## Local Tests

Required tests:

- `python3 -m py_compile scripts/lucy_service_status_command.py`
- `node --check openclaw_plugins/lucy-service-status-command/index.js`
- all six wrapper subcommands

Local tests passed:

- `python3 -m py_compile scripts/lucy_service_status_command.py`
- `node --check openclaw_plugins/lucy-service-status-command/index.js`
- `python3 scripts/lucy_service_status_command.py openclaw_health`
- `python3 scripts/lucy_service_status_command.py docker_status`
- `python3 scripts/lucy_service_status_command.py ollama_status`
- `python3 scripts/lucy_service_status_command.py n8n_health`
- `python3 scripts/lucy_service_status_command.py service_status`
- `python3 scripts/lucy_service_status_command.py log_tail`

Observed local behavior:

- OpenClaw gateway health returned `200 {"ok":true,"status":"live"}`
- OpenClaw model default returned `openai-codex/gpt-5.4`
- Docker daemon responded and containers were listed in bounded form
- Ollama `/api/tags` responded and model names were limited to ten
- n8n containers were visible and local mapped ports `5688` and `6969` responded
- service status used only the fixed allowlist
- log tail returned at most 80 sanitized, truncated lines

OpenClaw plugin load:

- plugin status: loaded
- commands registered:
  - `openclaw_health`
  - `docker_status`
  - `ollama_status`
  - `n8n_health`
  - `service_status`
  - `log_tail`
- gateway health after restart: `200 {"ok":true,"status":"live"}`

## Telegram Validation

Required manual checks:

- `/commands`
- `/openclaw_health`
- `/docker_status`
- `/ollama_status`
- `/n8n_health`
- `/service_status`
- `/log_tail`

Expected behavior:

- commands appear under plugin commands
- responses are compact JSON
- no secrets or tokens are exposed
- logs are bounded and sanitized
- no repair is attempted

Telegram validation status:

- Manual validation completed from Telegram after plugin load.
- `/log_tail` returned compact JSON with bounded `openclaw-gateway.service` lines.
- Observed Telegram send confirmations from `2026-04-30 12:42:49` through `12:43:44` for the command replies.
- A later local journal check also showed replies through `12:44:19`.
- The pasted `/log_tail` content contained only gateway send confirmations and did not expose tokens or secrets.
- The command routed through the plugin path instead of conversational fallback.

## Security Boundaries Preserved

Required confirmations:

- memory untouched
- n8n workflows untouched
- vault untouched
- personality untouched
- `.env` untouched
- tokens not printed
- no shell freedom
- no `sudo`
- no repair actions
- no writing outside R43 files and required OpenClaw plugin registration

## Result

R43 is intended to give LucyClaw service and log observability while staying inside the Green zone defined by R41.

If Telegram replies conversationally instead of returning JSON, the plugin is not loaded or the command is not registered yet.
