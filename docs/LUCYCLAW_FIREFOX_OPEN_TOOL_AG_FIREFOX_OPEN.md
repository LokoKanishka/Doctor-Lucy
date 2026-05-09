# LucyClaw Firefox Open Tool - AG-FIREFOX-OPEN

Date: 2026-05-08

## Goal

Allow LucyClaw on Telegram to open Firefox on the host machine by herself when Diego asks for Firefox, instead of forcing the Chrome extension lane.

## Decision

OpenClaw's built-in `browser` lane in this installation is Chrome/Chromium-only. It has profiles `openclaw` and `chrome`; no `firefox` browser profile is available.

So the fix adds a narrow host tool:

- `lucy_firefox_status`: checks whether Firefox exists/runs.
- `lucy_firefox_open`: opens a safe URL in visible host Firefox using `firefox --new-tab` or `firefox --new-window`.

This tool intentionally does not claim DOM reading, clicking, YouTube playback verification, or NotebookLM inspection inside Firefox. Those require an automation-capable browser tool. For evidence-based web operation today, LucyClaw still uses OpenClaw `browser` with an automation-capable profile.

## Safety

- No shell execution.
- No sudo.
- No secret/env reads.
- Only `http`, `https`, and `about:blank` are accepted.
- `file:`, `javascript:`, `data:`, internal browser URLs, and control characters are rejected.
- The tool reports its limit explicitly: opening Firefox is confirmed by launch command acceptance, not by page DOM inspection.

## Runtime

The tool is registered in `lucy-machine-agent-tools` and added to agent main tool allowlists so the normal Telegram path can call it.

## Operator Rule

When Diego asks to use Firefox or "abrilo solo en Firefox", LucyClaw should call `lucy_firefox_open` directly for safe URLs. If Diego asks to verify, read, click, play, or summarize web content with evidence, LucyClaw must use an automation-capable browser lane or report the exact limitation.
