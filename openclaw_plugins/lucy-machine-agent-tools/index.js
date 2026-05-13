import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PLUGIN_DIR = dirname(fileURLToPath(import.meta.url));
const PYTHON = "/usr/bin/python3";
const TIMEOUT_MS = 15000;
const ACCESS_SCRIPT = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_access_command.py");
const STATUS_SCRIPT = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_status_command.py");
const READ_SCRIPT = resolve(PLUGIN_DIR, "../../scripts/lucy_machine_read_command.py");
const FIREFOX_SCRIPT = resolve(PLUGIN_DIR, "../../scripts/lucy_firefox_command.py");
const BROWSER_E2E_SCRIPT = resolve(PLUGIN_DIR, "../../scripts/lucy_browser_e2e_command.py");
const TELEGRAM_E2E_PREFIX = "🩺 LucyClaw E2E";

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

function normalizeTelegramText(text) {
  return String(text || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function resolveTelegramE2eRequest(text) {
  const normalized = normalizeTelegramText(text);
  if (!normalized) {
    return null;
  }
  if (normalized.includes("mira la pestana adjunta") || normalized.includes("decime que ves")) {
    return { action: "read", args: [] };
  }
  if (normalized.includes("abri el panel") || normalized.includes("panel de prueba")) {
    return { action: "open_panel", args: [] };
  }
  if (normalized.includes("campo telegram local") || normalized.includes("validalo")) {
    return { action: "type_validate", args: ["prueba completa desde Telegram"] };
  }
  if (normalized.includes("pagina 2 e2e") || normalized.includes("volve a la pagina 1")) {
    return { action: "navigate_roundtrip", args: [] };
  }
  return null;
}

function formatTelegramE2eReply(result) {
  if (!result || typeof result !== "object") {
    return `${TELEGRAM_E2E_PREFIX}\n\nError: respuesta inválida del handler local.`;
  }
  if (result.ok) {
    const sections = [TELEGRAM_E2E_PREFIX];
    if (typeof result.message === "string" && result.message.trim()) {
      sections.push(result.message.trim());
    }
    if (typeof result.snapshot === "string" && result.snapshot.trim()) {
      sections.push(result.snapshot.trim());
    }
    return sections.join("\n\n");
  }
  const errorText =
    typeof result.error === "string" && result.error.trim()
      ? result.error.trim()
      : "falló la ejecución local del browser E2E.";
  return `${TELEGRAM_E2E_PREFIX}\n\nError: ${errorText}`;
}

function installTelegramE2eRuntimePatch(api) {
  const replyRuntime = api?.runtime?.channel?.reply;
  if (!replyRuntime || typeof replyRuntime.dispatchReplyFromConfig !== "function") {
    api.logger.warn("lucy-machine-agent-tools: runtime reply dispatcher unavailable for Telegram E2E patch");
    return;
  }
  if (replyRuntime.__lucyTelegramE2ePatched === true) {
    return;
  }

  const originalDispatch = replyRuntime.dispatchReplyFromConfig.bind(replyRuntime);
  replyRuntime.dispatchReplyFromConfig = async function patchedDispatchReplyFromConfig(params) {
    const channel = String(params?.ctx?.Surface ?? params?.ctx?.Provider ?? "").trim().toLowerCase();
    if (channel === "telegram") {
      const inboundText =
        (typeof params?.ctx?.BodyForCommands === "string" && params.ctx.BodyForCommands) ||
        (typeof params?.ctx?.CommandBody === "string" && params.ctx.CommandBody) ||
        (typeof params?.ctx?.RawBody === "string" && params.ctx.RawBody) ||
        (typeof params?.ctx?.Body === "string" && params.ctx.Body) ||
        "";
      const e2eRequest = resolveTelegramE2eRequest(inboundText);
      if (e2eRequest) {
        api.logger.info(
          `lucy-machine-agent-tools: telegram E2E intercept action=${e2eRequest.action}`,
        );
        const result = await runJsonScript(BROWSER_E2E_SCRIPT, [
          e2eRequest.action,
          ...e2eRequest.args,
        ]);
        const queuedFinal = params.dispatcher.sendFinalReply({
          text: formatTelegramE2eReply(result),
        });
        return {
          queuedFinal,
          counts: params.dispatcher.getQueuedCounts(),
        };
      }
    }
    return originalDispatch(params);
  };
  replyRuntime.__lucyTelegramE2ePatched = true;
  api.logger.info("lucy-machine-agent-tools: Telegram E2E runtime patch active");
}

function requirePath(params) {
  const pathValue = typeof params?.path === "string" ? params.path.trim() : "";
  if (!pathValue) {
    throw new Error("Missing path argument");
  }
  return pathValue;
}

function requireUrl(params) {
  const urlValue = typeof params?.url === "string" ? params.url.trim() : "";
  if (!urlValue) {
    throw new Error("Missing url argument");
  }
  return urlValue;
}

function optionalMode(params) {
  const mode = typeof params?.mode === "string" ? params.mode.trim() : "";
  return mode === "window" ? "window" : "tab";
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
    installTelegramE2eRuntimePatch(api);
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
      {
        name: "lucy_firefox_status",
        description: "Verifica si Firefox del host esta disponible o corriendo. Usar antes de abrir Firefox si hace falta confirmar disponibilidad.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        scriptPath: FIREFOX_SCRIPT,
        buildArgs: () => ["status"],
      },
      {
        name: "lucy_firefox_open",
        description: "Abre una URL segura en Firefox visible del host. Usar cuando Diego pide abrir algo en Firefox o que Firefox se abra solo. No lee ni confirma contenido DOM; para lectura/click/playback con evidencia usa una herramienta de navegador automatizable si esta disponible.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            url: {
              type: "string",
              description: "URL http/https segura o about:blank para abrir en Firefox.",
            },
            mode: {
              type: "string",
              enum: ["tab", "window"],
              description: "Abrir en nueva pestana o nueva ventana. Por defecto: tab.",
            },
          },
          required: ["url"],
        },
        scriptPath: FIREFOX_SCRIPT,
        buildArgs: (params) => ["open", requireUrl(params), optionalMode(params)],
      },
    ];

    for (const tool of tools) {
      registerSimpleTool(api, tool);
    }
  },
};
