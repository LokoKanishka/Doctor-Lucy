import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_plan_brief_command.py");
const TIMEOUT_MS = 12000;

function runPlanBrief(rawArgs) {
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
        reject(new Error(stderr.trim() || `plan_brief exited ${code}`));
        return;
      }
      resolvePromise(text);
    });
  });
}

function normalizeArgs(rawArgs) {
  const text = typeof rawArgs === "string" ? rawArgs.trim() : "";
  if (!text) {
    throw new Error("usage: /plan_brief <request>");
  }
  return text;
}

export default {
  id: "lucy-plan-brief-command",
  name: "Lucy Plan Brief Command",
  description: "Deterministic read-only planning brief for LucyClaw requests.",
  register(api) {
    api.registerCommand({
      name: "plan_brief",
      description: "Prepare a deterministic plan-only brief for a requested LucyClaw task.",
      acceptsArgs: true,
      async handler(ctx) {
        try {
          const text = await runPlanBrief(normalizeArgs(ctx.args));
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "plan_brief",
              stage: "R51",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
