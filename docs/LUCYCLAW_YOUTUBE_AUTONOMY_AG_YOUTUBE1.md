# LucyClaw YouTube Autonomy v1 with Evidence - AG-YOUTUBE1

Date: 2026-05-09
Run: AG-YOUTUBE1

## Objective

Improve LucyClaw's autonomy for YouTube tasks from Telegram by enforcing a strict search-selection-verification loop and requiring post-action evidence for playback.

## The YouTube Autonomy Loop

### 1. Preflight
*   **Unique Lane**: YouTube MUST use Chrome/OpenClaw. Firefox is forbidden for YouTube tasks unless explicitly requested (and even then, it is non-operational).
*   **Condition**: Confirm if a Chrome tab is attached or if the `browser` tool can use a controllable profile.
*   **Blocker**: If no tab/control is available, report a specific blocker (e.g., "Bloqueo: requiere pestaña Chrome adjunta para operar YouTube").

### 2. Intelligent Search
*   **Entities**: Extract Channel, Program, Date, and Content Type.
*   **Strategy**: Prefer searching within the official channel or using direct metadata tools over generic Google/YouTube searches.
*   **Recency**: If "today's" or "latest" video is requested, prioritize sorting by date and verifying against the current system date.

### 3. Selection & Verification
*   **Criteria**: Match Title + Channel + Date.
*   **Avoid Shorts**: Do not select Shorts for long-form content requests unless specified.
*   **Observation**: Take a fresh `snapshot` immediately after the video page loads.

### 4. Playback Evidence
*   **Action**: Attempt to play the video.
*   **Verification**: Take a new `snapshot` after the action.
*   **Evidence Required**: To claim "play succeeded", at least two of these must be true:
    1.  Video Title is visible and matches.
    2.  Player controls show "Pause" (indicating it is currently playing).
    3.  Video progress/time is advancing or non-zero.
    4.  Player status is "playing".
*   **Failure**: If playback cannot be verified (e.g., due to ads, login, or DRM), report "no confirmado" and describe the exact blocker.

## Reporting Standard

*   **Brevity**: Maximum 5 lines for Telegram.
*   **Format**: [Action] + [Evidence] + [Blocker/Note].
*   **Zero-Prompt**: Do not ask "si quieres sigo".

## Verification

Smoke tests were performed for:
1.  YouTube request without Chrome tab (Expected: specific blocker).
2.  Play request without evidence (Expected: reporting non-verified state).
3.  Operator mode brevity (Expected: concise report).

## Result

YouTube operations are now disciplined, avoiding false success reports and ensuring the agent remains in sync with the real state of the media player.
