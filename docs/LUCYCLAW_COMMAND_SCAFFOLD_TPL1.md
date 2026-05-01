# LucyClaw Command Scaffold - TPL1

Date: 2026-05-01

## Objective

`TPL1` adds a safe scaffold generator so future LucyClaw commands start from the established secure pattern instead of being assembled manually each time.

## Files

- `scripts/create_lucy_command_scaffold.py`
- `scripts/verify_lucy_command_scaffold.py`

## Why It Exists

The Lucy pattern is now stable:

- Python wrapper
- separate OpenClaw plugin
- `package.json`
- `openclaw.plugin.json`
- `index.js` with `spawn(..., shell:false)`
- relative command resolution
- bounded timeout
- compact JSON
- tranche doc
- QA1 plus SEC1 gates

`TPL1` reduces copy-paste drift and makes future tranches safer by default.

## Dry Run

Use dry-run first:

```bash
python3 scripts/create_lucy_command_scaffold.py \
  --name example_status \
  --stage RXX \
  --description "Example read-only status command" \
  --dry-run
```

Dry-run returns JSON with:

- `ok`
- `command`
- `dry_run`
- `files_planned`
- `plugin_id`
- `slash_command`

Dry-run does not write files.

## Real Generation

Future tranches can generate a new command scaffold with:

```bash
python3 scripts/create_lucy_command_scaffold.py \
  --name example_status \
  --stage RXX \
  --description "Example read-only status command"
```

It creates:

- `scripts/lucy_example_status_command.py`
- `openclaw_plugins/lucy-example-status-command/package.json`
- `openclaw_plugins/lucy-example-status-command/openclaw.plugin.json`
- `openclaw_plugins/lucy-example-status-command/index.js`
- `docs/LUCYCLAW_EXAMPLE_STATUS_RXX.md`

## Safety Rules

The generator enforces:

- safe command names only
- no overwrite by default
- `acceptsArgs:false` by default
- `spawn(..., shell:false)`
- no legacy absolute runtime paths
- no `exec` / `execSync`
- no runtime mutation

## What It Does Not Do

`TPL1` does not:

- install plugins
- restart OpenClaw
- create a live capability by itself
- bypass yellow authorization

## Verification

Run:

```bash
python3 scripts/verify_lucy_command_scaffold.py
python3 scripts/verify_lucyclaw_green_commands.py
python3 scripts/verify_lucyclaw_security_policy.py
```

## Rule For Future Tranches

After generating and adapting a real Lucy command:

1. run `QA1`
2. run `SEC1`
3. install or restart only with explicit yellow authorization
