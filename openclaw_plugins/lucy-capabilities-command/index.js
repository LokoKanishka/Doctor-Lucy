import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_capabilities_command.py");
const TIMEOUT_MS = 10000;

function runCapabilities() {
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
        reject(new Error(stderr.trim() || `lucy_capabilities exited ${code}`));
        return;
      }
      resolve(text);
    });
  });
}

export default {
  id: "lucy-capabilities-command",
  name: "Lucy Capabilities Command",
  description: "Deterministic read-only capabilities map for LucyClaw.",
  register(api) {
    api.registerCommand({
      name: "lucy_capabilities",
      description: "Show the current green/yellow/red capability map for LucyClaw.",
      acceptsArgs: false,
      async handler() {
        try {
          const text = await runCapabilities();
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "lucy_capabilities",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
