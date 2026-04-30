import { spawn } from "node:child_process";

const COMMAND = "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_service_status_command.py";
const TIMEOUT_MS = 20000;
const COMMANDS = [
  {
    name: "openclaw_health",
    description: "Show OpenClaw gateway health, user service status, and model state when available.",
  },
  {
    name: "docker_status",
    description: "Show Docker CLI, daemon, and bounded container status.",
  },
  {
    name: "ollama_status",
    description: "Show Ollama local API reachability and up to ten model names.",
  },
  {
    name: "n8n_health",
    description: "Show visible n8n container or local HTTP health without reading workflows.",
  },
  {
    name: "service_status",
    description: "Show fixed allowlist service status for OpenClaw, Docker, Ollama, and n8n.",
  },
  {
    name: "log_tail",
    description: "Show sanitized bounded OpenClaw gateway logs.",
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
  id: "lucy-service-status-command",
  name: "Lucy Service Status Command",
  description: "Deterministic read-only service and bounded log status commands for LucyClaw.",
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
