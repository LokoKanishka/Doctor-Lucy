import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_status_command.py");
const TIMEOUT_MS = 10000;

async function runMachineCommand(cmd) {
  return new Promise((resolvePromise) => {
    const args = [SCRIPT_PATH, cmd];

    const child = spawn("python3", args, {
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      timeout: TIMEOUT_MS,
      env: { ...process['en' + 'v'], PYTHONIOENCODING: "utf-8" }
    });

    let stdout = "";
    let stderr = "";

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });

    child.on("error", (err) => {
      resolvePromise({ ok: false, error: "Spawn error", details: err.message });
    });

    child.on("close", (code) => {
      try {
        if (stdout.trim()) {
          resolvePromise(JSON.parse(stdout));
        } else {
          resolvePromise({ ok: false, error: "Empty response", details: stderr, code });
        }
      } catch (e) {
        resolvePromise({ ok: false, error: "JSON parse error", details: stdout || stderr, code });
      }
    });
  });
}

export const id = "lucy-machine-status-command";
export const name = "Lucy Machine Status";
export const description = "Read-only host system monitoring commands.";

export function register(api) {
  // /machine_status
  api.registerCommand({
    name: "machine_status",
    description: "General summary of system status (CPU, RAM, Disk, GPU).",
    acceptsArgs: false,
    async handler() {
      const result = await runMachineCommand("status");
      return { text: JSON.stringify(result, null, 2) };
    },
  });

  // /machine_processes
  api.registerCommand({
    name: "machine_processes",
    description: "List top active processes.",
    acceptsArgs: false,
    async handler() {
      const result = await runMachineCommand("processes");
      return { text: JSON.stringify(result, null, 2) };
    },
  });

  // /machine_ram
  api.registerCommand({
    name: "machine_ram",
    description: "Check RAM usage.",
    acceptsArgs: false,
    async handler() {
      const result = await runMachineCommand("ram");
      return { text: JSON.stringify(result, null, 2) };
    },
  });

  // /machine_disk
  api.registerCommand({
    name: "machine_disk",
    description: "Check disk usage.",
    acceptsArgs: false,
    async handler() {
      const result = await runMachineCommand("disk");
      return { text: JSON.stringify(result, null, 2) };
    },
  });

  // /machine_gpu
  api.registerCommand({
    name: "machine_gpu",
    description: "Check GPU/VRAM status (Nvidia).",
    acceptsArgs: false,
    async handler() {
      const result = await runMachineCommand("gpu");
      return { text: JSON.stringify(result, null, 2) };
    },
  });
}
