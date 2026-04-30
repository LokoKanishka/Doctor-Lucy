import { spawn } from "node:child_process";

const COMMAND = "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_fs_read_command.py";
const ARG_RE = /^(\S+)\s+(\d+)\s+(\d+)\s*$/u;

function runReadonlyCommand(args) {
  return new Promise((resolve, reject) => {
    const child = spawn("python3", [COMMAND, ...args], {
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      timeout: 15000,
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
        reject(new Error(stderr.trim() || `fs_read exited ${code}`));
        return;
      }
      if (code !== 0) {
        try {
          const payload = JSON.parse(text);
          reject(new Error(payload.error || `fs_read exited ${code}`));
        } catch {
          reject(new Error(`fs_read exited ${code}`));
        }
        return;
      }
      resolve(text);
    });
  });
}

function parseRawArgs(raw) {
  const command = typeof raw === "string" ? raw.trim() : "";
  const match = command.match(ARG_RE);
  if (!match) {
    throw new Error("usage: /fs_read <relative-path> <start> <end>");
  }
  const [, path, start, end] = match;
  return [path, start, end];
}

export default {
  id: "lucy-fs-readonly-command",
  name: "Lucy FS Readonly Command",
  description: "Deterministic read-only filesystem command for Doctor-Lucy repo.",
  register(api) {
    api.registerCommand({
      name: "fs_read",
      description: "Read an exact allowed line range from the Doctor-Lucy repo.",
      acceptsArgs: true,
      async handler(ctx) {
        try {
          const text = await runReadonlyCommand(parseRawArgs(ctx.args));
          return { text };
        } catch (error) {
          return { text: JSON.stringify({ ok: false, error: error instanceof Error ? error.message : String(error) }) };
        }
      },
    });

    api.registerTool({
      name: "fs_read_command",
      description: "Read an exact line range from an allowed Doctor-Lucy repo file. Input command format: <path> <start> <end>.",
      parameters: {
        type: "object",
        additionalProperties: false,
        properties: {
          command: {
            type: "string",
            description: "Relative path plus start/end lines, for example: scripts/lucy_openclaw_bridge.py 138 138",
          },
        },
        required: ["command"],
      },
      async execute(_id, params) {
        const text = await runReadonlyCommand(parseRawArgs(params?.command));
        return { content: [{ type: "text", text }] };
      },
    });
  },
};
