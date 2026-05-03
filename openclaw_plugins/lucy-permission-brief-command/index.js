import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_permission_brief_command.py");
const TIMEOUT_MS = 12000;

function runPermissionBrief(rawArgs) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn("python3", [COMMAND, rawArgs], {
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      timeout: TIMEOUT_MS,
    });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("error", reject);
    child.on("close", (code) => {
      const text = stdout.trim();
      if (!text) {
        reject(new Error(stderr.trim() || `permission_brief exited ${code}`));
        return;
      }
      resolvePromise(text);
    });
  });
}

function normalizeArgs(rawArgs) {
  const text = typeof rawArgs === "string" ? rawArgs.trim() : "";
  if (!text) {
    throw new Error("usage: /permission_brief <request>");
  }
  return text;
}

export default {
  id: "lucy-permission-brief-command",
  name: "Lucy Permission Brief Command",
  description: "Deterministic read-only permission brief for LucyClaw requests.",
  register(api) {
    api.registerCommand({
      name: "permission_brief",
      description: "Explain which permissions would be required before executing a requested LucyClaw task.",
      acceptsArgs: true,
      async handler(ctx) {
        try {
          const text = await runPermissionBrief(normalizeArgs(ctx.args));
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "permission_brief",
              stage: "R53",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
