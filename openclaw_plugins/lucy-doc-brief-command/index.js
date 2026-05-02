import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_doc_brief_command.py");
const TIMEOUT_MS = 12000;

function runDocBrief(rawArgs) {
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
        reject(new Error(stderr.trim() || `doc_brief exited ${code}`));
        return;
      }
      resolvePromise(text);
    });
  });
}

function normalizeArgs(rawArgs) {
  const text = typeof rawArgs === "string" ? rawArgs.trim() : "";
  if (!text) {
    throw new Error("usage: /doc_brief <relative-path>");
  }
  return text;
}

export default {
  id: "lucy-doc-brief-command",
  name: "Lucy Doc Brief Command",
  description: "Deterministic read-only document brief for safe LucyClaw repo files.",
  register(api) {
    api.registerCommand({
      name: "doc_brief",
      description: "Summarize an allowed repo doc or command file using deterministic local heuristics.",
      acceptsArgs: true,
      async handler(ctx) {
        try {
          const text = await runDocBrief(normalizeArgs(ctx.args));
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "doc_brief",
              stage: "R50A",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
