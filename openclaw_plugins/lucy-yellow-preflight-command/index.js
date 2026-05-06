import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const WRAPPER_PATH = resolve(__dirname, '../../scripts/lucy_yellow_preflight_command.py');

export default {
  async init(api) {
    api.registerCommandHandler('yellow_preflight', async (args) => {
      return new Promise((res) => {
        const proc = spawn('python3', [WRAPPER_PATH], { shell: false });
        let stdout = '';
        let stderr = '';

        proc.stdout.on('data', (data) => { stdout += data; });
        proc.stderr.on('data', (data) => { stderr += data; });

        proc.on('close', (code) => {
          if (code === 0 || code === 1) {
            try {
              res(jsonResponse(stdout));
            } catch (e) {
              res({ ok: false, error: 'invalid json from wrapper', details: stdout });
            }
          } else {
            res({ ok: false, error: `wrapper exited with code ${code}`, details: stderr || stdout });
          }
        });
      });
    });
  }
};

function jsonResponse(stdout) {
  return JSON.parse(stdout.trim());
}
