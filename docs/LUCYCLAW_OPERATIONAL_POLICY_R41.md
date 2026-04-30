# LucyClaw Operational Policy R41

Date: 2026-04-30

## Objective

Define an operational policy for LucyClaw and Doctora Lucy that expands practical freedom without allowing destructive or irreversible behavior.

This document is design-only. It does not create new commands, modify OpenClaw config, send Telegram messages, or broaden filesystem access.

## Current Confirmed State

The current runtime baseline is:

- OpenClaw principal healthy
- Native Telegram healthy
- Current/default model: `openai-codex/gpt-5.4`
- Codex OAuth operational
- Deterministic command `/fs_read` operational in Telegram

Confirmed protection baseline:

- Memory untouched
- n8n untouched
- Vault untouched
- Personality untouched
- `.env` untouched
- Tokens not printed
- No `/bash`
- No `/exec`
- No `/mcp`
- No write path exposed

## Architectural Roles

### Doctora Lucy

Doctora Lucy is the judgment layer.

She decides:

- what matters
- what should not be touched
- how to explain
- when a risk requires authorization
- how to prioritize diagnosis and repair

### LucyClaw

LucyClaw is the operational layer.

It executes bounded capabilities such as:

- Telegram command handling
- status inspection
- safe file reads
- controlled search
- diagnostics
- report generation
- narrowly scoped repairs when explicitly permitted

### Operating Principle

The system should follow one rule:

```text
Lucy can observe, diagnose, summarize, search, prepare, open, send, and propose fixes.
Lucy cannot destroy, expose secrets, perform irreversible actions, or change protected areas without authorization.
```

## Current Capability Map

### Conversation and Session

Confirmed:

- Telegram conversation works
- `/new` works
- `/stop` works
- `/model status` works
- `/commands` works

### State and Model

Confirmed:

- session model visibility works
- default/current model reporting works
- Codex runtime is responsive

### Safe Read

Confirmed:

- `/fs_read` is exposed in Telegram
- `/fs_read` reads exact line ranges from allowed repo files
- read path is deterministic
- no write capability is attached

### Plugins and Tools

Confirmed:

- MCP registration alone does not guarantee Telegram exposure
- Telegram runtime did not expose MCP tools through `/tools`
- plugin command route did expose `/fs_read`

## Known Commands by Risk Class

This inventory is based on validated Telegram behavior, recent documentation, and command lists captured during R38-R40.

### Safe Query

These are suitable as default-safe session and runtime inspection commands:

- `/help`
- `/commands`
- `/tools`
- `/model status`
- `/models`
- `/status`
- `/context`
- `/whoami`
- `/export-session`

Expected policy:

- allowed by default
- no mutation
- no secrets in normal output

### Session Control

These affect the session but are not inherently destructive:

- `/new`
- `/stop`
- `/queue`
- `/fast`
- `/reasoning`

Expected policy:

- generally allowed
- safe for the active session
- should not alter protected system state

### Safe Bounded Read

Currently confirmed:

- `/fs_read`

Planned in the same family:

- `/fs_find`
- `/fs_grep`
- `/doc_summary`
- `/doc_summary_send`

Expected policy:

- allowed only in approved directories
- no `.env`
- no tokens
- no backups
- no SQLite/log dumps
- no `n8n_data`
- no path traversal

### Sensitive Operational Commands

These are useful but should not run freely:

- `/restart`
- `/agents`
- `/subagents`
- `/kill`
- `/steer`
- `/focus`
- `/unfocus`
- `/activation`
- `/approve`
- `/allowlist`
- `/elevated`

Expected policy:

- require explicit policy review
- some may remain blocked entirely in Telegram
- none should be treated as casually safe

### Plugin and External Capability Names Seen

These names are visible in current docs or command inventories and should be treated as capability labels, not automatically approved actions:

- `/coding_agent`
- `/github`
- `/gh_issues`
- `/tmux`
- `/mcporter`
- `/skill_creator`
- `/healthcheck`
- `/summarize`
- `/gemini`
- `/weather`
- `/tts`
- `/openai_whisper`
- `/nano_pdf`
- `/himalaya`
- `/wacli`
- `/sonoscli`
- `/openhue`

Policy note:

- visibility is not approval
- each command family needs explicit classification before trusted operational use

## Permission Levels

### Green

Allowed without asking Diego first.

Examples:

- machine status inspection
- limited log inspection
- allowed file reading
- allowed document summarization
- public web lookup
- diagnostics without changes
- non-sensitive Telegram reports

Green actions should be:

- reversible by nature
- read-only or equivalent
- bounded in scope
- logged or explainable

### Yellow

Lucy may prepare the action, but should ask before applying it.

Examples:

- restart allowed services
- edit OpenClaw config
- modify scripts
- install dependencies
- send large documents
- open or focus desktop windows
- apply small repairs

Yellow actions should require:

- clear plan
- backup if config is touched
- rollback path
- short pre-action report
- verification after action

### Red

Forbidden unless Diego gives explicit authorization.

Examples:

- delete files
- mass overwrite
- touch `.env`
- touch tokens
- touch memory
- touch n8n production
- touch vault
- touch personality
- use `sudo`
- free shell
- sensitive data exfiltration
- payments
- external publication
- irreversible changes

Red actions should default to:

- refuse
- explain why
- prepare a safer plan instead

## Safety Limits

The operational constitution should remain anchored in four hard limits:

1. No destruction.
2. No secret exposure.
3. No irreversible actions without authorization.
4. No dangerous autonomy without reporting.

This is the difference between "capable" and "reckless".

## What LucyClaw Can Do Without Diego

Within the proposed Green zone, LucyClaw should eventually be able to:

- inspect GPU, RAM, CPU, disk, processes
- inspect service status
- read allowed logs
- read and summarize approved documents
- search allowed files
- search public web content
- send non-sensitive reports by Telegram
- prepare fixes and explain them

## What Requires Permission

Before acting, LucyClaw should pause and ask for approval when the action would:

- restart a service
- change config
- edit code
- install software
- operate desktop controls
- send large or potentially sensitive documents
- apply a repair instead of only diagnosing it

## What Must Stay Forbidden

Forbidden by default:

- deleting data
- exposing secrets
- editing protected Lucy subsystems
- enabling broad shell access
- broadening filesystem write access
- publishing externally
- any irreversible operation without explicit approval

## Roadmap R42-R47

### R42

Machine status, read-only:

- `/sys_status`
- `/gpu_status`
- `/disk_status`
- `/process_status`

### R43

Service and log diagnostics:

- `/service_status`
- `/log_tail`
- `/openclaw_health`
- `/n8n_health`
- `/docker_status`
- `/ollama_status`

### R44

Filesystem and document ergonomics:

- `/fs_find`
- `/fs_grep`
- `/doc_summary`
- `/doc_summary_send`

### R45

Web capabilities:

- `/web_search`
- `/web_read`
- `/web_summary`

### R46

Controlled repair protocols:

- `/repair_openclaw`
- `/repair_telegram`
- `/repair_n8n`
- `/repair_ollama`

Repair policy should always follow:

1. diagnosis
2. plan
3. backup if needed
4. bounded action
5. verification
6. report

### R47

Safe desktop observation before interaction:

- `/window_list`
- `/screenshot`
- `/open_folder`

Initial constraint:

- no free mouse
- no free keyboard
- no broad desktop autonomy

## Final Recommendation

The right path is not "give Lucy shell" and not "keep Lucy trapped in a demo".

The right path is a growing board of explicit, auditable, bounded commands:

- high freedom
- low destructiveness
- clear authorization boundaries
- strong evidence trail

`/fs_read` is the first proven example of that model.

The next recommended step is R42: machine-status commands in the Green zone, because they increase operational usefulness without crossing into destructive behavior.
