# Backup Instructions

Fecha: 2026-04-30

## Alcance

Este documento registra el backup previo a la integracion del MCP read-only `lucy-fs-readonly` en el OpenClaw principal.

No se tocaron memoria, n8n, boveda, personalidad, `.env`, tokens, Telegram legacy ni scripts ajenos a OpenClaw.

## Backup creado

- Directorio: `~/.openclaw/backups-mcp-20260430_003026`
- Config OpenClaw: `~/.openclaw/backups-mcp-20260430_003026/openclaw.json.bak`
- Metadata de agentes/auth: `~/.openclaw/backups-mcp-20260430_003026/agents-auth-profiles.tgz`

OpenClaw tambien genero su propio backup automatico al guardar la config:

- `~/.openclaw/openclaw.json.bak`

## Restaurar solo configuracion

Para revertir el registro MCP sin tocar metadata de auth:

```bash
cp -a ~/.openclaw/backups-mcp-20260430_003026/openclaw.json.bak ~/.openclaw/openclaw.json
```

Despues verificar:

```bash
openclaw mcp list --json
openclaw mcp show --json
```

## Restaurar metadata de agentes/auth

No restaurar este archivo salvo necesidad explicita y decision documentada.

```bash
tar -xzf ~/.openclaw/backups-mcp-20260430_003026/agents-auth-profiles.tgz -C ~/.openclaw
```

## Nota de seguridad

Los backups pueden contener configuracion sensible de OpenClaw. No deben imprimirse ni compartirse.
