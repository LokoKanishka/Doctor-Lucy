# LucyClaw Doc Brief R50A

Date: 2026-05-02

## Objective

`R50A` adds `/doc_brief <path>`, a green read-only command that produces a compact deterministic brief for safe repo documents and command files.

The command is for orientation only. It helps Lucy decide what to read next without exposing sensitive zones or calling any external model.

## Examples

- `/doc_brief docs/LUCYCLAW_CURRENT_STATE.md`
- `/doc_brief docs/LUCYCLAW_REPO_MAP_R49.md`
- `/doc_brief scripts/lucy_repo_map_command.py`

## What It Summarizes

- `docs/*.md`
- `scripts/lucy_*_command.py`
- `scripts/verify_lucyclaw_*.py`
- `openclaw_plugins/lucy-*/index.js`
- `openclaw_plugins/lucy-*/openclaw.plugin.json`
- `openclaw_plugins/lucy-*/package.json`

The summary is heuristic and extractive:

- Markdown: H1, early headings, early bullets, and compact purpose text
- Python: docstring, top-level imports, functions, and command payload hints
- JavaScript: imports, registered command names, and argument behavior
- JSON: id/name/main keys and compact description

## What It Does Not Summarize

`/doc_brief` rejects:

- sensitive runtime data
- backups
- workflow files
- hidden env/config secrets
- binary files
- oversized files
- path traversal
- absolute paths

It does not print full file bodies or long logs.

## Security Limits

- deterministic local parsing only
- no LLM
- no OpenAI/Codex/Ollama calls
- no network dependency
- no write operations
- no repair
- no restart
- no install from the command
- no shell freeform execution
- `shell:false` in the plugin
- bounded file size and analyzed lines

## Relationship To Existing Green Commands

- `/repo_map` gives the high-level repo map
- `/fs_find` locates candidate files
- `/fs_grep` locates keywords in safe scopes
- `/fs_read` zooms into exact lines
- `/doc_brief` provides conceptual orientation before deeper reading

Recommended flow:

1. use `/repo_map` for map-level orientation
2. use `/fs_find` or `/fs_grep` to locate relevant files
3. use `/doc_brief` to decide whether the file is the right target
4. use `/fs_read` for exact bounded inspection

## Tests

```bash
python3 -m py_compile scripts/lucy_doc_brief_command.py
node --check openclaw_plugins/lucy-doc-brief-command/index.js
python3 scripts/lucy_doc_brief_command.py docs/LUCYCLAW_CURRENT_STATE.md
python3 scripts/lucy_doc_brief_command.py docs/LUCYCLAW_REPO_MAP_R49.md
python3 scripts/lucy_doc_brief_command.py ../.env
python3 scripts/verify_lucyclaw_security_policy.py
python3 scripts/verify_lucyclaw_green_commands.py
```

## Smoke Runtime

If local checks pass:

```bash
openclaw plugins install --link /home/lucy-ubuntu/Escritorio/doctora-lucy/openclaw_plugins/lucy-doc-brief-command
systemctl --user restart openclaw-gateway.service
```

Then verify:

- gateway health ok/live
- Telegram healthy
- plugin loaded
- `doc_brief` command registered
- `/doc_brief docs/LUCYCLAW_CURRENT_STATE.md` returns JSON through runtime
- `/lucy_capabilities` includes `/doc_brief`
- `/repo_map`, `/lucy_next_step`, `/health_brief`, `/fs_find`, and `/fs_grep` still work

## Rollback

Rollback is additive and bounded:

- unlink/remove the `lucy-doc-brief-command` plugin
- revert the `R50A` files
- rerun `SEC1` and `QA1`

No sensitive runtime state is modified by the command.

## Sensitive Non-Mutation

`/doc_brief` does not write files, does not alter services, does not change memory or workflow state, and does not broaden access beyond the safe allowlist.
