# AG-TELEGRAM-HOST-BROWSER-FIX

Date: 2026-05-08

## Objective

Make LucyClaw Telegram agent runs able to read a manually attached Chrome tab
through OpenClaw Browser Relay, instead of replying that the browser is
unavailable when Diego asks about a real tab such as NotebookLM.

## Root Cause

The Chrome extension relay and `chrome` profile were healthy, and the attached
NotebookLM tab was visible through the CLI. The blocker was the effective tool
pipeline for agent `main`:

- `browser.enabled` was missing, so gateway browser capability wiring was not
  explicitly enabled.
- The global tool deny list included `browser`.
- Agent `main` had sandbox allow entries for local machine tools, but not for
  the host browser path.
- The default sandbox deny list still denied `browser`; sandbox deny wins before
  allow.
- The implicit `coding` tool profile filtered UI tools before the agent allowlist
  could expose `browser`.

## Runtime Fix

Backed up `~/.openclaw/openclaw.json` before every config mutation and applied a
narrow runtime policy for agent `main`:

- `browser.enabled = true`
- `agents.defaults.sandbox.browser.allowHostControl = true`
- removed `browser` from global `tools.deny`
- set `agents.list[main].tools.profile = "full"`
- set an explicit `agents.list[main].tools.allow` matching the existing coding
  and Lucy machine tool surface plus `browser`
- set `agents.list[main].tools.sandbox.tools.allow` to include `browser`
- set `agents.list[main].tools.sandbox.tools.deny` to preserve sensitive denies
  while excluding `browser`

This keeps sandboxing enabled and does not enable host access globally beyond
the browser host-control gate needed by the Chrome extension relay.

## Evidence

- Gateway health: `{"ok":true,"status":"live"}`
- Browser relay health: `OK`
- `openclaw browser tabs --browser-profile chrome` showed:
  `The Symposium or On Love - NotebookLM`
- `openclaw browser snapshot --browser-profile chrome` read NotebookLM text,
  including `El Banquete`, `Amor`, `Sócrates`, `Diotima`, and `Alcibíades`.
- `openclaw sandbox explain` after the fix showed `browser` in agent allow and
  no longer in agent deny.
- Local Telegram-equivalent runtime test returned:
  `The Symposium or On Love - NotebookLM`
- The system prompt report for that run included the `browser` tool.

## Safety Notes

No n8n workflow, memory, vault, `.env`, TTS, voice payload, or sqlite database
was touched. No screenshots, clicks, page writes, JavaScript execution, or
sensitive browsing were performed.

