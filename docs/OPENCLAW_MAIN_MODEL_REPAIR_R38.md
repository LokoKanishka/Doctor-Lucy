
# Reporte CODEX-R38 — Reparación modelo OpenClaw principal

Fecha: 2026-04-29

Objetivo:
- Reparar la orientación del modelo principal de OpenClaw cambiando el default
  de `ollama/qwen2.5-coder:14b` a un candidato OpenAI/Codex saludable,
  con backup, diff, smoke y rollback documentados.

1) Estado inicial del repo
- rama: memoria/bunker
- HEAD: d84a009 (docs(openclaw): audit main runtime safely)
- status: untracked: .agents/archive_openclaw_scope_fix_20260429_153235/,
  docs/OPENCLAW_REBUILD_1A_PROFILE.md
- ahead/behind vs origin/memoria/bunker: 0/0

2) Estado oficial de modelos/auth (sanitizado)
- configPath: ~/.openclaw/openclaw.json
- defaultModel (antes): ollama/qwen2.5-coder:14b
- fallbacks (antes): [ollama/qwen3-coder:30b-a3b-q8_0, ollama/devstral-small-2:latest, google/gemini-2.5-flash]
- modelos disponibles (ej): openai-codex/gpt-5.4 (available: true), google/gemini-2.5-flash (available: true), ollama/... (local available)
- auth: provider `openai-codex` aparece con `oauth: 1` (OAuth profile present)

3) Candidato elegido
- `openai-codex/gpt-5.4` (aparece en `openclaw models list` y `models status` y tiene perfil OAuth activo)
- Prioridad aplicada: OpenAI/Codex ante local Ollama por criterios de tool-use y cloud availability.

4) Backup realizado
- backup_dir: ~/.openclaw/backups-r38-model-repair/20260429_223344
- openclaw.json respaldado: ~/.openclaw/backups-r38-model-repair/20260429_223344/openclaw.json.bak (present)
- auth metadata respaldada: agents-auth-profiles.tgz (present)

5) Comando usado y cambio
- comando ejecutado: `openclaw models set "openai-codex/gpt-5.4"`
- salida relevante: "Updated ~/.openclaw/openclaw.json\nDefault model: openai-codex/gpt-5.4"
- cambio aplicado: SÍ

6) Verificación post-cambio
- primary nuevo: openai-codex/gpt-5.4
- fallbacks (ahora): [ollama/qwen3-coder:30b-a3b-q8_0, ollama/devstral-small-2:latest, google/gemini-2.5-flash]
- `openclaw models status` (sanitizado) refleja `defaultModel: openai-codex/gpt-5.4`
- gateway health (http://127.0.0.1:18789/health): 200 {"ok":true,"status":"live"}
- Telegram real probado: NO
- MCP tocado: NO

7) Rollback
- necesario: NO
- aplicado: NO

8) Seguridad y cumplimiento de reglas
- tokens impresos: NO (salida sanitizada)
- .env tocado: NO
- servicios reiniciados: NO
- ~/.openclaw tocado: SÍ (openclaw.json modificado) con backup en backup_dir
- Doctora Lucy, memoria, n8n, bóveda, personalidad: NO tocadas

9) Próximo paso recomendado
- Si se desea: coordinar smoke adicional no-invasivo con OpenClaw (no Telegram) o
  ejecutar pruebas controladas de tool-use en staging antes de exponer a Telegram.

-- Fin del reporte --
