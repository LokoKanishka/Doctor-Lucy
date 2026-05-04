import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_help_command.py");
const TIMEOUT_MS = 8000;

function runHelp() {
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
      const text = stdout.strip ? stdout.strip() : stdout.trim();
      if (!text && code !== 0) {
        reject(new Error(stderr.trim() || `lucy_help exited ${code}`));
        return;
      }
      resolvePromise(text);
    });
  });
}

export const id = "lucy-help-command";
export const name = "Lucy Help Command";
export const description = "Compact read-only help guide for LucyClaw.";

export function register(api) {
  api.registerCommand({
    name: "lucy_help",
    description: "Compact read-only help guide for LucyClaw.",
    acceptsArgs: false,
    async handler() {
      try {
        const text = await runHelp();
        return { text };
      } catch (error) {
        return {
          text: JSON.stringify({
            ok: false,
            command: "lucy_help",
            stage: "R56",
            error: error instanceof Error ? error.message : String(error),
          }),
        };
      }
    },
  });
}
