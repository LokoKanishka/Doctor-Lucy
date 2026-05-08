# AG-BROWSER5 — Chrome extension manual attach validated

Date: 2026-05-08

OpenClaw version: 2026.3.8 (3caab92)

## Status

Chrome extension relay validation completed successfully on real Chrome.

- Gateway `127.0.0.1:18789` was live.
- Relay `127.0.0.1:18792` was reachable and returned the expected relay surface.
- The gateway token was not printed and remained stored in `chrome.storage.local`.
- Badge `ON` was achieved after effective extension/service-worker reload.
- The `chrome` browser profile detected the smoke tab.
- Snapshot read:
  - `Lucy Extension Smoke`
  - `LUCY_EXTENSION_SMOKE_20260507`
  - `Attach manual seguro`
- `SEC1`, `run_registry`, and `QA1` completed successfully.

## Auth Contract

The extension auth contract is now confirmed:

- The extension stores the raw gateway token in `chrome.storage.local.gatewayToken`.
- `buildRelayWsUrl(...)` derives the relay URL token using HMAC-SHA256 with context `openclaw-extension-relay-v1:<port>`.
- The relay upgrade path accepts raw and derived tokens.
- The gateway `connect` handshake uses the raw token.

Operationally, the winning state is:

- storage format: raw token
- relay URL auth: derived token
- connect handshake auth: raw token

## Lesson Learned

If the extension shows badge `!` after a token rotation or auth repair, do not declare success until all of these are true:

1. The installed extension build is the intended one.
2. `chrome.storage.local.gatewayToken` is present.
3. The service worker / extension has been reloaded effectively.
4. Badge is `ON`.
5. `openclaw browser tabs --browser-profile chrome` detects the selected tab.
6. `openclaw browser snapshot --browser-profile chrome` reads the expected marker text.

During AG-BROWSER5, the decisive step was an effective reload of the extension runtime via `chrome.runtime.reload()`. Raw token storage alone was correct but not sufficient until the running service worker picked it up.

## Safe Usage Protocol

1. Use the isolated `openclaw` browser profile by default.
2. Use the Chrome extension path only for tabs explicitly chosen by Diego.
3. Keep attach manual; do not enable or simulate auto-attach behavior for general browsing.
4. Do not inspect, snapshot, or read sensitive/personal tabs without explicit permission.
5. Do not capture screenshots from personal Chrome pages without explicit permission.
6. Prefer a smoke tab or an innocuous public tab for auth and attach validation.
7. Detach when the work is finished.

## Recommended Future Procedure

When validating or recovering the browser relay in the future:

1. Check gateway health on `18789`.
2. Check relay reachability on `18792`.
3. Verify `chrome.storage.local` presence and token length without printing the value.
4. Reload the service worker / extension if auth changes were applied.
5. Attach only to a safe tab.
6. Confirm `badge ON` plus `tabs` plus `snapshot` before using the profile for real work.
