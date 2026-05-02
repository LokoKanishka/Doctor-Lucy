import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_repo_map_command.py");
const TIMEOUT_MS = 10000;

function runRepoMap() {
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
        reject(new Error(stderr.trim() || `repo_map exited ${code}`));
        return;
      }
      resolve(text);
    });
  });
}

export default {
  id: "lucy-repo-map-command",
  name: "Lucy Repo Map Command",
  description: "Compact read-only repo map for LucyClaw/OpenClaw navigation.",
  register(api) {
    api.registerCommand({
      name: "repo_map",
      description: "Show a compact safe repo map for LucyClaw/OpenClaw navigation.",
      acceptsArgs: false,
      async handler() {
        try {
          const text = await runRepoMap();
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "repo_map",
              stage: "R49",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
