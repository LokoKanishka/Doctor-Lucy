import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_health_brief_command.py");
const TIMEOUT_MS = 20000;

function runHealthBrief() {
  return new Promise((resolve, reject) => {
    const child = spawn("python3", [COMMAND], {
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
        reject(new Error(stderr.trim() || `health_brief exited ${code}`));
        return;
      }
      resolve(text);
    });
  });
}

export default {
  id: "lucy-health-brief-command",
  name: "Lucy Health Brief Command",
  description: "Deterministic compact read-only health brief for LucyClaw.",
  register(api) {
    api.registerCommand({
      name: "health_brief",
      description: "Show a compact read-only health summary for Telegram.",
      acceptsArgs: false,
      async handler() {
        try {
          const text = await runHealthBrief();
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "health_brief",
              overall: "error",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
