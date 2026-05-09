# LucyClaw Chrome-Only Browser Policy - AG-CHROME-ONLY

Date: 2026-05-09
Run: AG-CHROME-ONLY

## Decision

Following Diego's explicit instruction to "not mix Firefox and Chrome", the system is now configured to use **Chrome/OpenClaw** as the unique operational browser lane for all automated tasks, including reading, clicking, YouTube playback, NotebookLM inspection, and evidence-based verification.

## Policy Rules

1.  **Unique Operational Lane**: Chrome/OpenClaw is the only browser allowed for automated web operations.
2.  **Firefox Status**: The Firefox host tool (`lucy_firefox_open`) remains installed but is relegated to **EXPLICIT-ONLY** status.
3.  **No Silent Fallback**: LucyClaw must NEVER use Firefox as a fallback for browser tasks if Chrome is unavailable.
4.  **Blocker Reporting**: If a task requires a browser and no Chrome tab is attached (or `profile="chrome"` fails), LucyClaw must report a specific blocker (e.g., "Bloqueo: requiere pestaña Chrome adjunta") instead of attempting to use Firefox.
5.  **Explicit Firefox Usage**: LucyClaw will only call `lucy_firefox_open` if Diego explicitly says "abrilo en Firefox" or equivalent. Even in this case, LucyClaw must clarify that Firefox is non-operational (no DOM reading/verification).

## Implementation

*   **AGENTS.md**: Updated the Domain Router and Preflight rules to prioritize Chrome and mark Firefox as explicit-only.
*   **TOOLS.md**: Updated the Firefox Host section with the new restrictive policy.
*   **IDENTITY.md**: Defined Chrome/OpenClaw as the "Navegador Operativo Único".
*   **Gateway**: Restarted to apply instruction changes.

## Verification

Smoke tests performed:
*   **Generic Browser Request**: Requesting "open YouTube" without specifying browser -> Uses/attempts Chrome, ignores Firefox.
*   **Reading Request**: Requesting tab title without specifying browser -> Uses Chrome lane, reports blocker if no tab attached.
*   **Explicit Firefox Request**: Requesting "open about:blank in Firefox" -> Uses Firefox tool but acknowledges it is non-operational.
*   **YouTube Play**: Requesting playback -> Enforces Chrome-only and evidence loop.

## Result

Operational clarity achieved. The agent no longer confuses the visibility of Firefox with the automation capabilities of Chrome.
