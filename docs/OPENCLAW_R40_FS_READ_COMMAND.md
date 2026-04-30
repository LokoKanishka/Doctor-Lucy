# R40 - Deterministic fs_read Command

Date: 2026-04-30

## Objective

Implement a deterministic read-only filesystem command for OpenClaw Telegram, without relying on model-driven MCP tool choice.

The command is intentionally narrow:

```text
/fs_read <relative-path> <start> <end>
```

It reuses the hardened `scripts/lucy_fs_readonly.py` path and reads only allowed files inside the Doctor-Lucy repo.

## Context

R39 confirmed that `lucy-fs-readonly` was registered as an MCP server and worked from local OpenClaw agent mode, but Telegram did not expose the MCP tools in `/tools compact` or `/tools verbose`.

For R40, the chosen design is a deterministic OpenClaw plugin command instead of another prompt-based attempt.

Official docs considered:

- `openclaw mcp set/list/show` registers client MCP server definitions but does not prove Telegram runtime tool exposure.
- User-invocable slash command behavior can expose commands directly to channel users.
- A deterministic command avoids depending on the model deciding to call a filesystem tool.

## Protection Scope

Doctora Lucy protection was preserved:

- Memory touched: NO
- n8n touched: NO
- Vault touched: NO
- Personality touched: NO
- `.env` touched: NO
- Tokens printed: NO
- Unrelated scripts touched: NO
- `/bash` used from Telegram: NO
- `/exec` used from Telegram: NO
- `/mcp` used from Telegram: NO
- Write test attempted: NO
- Filesystem scope expanded: NO

## Implementation

Created:

- `scripts/lucy_fs_read_command.py`
- `openclaw_plugins/lucy-fs-readonly-command/package.json`
- `openclaw_plugins/lucy-fs-readonly-command/openclaw.plugin.json`
- `openclaw_plugins/lucy-fs-readonly-command/index.js`
- `openclaw_plugins/lucy-fs-readonly-command/skills/fs_read/SKILL.md`

The wrapper:

- Accepts `path start end`.
- Calls `scripts/lucy_fs_readonly.py read_lines`.
- Uses `subprocess.run(..., shell=False)` from Python and `spawn(..., shell:false)` from the plugin.
- Returns compact JSON.
- Preserves all guardrails from `lucy_fs_readonly.py`.

The OpenClaw plugin registers:

- Plugin command: `fs_read`
- Tool helper: `fs_read_command`

The command route is the operative path for Telegram.

## Backup

Before modifying the OpenClaw principal config, a backup was created:

```text
~/.openclaw/backups-r40-fs-read-command/20260430_020627
```

Backed up:

- `openclaw.json.bak`
- `agents-auth-profiles.tgz`

Rollback for OpenClaw config:

```bash
cp -a ~/.openclaw/backups-r40-fs-read-command/20260430_020627/openclaw.json.bak ~/.openclaw/openclaw.json
openclaw gateway restart
```

Do not restore `agents-auth-profiles.tgz` unless explicitly authorized.

## Local Tests

Passed:

- `python3 -m py_compile scripts/lucy_fs_readonly.py scripts/lucy_fs_read_command.py`
- `node --check openclaw_plugins/lucy-fs-readonly-command/index.js`
- Direct wrapper read:

```json
{"ok":true,"path":"scripts/lucy_openclaw_bridge.py","start":138,"end":138,"lines":[{"line":138,"text":"def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):"}]}
```

Rejections passed:

- `../.bashrc`: rejected with exit `2`
- `.env`: rejected with exit `2`
- `n8n_data/daemon.pid`: rejected with exit `2`

## OpenClaw Registration

The plugin was installed locally into OpenClaw principal using the official plugin install path.

The gateway was restarted only to load the plugin, as requested by OpenClaw after plugin installation.

Post-load inspection showed:

- Plugin status: loaded
- Command registered: `fs_read`
- Tool helper registered: `fs_read_command`
- Gateway health: `200 {"ok":true,"status":"live"}`

## Telegram Validation

Diego validated the command manually from Telegram.

Result:

- `/fs_read` exposed in Telegram: YES
- Location: `/commands` page `9/9`, under `Plugins`
- Command sent:

```text
/fs_read scripts/lucy_openclaw_bridge.py 138 138
```

Telegram response:

```json
{"ok":true,"path":"scripts/lucy_openclaw_bridge.py","start":138,"end":138,"lines":[{"line":138,"text":"def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):"}]}
```

Verification:

- Exact read: YES
- Returned line: `138`
- Returned text: `def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):`
- Write performed: NO

## Result

`/fs_read` is operational from Telegram as a deterministic, read-only command.

This does not grant general filesystem access. It only exposes the hardened line-reading path already validated in R29/R29B.

## Recommendation

Pause here.

Do not expand filesystem access, add write tools, enable `/bash`, enable `/exec`, or use `/mcp`.

The next safe step, only if Diego authorizes it, would be a planning-only R41 for command ergonomics and audit logging, without broadening permissions.
