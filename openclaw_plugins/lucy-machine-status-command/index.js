import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const COMMAND = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_status_command.py");
const TIMEOUT_MS = 15000;
const COMMANDS = [
  {
    name: "sys_status",
    description: "Show host, uptime, load, and RAM status.",
  },
  {
    name: "gpu_status",
    description: "Show NVIDIA GPU name, VRAM, utilization, and temperature when available.",
  },
  {
    name: "disk_status",
    description: "Show disk usage for the home path.",
  },
  {
    name: "process_status",
    description: "Show the top memory-consuming processes with scrubbed commands.",
  },
];

function runStatusCommand(commandName) {
  return new Promise((resolve, reject) => {
    const child = spawn("python3", [COMMAND, commandName], {
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
      resolve(text);
    });
  });
}

export default {
  id: "lucy-machine-status-command",
  name: "Lucy Machine Status Command",
  description: "Deterministic read-only machine status commands for LucyClaw.",
  register(api) {
    for (const entry of COMMANDS) {
      api.registerCommand({
        name: entry.name,
        description: entry.description,
        acceptsArgs: false,
        async handler() {
          try {
            const text = await runStatusCommand(entry.name);
            return { text };
          } catch (error) {
            return {
              text: JSON.stringify({
                ok: false,
                command: entry.name,
                error: error instanceof Error ? error.message : String(error),
              }),
            };
          }
        },
      });
    }
  },
};
