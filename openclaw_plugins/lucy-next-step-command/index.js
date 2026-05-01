import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_next_step_command.py");
const TIMEOUT_MS = 30000;

function runNextStep() {
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
        reject(new Error(stderr.trim() || `lucy_next_step exited ${code}`));
        return;
      }
      resolve(text);
    });
  });
}

export default {
  id: "lucy-next-step-command",
  name: "Lucy Next Step Command",
  description: "Deterministic safe advance gate for LucyClaw.",
  register(api) {
    api.registerCommand({
      name: "lucy_next_step",
      description: "Evaluate whether LucyClaw is ready to safely prepare the next tranche.",
      acceptsArgs: false,
      async handler() {
        try {
          const text = await runNextStep();
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "lucy_next_step",
              stage: "R48",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
