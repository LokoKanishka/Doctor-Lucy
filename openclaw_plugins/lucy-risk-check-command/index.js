import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_risk_check_command.py");
const TIMEOUT_MS = 12000;

function runRiskCheck(rawArgs) {
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
        reject(new Error(stderr.trim() || `risk_check exited ${code}`));
        return;
      }
      resolvePromise(text);
    });
  });
}

function normalizeArgs(rawArgs) {
  const text = typeof rawArgs === "string" ? rawArgs.trim() : "";
  if (!text) {
    throw new Error("usage: /risk_check <request>");
  }
  return text;
}

export default {
  id: "lucy-risk-check-command",
  name: "Lucy Risk Check Command",
  description: "Deterministic read-only risk classifier for LucyClaw requests.",
  register(api) {
    api.registerCommand({
      name: "risk_check",
      description: "Classify a requested LucyClaw task as green, yellow, or red without executing it.",
      acceptsArgs: true,
      async handler(ctx) {
        try {
          const text = await runRiskCheck(normalizeArgs(ctx.args));
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "risk_check",
              stage: "R52",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
