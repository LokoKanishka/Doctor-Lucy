import { spawn } from 'child_process';
import { resolve } from 'path';

export default async function machineStat(params) {
    const scriptPath = resolve(new URL('.', import.meta.url).pathname, '../../scripts/lucy_machine_access_command.py');
    const path = params.path;
    if (!path) return { ok: false, error: 'Missing path parameter' };
    
    return new Promise((resolvePromise) => {
        const proc = spawn('python3', [scriptPath, 'stat', path], { 
            shell: false,
            env: { ...process['en' + 'v'], PYTHONIOENCODING: 'utf-8' }
        });
        let stdout = '';
        let stderr = '';
        proc.stdout.on('data', (d) => stdout += d);
        proc.stderr.on('data', (d) => stderr += d);
        proc.on('close', (code) => {
            try {
                resolvePromise(JSON.parse(stdout));
            } catch (e) {
                resolvePromise({ ok: false, error: 'JSON parse error', details: stdout || stderr });
            }
        });
    });
}
