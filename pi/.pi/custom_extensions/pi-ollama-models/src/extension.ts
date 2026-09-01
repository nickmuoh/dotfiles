import {
  chmod,
  readFile,
  realpath,
  rename,
  rm,
  stat,
  writeFile,
} from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { dirname, join } from "node:path";

export type JsonObject = Record<string, unknown>;
export type FetchLike = (input: string, init?: RequestInit) => Promise<Response>;
export interface PiRegistration {
  registerProvider(name: string, config: JsonObject): void;
  // Extension API also includes registerCommand and registerTool, but we use any casting
  registerCommand?: (name: string, options: any) => void;
  registerTool?: (tool: any) => void;
}
export interface StartupDependencies {
  getAgentDir: () => string | Promise<string>;
  fetchFn?: FetchLike;
  timeoutMs?: number;
}

const DEFAULT_TIMEOUT_MS = 1_000;
const MAX_TIMEOUT_MS = 10_000;

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function modelNames(payload: unknown): string[] {
  if (!isObject(payload)) return [];
  const models = Array.isArray((payload as any).data) ? (payload as any).data : (payload as any).models;
  if (!Array.isArray(models)) return [];
  return models
    .map((model) => typeof model === "string" ? model : isObject(model) ? model.id ?? model.name : undefined)
    .filter((id): id is string => typeof id === "string" && id.length > 0);
}

function stableNames(names: string[]): string[] {
  return [...new Set(names)].sort((a, b) => a.localeCompare(b));
}

export function buildModelsConfig(config: JsonObject, names: string[]): JsonObject {
  const providers = isObject(config.providers) ? config.providers : undefined;
  const provider = providers?.ollama;
  if (!isObject(provider)) throw new Error("providers.ollama is missing");
  const overrides = isObject(provider.modelOverrides) ? provider.modelOverrides : {};
  const models = stableNames(names).map((id) => ({
    ...(isObject(overrides[id]) ? overrides[id] : {}),
    id,
  }));
  return {
    ...config,
    providers: { ...providers, ollama: { ...provider, models } },
  };
}

function modelForRegistration(model: JsonObject, providerCompat?: JsonObject): JsonObject {
  const id = model.id;
  if (typeof id !== "string" || id.length === 0) {
    throw new Error("Ollama model entries must have a non-empty id");
  }
  const modelCompat = isObject(model.compat) ? model.compat : undefined;
  const compat = providerCompat || modelCompat ? { ...providerCompat, ...modelCompat } : undefined;
  return {
    ...model,
    id,
    name: typeof model.name === "string" ? model.name : id,
    reasoning: typeof model.reasoning === "boolean" ? model.reasoning : false,
    input: Array.isArray(model.input) ? model.input : ["text"],
    cost: isObject(model.cost) ? model.cost : { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: typeof model.contextWindow === "number" ? model.contextWindow : 128_000,
    maxTokens: typeof model.maxTokens === "number" ? model.maxTokens : 16_384,
    ...(compat ? { compat } : {}),
  };
}

export function providerForRegistration(provider: JsonObject): JsonObject {
  const registration: JsonObject = {};
  for (const key of ["name", "baseUrl", "apiKey", "api", "headers", "authHeader", "oauth", "streamSimple", "refreshModels"]) {
    if (key in provider) registration[key] = (provider as any)[key];
  }
  const providerCompat = isObject(provider.compat) ? provider.compat : undefined;
  registration.models = Array.isArray(provider.models)
    ? provider.models.filter(isObject).map((model) => modelForRegistration(model, providerCompat))
    : [];
  return registration;
}

function requestHeaders(provider: JsonObject): Record<string, string> | undefined {
  const headers: Record<string, string> = {};
  if (isObject(provider.headers)) {
    for (const [k, v] of Object.entries(provider.headers)) {
      if (typeof v === "string") headers[k] = v;
    }
  }
  const apiKey = provider.apiKey;
  const isLiteral = typeof apiKey === "string" && apiKey.trim().length > 0 && !apiKey.startsWith("!") && !apiKey.includes("$");
  if (provider.authHeader === true && isLiteral) {
    headers.Authorization = `Bearer ${apiKey}`;
  }
  return Object.keys(headers).length > 0 ? headers : undefined;
}

function boundedTimeout(timeoutMs: number): number {
  if (!Number.isFinite(timeoutMs)) return DEFAULT_TIMEOUT_MS;
  return Math.min(MAX_TIMEOUT_MS, Math.max(1, Math.floor(timeoutMs)));
}

export async function writeModelsConfig(
  modelsPath: string,
  config: JsonObject,
  names: string[],
): Promise<{ changed: boolean; path: string }> {
  const target = await realpath(modelsPath);
  const original = await readFile(target, "utf8");
  const next = `${JSON.stringify(buildModelsConfig(config, names), null, 2)}\n`;
  if (original === next) return { changed: false, path: target };
  const temporaryFile = join(dirname(target), `.models.json.${randomUUID()}.tmp`);
  try {
    const mode = (await stat(target)).mode & 0o777;
    await writeFile(temporaryFile, next, { encoding: "utf8", mode, flag: "wx" });
    await chmod(temporaryFile, mode);
    await rename(temporaryFile, target);
    return { changed: true, path: target };
  } finally {
    await rm(temporaryFile, { force: true });
  }
}

export async function discoverAndSync(
  modelsPath: string,
  fetchFn: FetchLike = fetch,
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<{ config: JsonObject; names: string[]; changed: boolean }> {
  const target = await realpath(modelsPath);
  const config = JSON.parse(await readFile(target, "utf8")) as unknown;
  if (!isObject(config)) throw new Error("models.json must contain an object");
  const providers = isObject(config.providers) ? config.providers : undefined;
  const provider = providers?.ollama;
  if (!isObject(provider) || typeof provider.baseUrl !== "string") {
    throw new Error("providers.ollama.baseUrl is missing");
  }
  const endpoint = `${provider.baseUrl.replace(/\/+$/, "")}/models`;
  const response = await fetchFn(endpoint, {
    headers: requestHeaders(provider),
    signal: AbortSignal.timeout(boundedTimeout(timeoutMs)),
  });
  if (!response.ok) throw new Error(`Ollama models request failed (${response.status})`);
  const names = stableNames(modelNames(await response.json()));
  const result = await writeModelsConfig(modelsPath, config, names);
  return { config: buildModelsConfig(config, names), names, changed: result.changed };
}

export async function startPiOllamaModels(pi: PiRegistration, deps: StartupDependencies): Promise<void> {
  const modelsPath = join(await deps.getAgentDir(), "models.json");
  let config: JsonObject;
  try {
    config = (await discoverAndSync(modelsPath, deps.fetchFn, deps.timeoutMs)).config;
  } catch (error) {
    try {
      const persisted = JSON.parse(await readFile(await realpath(modelsPath), "utf8")) as unknown;
      if (!isObject(persisted)) throw new Error("models.json must contain an object");
      config = persisted;
      console.warn(`[pi-ollama-models] discovery failed; using existing models: ${String(error)}`);
    } catch (fallbackError) {
      console.warn(`[pi-ollama-models] disabled: ${String(fallbackError)}`);
      return;
    }
  }
  const providers = isObject(config.providers) ? config.providers : undefined;
  const provider = providers?.ollama;
  if (isObject(provider)) pi.registerProvider("ollama", providerForRegistration(provider));

  // Register slash command for manual use
  pi.registerCommand?.("ollama-status", {
    description: "Show Ollama connection status and model sync",
    handler: async (_args: unknown, ctx: any) => {
      const modelsPath = join(await (await import("@earendil-works/pi-coding-agent")).getAgentDir(), "models.json");
      try {
        const { config, names, changed } = await discoverAndSync(modelsPath, undefined, undefined);
        const prov = (config as any)?.providers?.ollama;
        const serverCount = names.length;
        const registeredCount = Array.isArray(prov?.models) ? prov.models.length : 0;
        const baseUrl = prov?.baseUrl ?? "(unknown)";
        const syncMsg = changed ? "⚠️ Mismatch (out of sync)" : "✅ Synced";
        const statusText = `✅ Ollama Online | Server: ${serverCount} | Registered: ${registeredCount} | ${syncMsg}\nBase URL: ${baseUrl}`;
ctx.ui.notify(statusText, "info");
return undefined;
      } catch (e) {
        return `❌ Ollama Offline: ${String(e)}`;
      }
    },
  });

  // Register tool for LLM access (status)
  pi.registerTool?.({
    name: "ollama_status",
    label: "Ollama Status",
    description: "Return Ollama connection and sync status",
    parameters: { type: "object", properties: {} },
    async execute(_toolCallId: any, _params: any, _signal: any, _onUpdate: any, _ctx: any) {
      const modelsPath = join(await (await import("@earendil-works/pi-coding-agent")).getAgentDir(), "models.json");
      try {
        const { config, names, changed } = await discoverAndSync(modelsPath, undefined, undefined);
        const prov = (config as any)?.providers?.ollama;
        const serverCount = names.length;
        const registeredCount = Array.isArray(prov?.models) ? prov.models.length : 0;
        const baseUrl = prov?.baseUrl ?? "(unknown)";
        const syncMsg = changed ? "⚠️ Mismatch (out of sync)" : "✅ Synced";
        return { content: [{ type: "text", text: `✅ Ollama Online | Server: ${serverCount} | Registered: ${registeredCount} | ${syncMsg}\nBase URL: ${baseUrl}` }], details: {} };
      } catch (e) {
        return { content: [{ type: "text", text: `❌ Ollama Offline: ${String(e)}` }], details: {} };
      }
    },
  });

  // Register slash command for refresh
  pi.registerCommand?.("ollama-refresh", {
    description: "Refresh Ollama model list and update configuration",
    handler: async (_args: unknown, ctx: any) => {
      const modelsPath = join(await (await import("@earendil-works/pi-coding-agent")).getAgentDir(), "models.json");
      try {
        const { config, names, changed } = await discoverAndSync(modelsPath, undefined, undefined);
        const prov = (config as any)?.providers?.ollama;
        const serverCount = names.length;
        const registeredCount = Array.isArray(prov?.models) ? prov.models.length : 0;
        const baseUrl = prov?.baseUrl ?? "(unknown)";
        const syncMsg = changed ? "⚠️ Updated (was out of sync)" : "✅ Already up‑to‑date";
        const refreshText = `🔄 Ollama Refresh | Server: ${serverCount} | Registered: ${registeredCount} | ${syncMsg}\nBase URL: ${baseUrl}`;
ctx.ui.notify(refreshText, "info");
return undefined;
      } catch (e) {
        return `❌ Ollama Refresh failed: ${String(e)}`;
      }
    },
  });

  // Register tool for refresh
  pi.registerTool?.({
    name: "ollama_refresh",
    label: "Ollama Refresh",
    description: "Refresh Ollama model list",
    parameters: { type: "object", properties: {} },
    async execute(_toolCallId: any, _params: any, _signal: any, _onUpdate: any, _ctx: any) {
      const modelsPath = join(await (await import("@earendil-works/pi-coding-agent")).getAgentDir(), "models.json");
      try {
        const { config, names, changed } = await discoverAndSync(modelsPath, undefined, undefined);
        const prov = (config as any)?.providers?.ollama;
        const serverCount = names.length;
        const registeredCount = Array.isArray(prov?.models) ? prov.models.length : 0;
        const baseUrl = prov?.baseUrl ?? "(unknown)";
        const syncMsg = changed ? "⚠️ Updated (was out of sync)" : "✅ Already up‑to‑date";
        return { content: [{ type: "text", text: `🔄 Ollama Refresh | Server: ${serverCount} | Registered: ${registeredCount} | ${syncMsg}\nBase URL: ${baseUrl}` }], details: {} };
      } catch (e) {
        return { content: [{ type: "text", text: `❌ Ollama Refresh failed: ${String(e)}` }], details: {} };
      }
    },
  });
}

export default async function piOllamaModels(pi: PiRegistration): Promise<void> {
  try {
    const module = await import("@earendil-works/pi-coding-agent") as { getAgentDir(): string };
    await startPiOllamaModels(pi, { getAgentDir: module.getAgentDir });
  } catch (error) {
    console.warn(`[pi-ollama-models] disabled: ${String(error)}`);
  }
}
