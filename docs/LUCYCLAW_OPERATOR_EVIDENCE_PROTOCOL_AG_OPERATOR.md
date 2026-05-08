# LucyClaw Operator Evidence Protocol

Date: 2026-05-08
Run: AG-OPERATOR-EVIDENCE

## Problem

Telegram could already reach host Chrome through OpenClaw Browser Relay, but LucyClaw was still behaving like a weak browser operator:

- It narrated options instead of executing clear instructions.
- It asked "si queres sigo" after Diego had already asked for the next action.
- It claimed "listo", "lo abri" or "le di play" without post-action evidence.
- It used brittle YouTube search strategies for channel/program/date requests.
- It had an identity instruction claiming unrestricted elevated access, which encouraged overpromising.

## Decision

Do not enable every tool globally. The Telegram runtime already exposes `browser`; the issue is operational discipline, not raw tool count.

The durable fix is a mandatory observe-act-verify loop and domain runbooks for browser, YouTube, NotebookLM, Spotify, and exportable deliverables.

## Runtime Changes

Backed up and patched the live OpenClaw workspace instructions:

- `~/.openclaw/workspace/AGENTS.md`
- `~/.openclaw/workspace/TOOLS.md`
- `~/.openclaw/workspace/IDENTITY.md`

Also patched the active sandbox copies for immediate Telegram effect:

- `~/.openclaw/sandboxes/agent-main-f331f052/AGENTS.md`
- `~/.openclaw/sandboxes/agent-main-f331f052/TOOLS.md`
- `~/.openclaw/sandboxes/agent-main-f331f052/IDENTITY.md`

## New Operator Contract

LucyClaw must not say "listo", "lo abri", "le di play", "lo guarde", "lo envie" or equivalent without evidence observed after the action.

Required loop:

1. Observe the real resource.
2. Choose the next concrete step.
3. Act once.
4. Observe again.
5. Recover once if needed.
6. Report evidence or the exact blocker.

## Browser Rule

For manually attached Chrome tabs, LucyClaw should use:

- `browser`
- `profile="chrome"`
- `target="host"` when host control is allowed
- `tabs`/`snapshot` before action
- fresh `snapshot` after navigation, click, typing, or playback attempts

Screenshots are not the default. Snapshot is preferred unless visual verification is necessary.

## YouTube Rule

For channel/program/date requests:

- Separate channel, program, date, content type, and requested action.
- Avoid generic `site:` queries as the first strategy.
- Prefer official channel, recent videos/live streams, search within channel, or metadata through local tooling like `yt-dlp`.
- Verify title/channel/date before opening or playing.
- Verify playback before claiming play succeeded.

## NotebookLM Rule

For attached NotebookLM tabs:

- Use browser snapshot first.
- Read/summarize visible content without clicks or typing unless Diego explicitly asks.
- For export, create Markdown first and then DOCX/PDF as requested.

## Spotify Rule

For Spotify:

- Use an attached tab/app or verified local/API tool.
- Verify track/playlist/device/playback state after action.
- Do not browse private library/history unless requested.

## Word/PDF Rule

For Desktop deliverables:

- Preferred output root: `/home/lucy-ubuntu/Escritorio/`.
- Create the file, verify path and size, then respond.
- LibreOffice headless can be used for PDF conversion when available.

## Status

No n8n workflows, memory, vault, `.env`, TTS, voice payload, sqlite, or personal browser pages were modified for this run.
