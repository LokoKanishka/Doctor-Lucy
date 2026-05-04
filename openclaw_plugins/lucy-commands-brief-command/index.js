import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_commands_brief_command.py");
const TIMEOUT_MS = 8000;

function runCommandsBrief() {
  return new Promise((resolvePromise, reject) => {
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
      if (!text && code !== 0) {
        reject(new Error(stderr.trim() || `commands_brief exited ${code}`));
        return;
      }
      resolvePromise(text);
    });
  });
}

export const id = "lucy-commands-brief-command";
export const name = "Lucy Commands Brief Command";
export const description = "Compact read-only commands index for LucyClaw.";

export function register(api) {
  api.registerCommand({
    name: "commands_brief",
    description: "Compact read-only commands index for LucyClaw.",
    acceptsArgs: false,
    async handler() {
      try {
        const text = await runCommandsBrief();
        return { text };
      } catch (error) {
        return {
          text: JSON.stringify({
            ok: false,
            command: "commands_brief",
            stage: "R57",
            error: error instanceof Error ? error.message : String(error),
          }),
        };
      }
    },
  });
}
