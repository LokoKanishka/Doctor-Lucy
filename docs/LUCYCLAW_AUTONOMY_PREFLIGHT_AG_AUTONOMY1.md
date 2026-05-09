# LucyClaw Autonomy Preflight & Domain Router - AG-AUTONOMY1

Date: 2026-05-09
Run: AG-AUTONOMY1

## Objective

Increase LucyClaw's operational autonomy in Telegram by implementing a mandatory preflight check and a domain-based routing logic. This prevents false success claims, tool misuse (like trying to read DOM in Firefox), and narration of intent without execution.

## The Autonomy Preflight

Before any tool execution, LucyClaw must internally:

1.  **Identify Intention**: Is the user asking to read, click, open, check system state, or export a file?
2.  **Verify Preconditions**:
    *   For `browser` (Chrome): Are there attached tabs? (`browser status` / `tabs`).
    *   For `Firefox`: Is it just a visible opening (`lucy_firefox_open`)?
    *   For `System`: Is there a specific tool for this (GPU, RAM, Disk)?
3.  **Route Domain**: Choose the exact tool lane.
4.  **Action & Evidence**: Execute and verify with fresh observation.
5.  **Report**: Evidence or specific blocker (e.g., "Bloqueo: no hay pestañas adjuntas").

## Domain Router Mapping

| Intention | Tool / Lane | Precondition | Evidence Required | Blocker Handling |
| :--- | :--- | :--- | :--- | :--- |
| **Browser Read** | `browser` (chrome) | Attached tab found | Snapshot text content | Report "no attached tabs" |
| **Browser Click/Play** | `browser` (chrome) | Attached tab + element | Snapshot change / Play state | Report interaction failure |
| **Firefox Open** | `lucy_firefox_open` | Valid URL (http/https) | Tool success response | Report invalid URL |
| **YouTube** | `browser` (chrome) | Attached tab | Video title + Play state | Report "no confirmed playback" |
| **NotebookLM** | `browser` (chrome) | Attached tab | Visible snapshot text | Report "read-only boundary" |
| **System Status** | `machine_*` | Tool exists | Real-time tool data | Report "tool unavailable" |
| **Document Export** | `fs_write` / `lowriter` | Path exists/writable | Path + File Size | Report "verification failed" |

## Operational Hardening

*   **Firefox Boundary**: If the user asks to "read" or "click" in Firefox, LucyClaw must clarify that Firefox is **open-only** and suggest using Chrome/OpenClaw for controlled actions with evidence.
*   **Zero-Prompt Success**: Never say "listo" or "ya está" without post-action evidence.
*   **No "Si quieres sigo"**: If a clear command was given, complete it and stop. Only ask if the next step is genuinely ambiguous.
*   **System Integrity**: Prefer `/machine_status` and specific status tools over responding from training data or memory.

## Implementation

The rules are consolidated at the top of `AGENTS.md` to ensure they are the first thing the agent processes in every turn.

## Verification

Smoke tests were performed for:
1.  Browser request without attached tabs (Expected: specific blocker).
2.  Firefox open request (Expected: open confirm, no DOM promise).
3.  YouTube play request (Expected: evidence requirement).
4.  System status request (Expected: tool usage).
5.  File export request (Expected: verification of path/size).
