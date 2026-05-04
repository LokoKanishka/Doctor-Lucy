import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_scaffold_plan_command.py");
const TIMEOUT_MS = 12000;

async function runScaffoldPlan(rawArgs) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn("python3", [COMMAND, rawArgs], {
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      timeout: TIMEOUT_MS,
      env: { PYTHONPATH: resolve(PLUGIN_DIR, "../../") }
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
        reject(new Error(stderr.trim() || `scaffold_plan exited ${code}`));
        return;
      }
      resolvePromise(text);
    });
  });
}

function normalizeArgs(rawArgs) {
  const text = typeof rawArgs === "string" ? rawArgs.trim() : "";
  if (!text) {
    throw new Error("usage: /scaffold_plan <request>");
  }
  return text;
}

export const id = "lucy-scaffold-plan-command";
export const name = "Lucy Scaffold Plan Command";
export const description = "Generate a read-only technical plan for a new command scaffold.";

export function register(api) {
  api.registerCommand({
    name: "scaffold_plan",
    description: "Generate a read-only technical plan for a new command scaffold.",
    acceptsArgs: true,
    async handler(ctx) {
      try {
        const text = await runScaffoldPlan(normalizeArgs(ctx.args));
        return { text };
      } catch (error) {
        return {
          text: JSON.stringify({
            ok: false,
            command: "scaffold_plan",
            stage: "R55",
            error: error instanceof Error ? error.message : String(error),
          }),
        };
      }
    },
  });
}
