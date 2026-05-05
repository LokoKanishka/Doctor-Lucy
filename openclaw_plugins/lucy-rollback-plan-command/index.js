import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default async function rollbackPlanCommand(args) {
  return new Promise((res) => {
    // Sanitización básica de argumentos en JS antes de pasar a Python
    const target = (args && args._ && args._[0]) ? String(args._[0]) : "";
    
    // Solo permitir caracteres seguros para evitar inyecciones de shell (aunque shell:false lo protege)
    const sanitizedTarget = target.replace(/[^a-zA-Z0-9\-_.]/g, "").slice(0, 80);

    const scriptPath = resolve(__dirname, '../../scripts/lucy_rollback_plan_command.py');
    const child = spawn('python3', [scriptPath, sanitizedTarget], { shell: false });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => { stdout += data; });
    child.stderr.on('data', (data) => { stderr += data; });

    child.on('close', (code) => {
      if (code !== 0) {
        res({
          ok: false,
          command: "rollback_plan",
          error: stderr.trim() || `Process exited with code ${code}`,
          decision: "NEEDS_REVIEW"
        });
        return;
      }
      try {
        res(JSON.parse(stdout));
      } catch (e) {
        res({
          ok: false,
          command: "rollback_plan",
          error: "Failed to parse wrapper output",
          raw: stdout.trim(),
          decision: "NEEDS_REVIEW"
        });
      }
    });

    setTimeout(() => {
      child.kill();
      res({
        ok: false,
        command: "rollback_plan",
        error: "Timeout executing rollback_plan",
        decision: "NEEDS_REVIEW"
      });
    }, 10000);
  });
}
