# Browser Relay Diagnostic (AG-BROWSER1) — Read-Only

## Overview
Browser Relay allows LucyClaw to interact with a real Chrome browser instance via a local relay and a dedicated extension.

## Audit Results
- **Profile**: `chrome`
- **Port**: `18792`
- **Relay Status**: **Active** (Hosted by `openclaw-gateway`)
- **Extension Path**: `~/.openclaw/browser/chrome-extension`
- **Attached Tabs**: **0** (Waiting for user attachment)

## Operational Limits (Read-Only Phase)
In this phase (AG-BROWSER1), the following restrictions apply:
- **NO** clicks or form submissions.
- **NO** typing or data entry.
- **NO** automatic navigation.
- **ONLY** tab listing, status checks, and basic text snapshots (once a tab is attached).

## Current Status
The relay is listening and ready. The system is waiting for a manual attachment from the user to proceed with read-only tests.

## Next Steps
1. User attaches a non-sensitive tab in Chrome using the OpenClaw extension (Badge ON).
2. Agent verifies the tab via `openclaw browser --browser-profile chrome tabs`.
3. Agent performs a read-only snapshot or title check.
