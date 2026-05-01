import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_fs_search_command.py");
const TIMEOUT_MS = 20000;

function runSearchCommand(commandName, rawArgs) {
  return new Promise((resolve, reject) => {
    const args = [COMMAND, commandName, rawArgs];
    const child = spawn("python3", args, {
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
        reject(new Error(stderr.trim() || `${commandName} exited ${code}`));
        return;
      }
      if (code !== 0) {
        try {
          const payload = JSON.parse(text);
          reject(new Error(payload.error || `${commandName} exited ${code}`));
        } catch {
          reject(new Error(`${commandName} exited ${code}`));
        }
        return;
      }
      resolve(text);
    });
  });
}

function normalizeRawArgs(raw, commandName) {
  const text = typeof raw === "string" ? raw.trim() : "";
  if (!text) {
    if (commandName === "fs_find") {
      throw new Error("usage: /fs_find <query>");
    }
    throw new Error("usage: /fs_grep <query> [scope]");
  }
  return text;
}

function buildError(commandName, error) {
  return {
    text: JSON.stringify({
      ok: false,
      command: commandName,
      error: error instanceof Error ? error.message : String(error),
    }),
  };
}

export default {
  id: "lucy-fs-search-command",
  name: "Lucy FS Search Command",
  description: "Deterministic read-only filesystem search commands for LucyClaw.",
  register(api) {
    for (const entry of [
      {
        name: "fs_find",
        description: "Find allowed repo files by name fragment inside the bounded LucyClaw tree.",
      },
      {
        name: "fs_grep",
        description: "Search text inside allowed repo files using a bounded optional scope.",
      },
    ]) {
      api.registerCommand({
        name: entry.name,
        description: entry.description,
        acceptsArgs: true,
        async handler(ctx) {
          try {
            const text = await runSearchCommand(entry.name === "fs_find" ? "find" : "grep", normalizeRawArgs(ctx.args, entry.name));
            return { text };
          } catch (error) {
            return buildError(entry.name, error);
          }
        },
      });
    }
  },
};
