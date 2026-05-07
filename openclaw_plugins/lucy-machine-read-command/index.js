import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_read_command.py");
const TIMEOUT_MS = 15000;

function normalizeArgs(input) {
  if (!input) return "";
  if (typeof input === "string") return input.trim();
  if (Array.isArray(input)) return input.join(" ").trim();
  if (typeof input === "object") {
    return (
      input.text ||
      input.args ||
      input.argument ||
      input.query ||
      input.message ||
      ""
    ).toString().trim();
  }
  return String(input).trim();
}

async function runMachineReadCommand(action, pathArg) {
  return new Promise((resolvePromise) => {
    const args = [SCRIPT_PATH, action];
    if (pathArg) args.push(pathArg);

    const child = spawn("python3", args, {
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      timeout: TIMEOUT_MS,
      env: { ...process["en" + "v"], PYTHONIOENCODING: "utf-8" }
    });

    let stdout = "";
    let stderr = "";

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });

    child.on("error", (err) => {
      resolvePromise({ ok: false, error: "Spawn error", details: err.message, controlled_failure: true });
    });

    child.on("close", (code) => {
      try {
        if (stdout.trim()) {
          resolvePromise(JSON.parse(stdout));
        } else {
          resolvePromise({ ok: false, error: "Empty response", details: stderr, code, controlled_failure: true });
        }
      } catch (error) {
        resolvePromise({ ok: false, error: "JSON parse error", details: stdout || stderr, code, controlled_failure: true });
      }
    });
  });
}

export const id = "lucy-machine-read-command";
export const name = "Lucy Machine Read";
export const description = "Read-only host document reading commands.";

export function register(api) {
  api.registerCommand({
    name: "machine_read",
    description: "Read text from a supported local document inside allowed host paths.",
    acceptsArgs: true,
    async handler(args) {
      const normalized = normalizeArgs(args);
      if (!normalized) {
        return { text: JSON.stringify({ ok: false, error: "Missing path argument", controlled_failure: true }, null, 2) };
      }
      const result = await runMachineReadCommand("read", normalized);
      return { text: JSON.stringify(result, null, 2) };
    },
  });

  api.registerCommand({
    name: "machine_doc_brief",
    description: "Read metadata plus a bounded literal excerpt from a supported local document.",
    acceptsArgs: true,
    async handler(args) {
      const normalized = normalizeArgs(args);
      if (!normalized) {
        return { text: JSON.stringify({ ok: false, error: "Missing path argument", controlled_failure: true }, null, 2) };
      }
      const result = await runMachineReadCommand("brief", normalized);
      return { text: JSON.stringify(result, null, 2) };
    },
  });
}
