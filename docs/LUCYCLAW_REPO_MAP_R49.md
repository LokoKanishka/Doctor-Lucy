# LucyClaw Repo Map R49

Date: 2026-05-02

## Objective

`R49` adds `/repo_map`, a compact green read-only command for safe repo orientation inside LucyClaw/OpenClaw.

The goal is navigation, not execution. The command helps Lucy understand where to look next without adding repair, install, workflow, credential, or memory powers.

## What It Shows

- compact top-level repo structure
- Lucy command families
- key docs, command wrappers, QA scripts, and plugin directories
- safe next navigation hints
- explicit excluded zones

The payload is intentionally compact and bounded so it remains Telegram-friendly and predictable.

## What It Does Not Show

`/repo_map` does not read or expose:

- `.env`
- `.agents`
- `.git`
- `n8n_data/`
- `n8n_backups/`
- `workflows`
- `database.sqlite`
- `credentials`
- tokens
- heavy logs

It also does not mutate anything:

- no repair
- no restart
- no install
- no commit
- no memory touch
- no vault/personality touch

## Security Limits

The wrapper is bounded by design:

- no arguments accepted
- no shell freeform execution
- `shell:false` only
- no `sudo`
- no `exec` or `execSync`
- static allowlist for directories and key files
- existence checks only for known safe paths
- capped top-level output
- sensitive names filtered before output

## Relationship To Existing Green Commands

- `/repo_map` gives orientation
- `/fs_find` discovers safe file names
- `/fs_grep` finds safe bounded text matches
- `/fs_read` zooms into exact line ranges
- `/lucy_next_step` remains the advance gate before adding new capability work

Recommended flow:

1. use `/repo_map` for overview
2. use `/fs_find` or `/fs_grep` for target discovery
3. use `/fs_read` for exact bounded inspection

## Tests

Local checks for `R49`:

```bash
python3 -m py_compile scripts/lucy_repo_map_command.py
node --check openclaw_plugins/lucy-repo-map-command/index.js
python3 scripts/lucy_repo_map_command.py
python3 scripts/verify_lucyclaw_security_policy.py
python3 scripts/verify_lucyclaw_green_commands.py
```

## Smoke Runtime

If local checks pass, install and load the plugin:

```bash
openclaw plugins install --link /home/lucy-ubuntu/Escritorio/doctora-lucy/openclaw_plugins/lucy-repo-map-command
systemctl --user restart openclaw-gateway.service
```

Then verify:

- gateway health ok/live
- Telegram path healthy
- plugin loaded
- `repo_map` command registered
- `/repo_map` returns JSON through the runtime path
- `/lucy_capabilities` includes `/repo_map`
- `/lucy_next_step`, `/health_brief`, `/fs_find`, and `/fs_grep` still work

## Rollback

Rollback is simple because `R49` is additive:

- unlink/remove the `lucy-repo-map-command` plugin if needed
- revert the `R49` files
- rerun `SEC1` and `QA1`

No sensitive runtime state is modified by the command itself.

## Sensitive Non-Mutation

`/repo_map` is a navigation helper only.

It does not write files at runtime, does not alter services, does not change repo state, and does not broaden access to protected Lucy zones.
