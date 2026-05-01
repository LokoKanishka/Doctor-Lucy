# LucyClaw Filesystem Search - R47

Date: 2026-05-01

## Objective

`R47` adds two bounded read-only filesystem search commands for LucyClaw:

- `/fs_find`
- `/fs_grep`

Both reuse the existing safe helper logic from `scripts/lucy_fs_readonly.py`.

## Commands

### `/fs_find <query>`

Find allowed repo files by name fragment.

Examples:

- `/fs_find health`
- `/fs_find lucy_capabilities`
- `/fs_find LUCYCLAW`

### `/fs_grep <query> [scope]`

Search text within allowed repo files, optionally restricting the search scope.

Examples:

- `/fs_grep shell:false`
- `/fs_grep health_report scripts`
- `/fs_grep "no sudo" docs`

## Security Limits

These commands stay read-only and bounded:

- no writes
- no `.env`
- no tokens
- no `.git/`
- no `.agents/`
- no `n8n_data/`
- no `n8n_backups/`
- no SQLite or heavy log files
- no path traversal
- no absolute paths
- no shell freedom

## Relation To `/fs_read`

- `/fs_read` reads an exact line range from a known allowed file
- `/fs_find` discovers allowed file names
- `/fs_grep` finds bounded text matches inside allowed files

Together they improve repo inspection without leaving the green read-only boundary.

## Tests

Local checks:

```bash
python3 -m py_compile scripts/lucy_fs_search_command.py
node --check openclaw_plugins/lucy-fs-search-command/index.js
python3 scripts/lucy_fs_search_command.py find health
python3 scripts/lucy_fs_search_command.py grep delegate_mission scripts
python3 scripts/verify_lucyclaw_security_policy.py
python3 scripts/verify_lucyclaw_green_commands.py
```

## Runtime Smoke

After plugin installation and one authorized restart:

- verify plugin `lucy-fs-search-command` is loaded
- verify commands `fs_find` and `fs_grep` are registered
- verify `/fs_find health`
- verify `/fs_grep delegate_mission scripts`

## Rollback

Rollback is file-level revert plus plugin reload if the plugin has already been installed.

## No-Mutation Note

`R47` does not write repo files through the command surface and does not touch runtime-sensitive zones such as memory, vault, personality, `.env`, or `n8n` workflows.
