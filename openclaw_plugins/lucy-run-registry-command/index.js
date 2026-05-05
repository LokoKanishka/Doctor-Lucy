import { spawn } from 'child_process';
import { resolve } from 'path';

export default async function runRegistryCommand() {
    const scriptPath = resolve(new URL('.', import.meta.url).pathname, '../../scripts/lucy_run_registry_command.py');
    return new Promise((resolvePromise, rejectPromise) => {
        const proc = spawn('python3', [scriptPath], { shell: false });
        let stdoutData = '';
        let stderrData = '';

        proc.stdout.on('data', (chunk) => {
            stdoutData += chunk;
        });

        proc.stderr.on('data', (chunk) => {
            stderrData += chunk;
        });

        proc.on('close', (code) => {
            if (code !== 0 && code !== 1) { // 1 is handled explicitly by python wrapper returning valid JSON with error sometimes, but usually ok:false returns code 1. Actually wrapper returns code 1/2. Let's just resolve if JSON parses.
                // Wait, if it fails, our wrapper still outputs JSON. Let's try parsing first.
                try {
                    if (stdoutData.trim()) {
                        const result = JSON.parse(stdoutData.trim());
                        return resolvePromise(result);
                    }
                } catch(e) {}
                return rejectPromise(new Error(`Command failed with code ${code}. Stderr: ${stderrData}`));
            }
            try {
                const result = JSON.parse(stdoutData.trim());
                resolvePromise(result);
            } catch (err) {
                rejectPromise(new Error(`Failed to parse output as JSON: ${err.message}`));
            }
        });

        proc.on('error', (err) => {
            rejectPromise(err);
        });

        setTimeout(() => {
            proc.kill();
            rejectPromise(new Error('Command timed out'));
        }, 15000);
    });
}
