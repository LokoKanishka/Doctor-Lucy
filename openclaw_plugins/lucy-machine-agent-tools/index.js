import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const PYTHON = "/usr/bin/python3";
const TIMEOUT_MS = 15000;
const ACCESS_SCRIPT = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_access_command.py");
const STATUS_SCRIPT = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_status_command.py");
const READ_SCRIPT = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_read_command.py");

function runJsonScript(scriptPath, args) {
  return new Promise((resolvePromise) => {
    const child = spawn(PYTHON, [scriptPath, ...args], {
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
    });

    const timer = setTimeout(() => {
      child.kill("SIGKILL");
    }, TIMEOUT_MS);

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

    child.on("error", (err) => {
      clearTimeout(timer);
      resolvePromise({
        ok: false,
        controlled_failure: true,
        error: "Spawn error",
        details: err.message,
      });
    });

    child.on("close", (code, signal) => {
      clearTimeout(timer);
      try {
        if (stdout.trim()) {
          resolvePromise(JSON.parse(stdout));
          return;
        }
      } catch (error) {
        resolvePromise({
          ok: false,
          controlled_failure: true,
          error: "JSON parse error",
          details: stdout || stderr || String(error),
          code,
        });
        return;
      }

      resolvePromise({
        ok: false,
        controlled_failure: true,
        error: signal === "SIGKILL" ? "Tool timed out" : "Empty response",
        details: stderr || "",
        code,
      });
    });
  });
}

function buildTextResult(result) {
  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}

function requirePath(params) {
  const pathValue = typeof params?.path === "string" ? params.path.trim() : "";
  if (!pathValue) {
    throw new Error("Missing path argument");
  }
  return pathValue;
}

function registerSimpleTool(api, tool) {
  api.registerTool({
    name: tool.name,
    description: tool.description,
    parameters: tool.parameters,
    async execute(_id, params) {
      try {
        const args = tool.buildArgs(params);
        const result = await runJsonScript(tool.scriptPath, args);
        return buildTextResult(result);
      } catch (error) {
        return buildTextResult({
          ok: false,
          controlled_failure: true,
          error: error instanceof Error ? error.message : String(error),
        });
      }
    },
  });
}

export default {
  id: "lucy-machine-agent-tools",
  name: "Lucy Machine Agent Tools",
  description: "Read-only machine capabilities exposed as agent tools for LucyClaw.",
  register(api) {
    const tools = [
      {
        name: "lucy_machine_downloads",
        description: "Lista archivos recientes de Descargas. Usar cuando el usuario pregunta por descargas, archivos descargados o el último archivo descargado.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        scriptPath: ACCESS_SCRIPT,
        buildArgs: () => ["downloads"],
      },
      {
        name: "lucy_machine_ls",
        description: "Lista una carpeta segura de la máquina. Usar cuando el usuario pregunta qué hay en Escritorio, Documentos, Descargas u otra carpeta permitida.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            path: {
              type: "string",
              description: "Ruta segura permitida, por ejemplo /home/lucy-ubuntu/Escritorio",
            },
          },
          required: ["path"],
        },
        scriptPath: ACCESS_SCRIPT,
        buildArgs: (params) => ["ls", requirePath(params)],
      },
      {
        name: "lucy_machine_stat",
        description: "Devuelve metadata de archivo o carpeta segura.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            path: {
              type: "string",
              description: "Ruta segura permitida a archivo o carpeta.",
            },
          },
          required: ["path"],
        },
        scriptPath: ACCESS_SCRIPT,
        buildArgs: (params) => ["stat", requirePath(params)],
      },
      {
        name: "lucy_machine_status",
        description: "Devuelve estado general de la PC: CPU, RAM, disco, GPU/VRAM y procesos principales. Usar cuando el usuario pregunta qué hay activo, cómo está la PC o rendimiento general.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        scriptPath: STATUS_SCRIPT,
        buildArgs: () => ["status"],
      },
      {
        name: "lucy_machine_processes",
        description: "Lista procesos activos principales. Usar cuando el usuario pregunta qué programas o procesos están corriendo.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        scriptPath: STATUS_SCRIPT,
        buildArgs: () => ["processes"],
      },
      {
        name: "lucy_machine_ram",
        description: "Devuelve estado de RAM. Usar cuando el usuario pregunta por memoria RAM.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        scriptPath: STATUS_SCRIPT,
        buildArgs: () => ["ram"],
      },
      {
        name: "lucy_machine_gpu",
        description: "Devuelve estado de GPU y VRAM. Usar cuando el usuario pregunta por GPU, placa de video, RTX 5090 o VRAM.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        scriptPath: STATUS_SCRIPT,
        buildArgs: () => ["gpu"],
      },
      {
        name: "lucy_machine_disk",
        description: "Devuelve estado de disco y almacenamiento.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        scriptPath: STATUS_SCRIPT,
        buildArgs: () => ["disk"],
      },
      {
        name: "lucy_machine_read",
        description: "Lee texto de un documento seguro permitido: txt, md, json, csv, log, docx o pdf. Usar cuando el usuario pide leer un archivo o documento.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            path: {
              type: "string",
              description: "Ruta segura permitida al documento.",
            },
          },
          required: ["path"],
        },
        scriptPath: READ_SCRIPT,
        buildArgs: (params) => ["read", requirePath(params)],
      },
      {
        name: "lucy_machine_doc_brief",
        description: "Devuelve metadata y extracto de un documento seguro. Usar cuando el usuario pide un vistazo o qué contiene un documento; devuelve extracto literal, no resumen profundo.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            path: {
              type: "string",
              description: "Ruta segura permitida al documento.",
            },
          },
          required: ["path"],
        },
        scriptPath: READ_SCRIPT,
        buildArgs: (params) => ["brief", requirePath(params)],
      },
    ];

    for (const tool of tools) {
      registerSimpleTool(api, tool);
    }
  },
};
