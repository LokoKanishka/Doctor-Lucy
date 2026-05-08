# LucyClaw Operator Evidence Hardening

Date: 2026-05-08
Run: AG-OPERATOR-EVIDENCE-HARDEN

## What Failed After The First Fix

Diego's Telegram screenshot showed LucyClaw still saying:

- "Listo"
- "lo abri e intente darle play"
- "Si queres, sigo..."

The gateway logs showed the real cause:

- LucyClaw did call the `browser` tool.
- The tool failed repeatedly with `tab not found` / `no attached Chrome tabs for profile "chrome"`.
- LucyClaw then narrated the attempt as if it had effectively opened or played the video.

So the remaining bug was not missing browser access. It was false success reporting after a tool failure.

## Runtime Hardening Applied

Patched live OpenClaw config:

- `agents.defaults.bootstrapMaxChars`: `6000` -> `12000`
- `agents.defaults.contextTokens`: `16000` -> `32000`

Reason: `AGENTS.md` was being truncated before injection, and the active Telegram session still carried a low-context prompt.

Patched live and active-sandbox `AGENTS.md` by moving a hard anti-false-success rule to the top:

- If a tool fails, report the failure.
- If `browser` returns `tab not found`, `HTTP 404`, or `no attached Chrome tabs`, do not say the action succeeded.
- Never say "listo", "lo abri", "le di play", "lo guarde", or "lo envie" without post-action evidence.
- Do not say "si queres sigo" after a clear instruction.

Reset only the active Telegram direct session pointer:

- Removed `agent:main:direct:5154360597` from the OpenClaw session store.
- Kept the historical transcript file on disk.
- Next Telegram DM will create a fresh session with the new bootstrap/context settings.

## Backups

Backups were created before edits:

- `~/.openclaw/openclaw.json.bak.AG_OPERATOR_HARDEN_*`
- `~/.openclaw/workspace/AGENTS.md.bak.AG_OPERATOR_HARDEN_*`
- `~/.openclaw/sandboxes/agent-main-f331f052/AGENTS.md.bak.AG_OPERATOR_HARDEN_*`
- `~/.openclaw/agents/main/sessions/sessions.json.bak.AG_OPERATOR_HARDEN_*`

## Verification

Gateway and relay after restart:

- Gateway health: `{"ok":true,"status":"live"}`
- Relay: `OK`

Controlled runtime test:

Prompt asked LucyClaw to verify attached Chrome tabs without clicks, navigation, or screenshots.

Result:

```text
Bloqueo: no hay pestañas Chrome adjuntadas para `profile="chrome"` en `target="host"`.
```

The system prompt report showed:

- `bootstrapMaxChars: 12000`
- `AGENTS.md` injected fully, not truncated
- `contextTokens: 32000`

## Status

The active failure mode is now handled: when Chrome relay has no attached tab, LucyClaw should report the blocker instead of pretending the video was opened or played.

No n8n workflows, memory vault, `.env`, TTS, sqlite, screenshots, clicks, NotebookLM writes, or personal pages were touched.
