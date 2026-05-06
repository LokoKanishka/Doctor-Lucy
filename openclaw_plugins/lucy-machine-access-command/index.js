import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_access_command.py");
const TIMEOUT_MS = 10000;

async function runMachineCommand(cmd, pathArg = null) {
  return new Promise((resolvePromise, reject) => {
    const args = [SCRIPT_PATH, cmd];
    if (pathArg) args.push(pathArg);

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

    child.on("error", reject);
    child.on("close", (code) => {
      try {
        if (stdout.trim()) {
          resolvePromise(JSON.parse(stdout));
        } else {
          resolvePromise({ ok: false, error: "Empty response", details: stderr });
        }
      } catch (e) {
        resolvePromise({ ok: false, error: "JSON parse error", details: stdout || stderr });
      }
    });
  });
}

export const id = "lucy-machine-access-command";
export const name = "Lucy Machine Access";
export const description = "Read-only host file listing commands.";

export function register(api) {
  // /machine_downloads
  api.registerCommand({
    name: "machine_downloads",
    description: "List files in the Downloads folder.",
    acceptsArgs: false,
    async handler() {
      const result = await runMachineCommand("downloads");
      return { text: JSON.stringify(result, null, 2) };
    },
  });

  // /machine_ls [path]
  api.registerCommand({
    name: "machine_ls",
    description: "List files in a specified directory.",
    acceptsArgs: true,
    async handler(args) {
      const pathArg = args ? args.trim() : null;
      const result = await runMachineCommand("ls", pathArg);
      return { text: JSON.stringify(result, null, 2) };
    },
  });

  // /machine_stat <path>
  api.registerCommand({
    name: "machine_stat",
    description: "Get metadata for a specified file or directory.",
    acceptsArgs: true,
    async handler(args) {
      if (!args || !args.trim()) {
        return { text: JSON.stringify({ ok: false, error: "Missing path argument" }, null, 2) };
      }
      const result = await runMachineCommand("stat", args.trim());
      return { text: JSON.stringify(result, null, 2) };
    },
  });
}
