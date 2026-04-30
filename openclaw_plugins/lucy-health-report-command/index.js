import { spawn } from "node:child_process";

const COMMAND = "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_health_report_command.py";
const TIMEOUT_MS = 30000;

function runHealthReport() {
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
        reject(new Error(stderr.trim() || `health_report exited ${code}`));
        return;
      }
      resolve(text);
    });
  });
}

export default {
  id: "lucy-health-report-command",
  name: "Lucy Health Report Command",
  description: "Deterministic read-only aggregate health report for LucyClaw.",
  register(api) {
    api.registerCommand({
      name: "health_report",
      description: "Show aggregate read-only health report for machine, services, and bounded logs.",
      acceptsArgs: false,
      async handler() {
        try {
          const text = await runHealthReport();
          return { text };
        } catch (error) {
          return {
            text: JSON.stringify({
              ok: false,
              command: "health_report",
              error: error instanceof Error ? error.message : String(error),
            }),
          };
        }
      },
    });
  },
};
