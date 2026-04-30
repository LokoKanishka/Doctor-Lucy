---
name: fs_read
description: "Read an exact allowed line range from the Doctor-Lucy repo. Usage: /fs_read <relative-path> <start> <end>"
user-invocable: false
disable-model-invocation: true
---

# fs_read

Read an exact line range from an allowed file inside the Doctor-Lucy repo.

Usage:

```text
/fs_read scripts/lucy_openclaw_bridge.py 138 138
```

The `/fs_read` slash command is registered directly by the local OpenClaw plugin.
It does not ask the model to decide whether to read files.
