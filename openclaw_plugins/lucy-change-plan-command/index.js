import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_change_plan_command.py");
const TIMEOUT_MS = 12000;

function runChangePlan(rawArgs) {
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
        reject(new Error(stderr.trim() || `change_plan exited ${code}`));
        return;
      }
      resolvePromise(text);
    });
  });
}

function normalizeArgs(rawArgs) {
  const text = typeof rawArgs === "string" ? rawArgs.trim() : "";
  if (!text) {
    throw new Error("usage: /change_plan <request>");
  }
  return text;
}

export default {
  id: "lucy-change-plan-command",
  name: "Lucy Change Plan Command",
  description: "Deterministic read-only technical change plan for LucyClaw requests.",
  register(api) {
    api.registerCommand({
      name: "change_plan",
      description: "Prepare a deterministic technical plan for a requested LucyClaw change without executing it.",
      acceptsArgs: true,
      async handler(ctx) {
        try {
          const text = await runChangePlan(normalizeArgs(ctx.args));
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "change_plan",
              stage: "R54",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
