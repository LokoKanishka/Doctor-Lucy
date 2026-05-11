# Protocol: YouTube Search Hardening (AG-YOUTUBE2)

This protocol corrects failures in the search phase by enforcing strict evidence verification before declaring a search successful or attempting to open results.

## 1. "Search Performed" Evidence
The agent MUST NOT claim "búsqueda realizada" unless at least one of these is verified via `snapshot`:
*   **Search URL**: The browser URL contains `search_query=<query>`.
*   **Search Box**: The UI search box contains the query text.
*   **Visible Candidates**: At least one video result with a visible Title and Channel is present in the `snapshot`.

## 2. Robust Search Strategy
If the initial UI-based search fails to yield visible candidates:
1.  **Fallback to Direct URL**: Navigate directly to `https://www.youtube.com/results?search_query=<query_codificada>`.
2.  **Verify Again**: Take a new `snapshot` and check for candidates.
3.  **Hard Block**: If still no candidates are visible, report: `"Bloqueo: búsqueda sin candidatos visibles"`.

## 3. Candidate Selection Rules
*   **Forbidden**: Opening a "probable result" if no candidate metadata (Title, Channel, or URL) is visible.
*   **Shorts Filtering**: If the request is for a full program or specific video, prioritize regular videos over "Shorts" sections.
*   **Verification**: Before clicking to open, the agent must be able to cite the Title/Channel of the candidate it is about to open.

## 4. Playback Prerequisite
*   **Action**: `click` on candidate.
*   **Verification**: The browser URL must change to `watch?v=...`.
*   **Status**: `snapshot` must show the video player interface.
*   **Action**: Only then attempt "play".

## 5. Entity Extraction for Queries
For complex requests (e.g., "Vorterix Y qué"), extract:
*   **Channel**: Vorterix
*   **Program**: "Y qué"
*   **Search Query**: `Vorterix "Y qué"` (using quotes for precision).

---
*Enforced by AG-YOUTUBE2.*
