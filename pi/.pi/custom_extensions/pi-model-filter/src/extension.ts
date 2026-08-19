import { readFileSync, watch, type FSWatcher } from "node:fs";
import { join } from "node:path";

// ---------------------------------------------------------------------------
// Configuration and matching
// ---------------------------------------------------------------------------

export type Logger = { warn(message: string): void };
export type ContextWindowMatch = { min?: number; max?: number };
export interface FilterRule {
  provider: string;
  action: "allow" | "block";
  match: {
    ids?: string[];
    patterns?: string[];
    reasoning?: boolean;
    contextWindow?: ContextWindowMatch;
  };
}
export interface FilterConfig {
  rules: FilterRule[];
  defaultAction: "allow" | "block";
}
export interface ConfigStore {
  current(): FilterConfig;
  replace(config: FilterConfig): void;
}

const FAIL_OPEN_CONFIG: FilterConfig = { rules: [], defaultAction: "allow" };

function isValidBound(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0;
}

function validateContextWindow(
  value: unknown,
  log: Logger,
): ContextWindowMatch | undefined {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    log.warn("contextWindow must be an object");
    return undefined;
  }

  const object = value as Record<string, unknown>;
  const hasMin = "min" in object;
  const hasMax = "max" in object;
  if (!hasMin && !hasMax) {
    log.warn("contextWindow must have at least one of min or max");
    return undefined;
  }

  const min = object.min;
  const max = object.max;
  if (min !== undefined && !isValidBound(min)) {
    log.warn("contextWindow.min must be a finite non-negative number");
    return undefined;
  }
  if (max !== undefined && !isValidBound(max)) {
    log.warn("contextWindow.max must be a finite non-negative number");
    return undefined;
  }
  if (min !== undefined && max !== undefined && min > max) {
    log.warn("contextWindow.min must be <= contextWindow.max");
    return undefined;
  }

  const result: ContextWindowMatch = {};
  if (min !== undefined) result.min = min;
  if (max !== undefined) result.max = max;
  return result;
}

function validateMatch(value: unknown, log: Logger): FilterRule["match"] | undefined {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    log.warn("each rule must have a match object");
    return undefined;
  }

  const match = value as Record<string, unknown>;
  const result: FilterRule["match"] = {};
  let hasField = false;

  for (const field of ["ids", "patterns"] as const) {
    const raw = match[field];
    if (raw === undefined) continue;
    if (!Array.isArray(raw) || raw.length === 0 || !raw.every((item) => typeof item === "string")) {
      log.warn(`match.${field} must be a non-empty array`);
      return undefined;
    }
    result[field] = raw.slice();
    hasField = true;
  }

  if (match.reasoning !== undefined) {
    if (typeof match.reasoning !== "boolean") {
      log.warn("match.reasoning must be a boolean");
      return undefined;
    }
    result.reasoning = match.reasoning;
    hasField = true;
  }

  if (match.contextWindow !== undefined) {
    const contextWindow = validateContextWindow(match.contextWindow, log);
    if (!contextWindow) return undefined;
    result.contextWindow = contextWindow;
    hasField = true;
  }

  if (!hasField) {
    log.warn("match must contain at least one of: ids, patterns, reasoning, contextWindow");
    return undefined;
  }
  return result;
}

function validateRule(value: unknown, log: Logger): FilterRule | undefined {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    log.warn("each rule must be an object");
    return undefined;
  }
  const rule = value as Record<string, unknown>;
  if (typeof rule.provider !== "string" || rule.provider.length === 0) {
    log.warn("rule.provider must be a non-empty string or '*'");
    return undefined;
  }
  if (rule.action !== "allow" && rule.action !== "block") {
    log.warn('rule.action must be "allow" or "block"');
    return undefined;
  }
  const match = validateMatch(rule.match, log);
  return match ? { provider: rule.provider, action: rule.action, match } : undefined;
}

export function validateConfig(raw: unknown, log: Logger): FilterConfig | undefined {
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) {
    log.warn("config must be a JSON object");
    return undefined;
  }
  const object = raw as Record<string, unknown>;
  const defaultAction = object.defaultAction === undefined ? "allow" : object.defaultAction;
  if (defaultAction !== "allow" && defaultAction !== "block") {
    log.warn('defaultAction must be "allow" or "block"');
    return undefined;
  }
  if (object.rules === undefined) return { rules: [], defaultAction };
  if (!Array.isArray(object.rules)) {
    log.warn("rules must be an array");
    return undefined;
  }

  const rules: FilterRule[] = [];
  object.rules.forEach((value, index) => {
    const rule = validateRule(value, log);
    if (rule) rules.push(rule);
    else log.warn(`skipping invalid rule at index ${index}`);
  });
  return { rules, defaultAction };
}

export function loadConfig(path: string, log: Logger): FilterConfig {
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8"));
    const config = validateConfig(parsed, log);
    if (config) return config;
    log.warn("pi-model-filter: invalid config, failing open");
  } catch (error: unknown) {
    if (!(error && typeof error === "object" && "code" in error && error.code === "ENOENT")) {
      log.warn(`pi-model-filter: failed to read config: ${String(error)}, failing open`);
    }
  }
  return { ...FAIL_OPEN_CONFIG };
}

export function createConfigStore(path: string, log: Logger): ConfigStore {
  let current = loadConfig(path, log);
  return {
    current: () => current,
    replace: (next) => {
      current = next;
    },
  };
}

export interface WatcherHandle { close(): void }
export function startConfigWatcher(store: ConfigStore, log: Logger, path: string): WatcherHandle {
  let timer: ReturnType<typeof setTimeout> | undefined;
  let watcher: FSWatcher | undefined;
  const reload = () => {
    try { store.replace(loadConfig(path, log)); }
    catch (error: unknown) { log.warn(`pi-model-filter: config reload error: ${String(error)}`); }
  };
  try {
    watcher = watch(path, { persistent: false }, () => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => { timer = undefined; reload(); }, 200);
    });
    watcher.on("error", (error) => log.warn(`pi-model-filter: watcher error: ${String(error)}`));
  } catch (error: unknown) {
    log.warn(`pi-model-filter: failed to watch config: ${String(error)}`);
  }
  return {
    close() {
      if (timer) clearTimeout(timer);
      timer = undefined;
      watcher?.close();
      watcher = undefined;
    },
  };
}

export interface ModelLike { provider: string; id: string; reasoning?: boolean; contextWindow?: number }
export function globMatch(pattern: string, value: string): boolean {
  try {
    const escaped = pattern.replace(/[.+^${}()|[\]\\]/g, "\\$&");
    return new RegExp(`^${escaped.replace(/\*/g, ".*").replace(/\?/g, ".")}$`).test(value);
  } catch {
    // A malformed runtime rule must never become a broad match.
    return false;
  }
}

function contextMatches(match: ContextWindowMatch, value: unknown): boolean {
  const { min, max } = match;
  return (min !== undefined || max !== undefined) &&
    (min === undefined || isValidBound(min)) &&
    (max === undefined || isValidBound(max)) &&
    (min === undefined || max === undefined || min <= max) &&
    typeof value === "number" && Number.isFinite(value) &&
    (min === undefined || value >= min) && (max === undefined || value <= max);
}

export function ruleMatches(rule: FilterRule, model: ModelLike): boolean {
  if (rule.provider !== "*" && rule.provider !== model.provider) return false;
  const match = rule.match;
  let hasMatcher = false;
  if (match.ids) { hasMatcher = true; if (!match.ids.includes(model.id)) return false; }
  if (match.patterns) { hasMatcher = true; if (!match.patterns.some((pattern) => globMatch(pattern, model.id))) return false; }
  if (match.reasoning !== undefined) { hasMatcher = true; if (Boolean(model.reasoning) !== match.reasoning) return false; }
  if (match.contextWindow) { hasMatcher = true; if (!contextMatches(match.contextWindow, model.contextWindow)) return false; }
  return hasMatcher;
}

export function isBlocked(config: FilterConfig, model: ModelLike): boolean {
  for (const rule of config.rules) if (ruleMatches(rule, model)) return rule.action === "block";
  return config.defaultAction === "block";
}

// ---------------------------------------------------------------------------
// ModelRegistry patch
// ---------------------------------------------------------------------------

export const PATCH_STATE = Symbol.for("pi-model-filter.ModelRegistryPatch");
export const RUNTIME_PATCH_STATE = Symbol.for("pi-model-filter.ModelRuntimePatch");
export interface PatchState {
  originals?: Record<string, Function>;
  store: ConfigStore;
  closeWatcher?: () => void;
  failOpen(): void;
  unpatch(): void;
}
export interface RuntimePatchState extends PatchState {}

function isModelLike(value: unknown): value is ModelLike {
  return !!value && typeof value === "object" &&
    typeof (value as any).provider === "string" && typeof (value as any).id === "string";
}

function createBlockedPredicate(
  getStore: () => ConfigStore,
  log: Logger,
): (value: unknown) => boolean {
  return (value: unknown): boolean => {
    if (!isModelLike(value)) return false;
    try {
      return isBlocked(getStore().current(), value);
    } catch (error: unknown) {
      log.warn(`pi-model-filter fail-open after matcher error: ${String(error)}`);
      return false;
    }
  };
}

export function patchModelRegistryPrototype(proto: any, store: ConfigStore, log: Logger): PatchState {
  const required = ["getAll", "getAvailable", "find", "getApiKeyAndHeaders", "refresh"];
  const missing = required.filter((name) => typeof proto?.[name] !== "function");
  if (missing.length) {
    log.warn(`pi-model-filter disabled: ModelRegistry shape changed; missing ${missing.join(", ")}`);
    return { store, failOpen: () => store.replace({ ...FAIL_OPEN_CONFIG }), unpatch: () => {} };
  }

  const existing = proto[PATCH_STATE] as PatchState | undefined;
  if (existing) { existing.store = store; return existing; }
  const originals = {
    getAll: proto.getAll,
    getAvailable: proto.getAvailable,
    find: proto.find,
    getApiKeyAndHeaders: proto.getApiKeyAndHeaders,
  };
  const state = {} as PatchState;
  const blocked = createBlockedPredicate(() => state.store, log);

  proto.getAll = function () { const models = originals.getAll.call(this); return Array.isArray(models) ? models.filter((m: unknown) => !blocked(m)) : models; };
  proto.getAvailable = function () { const models = originals.getAvailable.call(this); return Array.isArray(models) ? models.filter((m: unknown) => !blocked(m)) : models; };
  proto.find = function (provider: string, id: string) { const model = originals.find.call(this, provider, id); return model && !blocked(model) ? model : undefined; };
  proto.getApiKeyAndHeaders = async function (model: unknown) {
    if (blocked(model)) {
      const selected = model as ModelLike;
      return { ok: false, error: `Model "${selected.provider}:${selected.id}" is blocked by pi-model-filter` };
    }
    return originals.getApiKeyAndHeaders.call(this, model);
  };

  state.originals = originals;
  state.store = store;
  state.failOpen = () => state.store.replace({ ...FAIL_OPEN_CONFIG });
  state.unpatch = () => {
    proto.getAll = originals.getAll;
    proto.getAvailable = originals.getAvailable;
    proto.find = originals.find;
    proto.getApiKeyAndHeaders = originals.getApiKeyAndHeaders;
    delete proto[PATCH_STATE];
  };
  proto[PATCH_STATE] = state;
  return state;
}

// ---------------------------------------------------------------------------
// ModelRuntime patch
// ---------------------------------------------------------------------------

const blockedModelError = (model: ModelLike): Error =>
  new Error(`Model "${model.provider}:${model.id}" is blocked by pi-model-filter`);

export function patchModelRuntimePrototype(proto: any, store: ConfigStore, log: Logger): RuntimePatchState {
  const required = ["getModels", "getModel", "getAvailable", "getAvailableSnapshot", "getAuth"];
  const missing = required.filter((name) => typeof proto?.[name] !== "function");
  if (missing.length) {
    log.warn(`pi-model-filter disabled: ModelRuntime shape changed; missing ${missing.join(", ")}`);
    return { store, failOpen: () => store.replace({ ...FAIL_OPEN_CONFIG }), unpatch: () => {} };
  }

  const existing = proto[RUNTIME_PATCH_STATE] as RuntimePatchState | undefined;
  if (existing) { existing.store = store; return existing; }
  const originals = {
    getModels: proto.getModels,
    getModel: proto.getModel,
    getAvailable: proto.getAvailable,
    getAvailableSnapshot: proto.getAvailableSnapshot,
    getAuth: proto.getAuth,
  };
  const state = {} as RuntimePatchState;
  const blocked = createBlockedPredicate(() => state.store, log);
  const filter = (models: unknown): unknown =>
    Array.isArray(models) ? models.filter((model) => !blocked(model)) : models;

  proto.getModels = function (providerId?: string) { return filter(originals.getModels.call(this, providerId)); };
  proto.getModel = function (providerId: string, modelId: string) {
    const model = originals.getModel.call(this, providerId, modelId);
    return blocked(model) ? undefined : model;
  };
  proto.getAvailable = async function (providerId?: string, options?: unknown) {
    return filter(await originals.getAvailable.call(this, providerId, options));
  };
  proto.getAvailableSnapshot = function () { return filter(originals.getAvailableSnapshot.call(this)); };
  proto.getAuth = async function (providerOrModel: unknown, overrides?: unknown) {
    if (isModelLike(providerOrModel) && blocked(providerOrModel)) {
      throw blockedModelError(providerOrModel);
    }
    return originals.getAuth.call(this, providerOrModel, overrides);
  };

  state.originals = originals;
  state.store = store;
  state.failOpen = () => state.store.replace({ ...FAIL_OPEN_CONFIG });
  state.unpatch = () => {
    proto.getModels = originals.getModels;
    proto.getModel = originals.getModel;
    proto.getAvailable = originals.getAvailable;
    proto.getAvailableSnapshot = originals.getAvailableSnapshot;
    proto.getAuth = originals.getAuth;
    delete proto[RUNTIME_PATCH_STATE];
  };
  proto[RUNTIME_PATCH_STATE] = state;
  return state;
}

// ---------------------------------------------------------------------------
// Extension lifecycle
// ---------------------------------------------------------------------------

type SessionContext = {
  ui?: {
    notify?: (message: string, level: "warning") => void;
  };
};

function factoryLogger(): Logger {
  return {
    warn: (message) => console.warn(`[pi-model-filter] ${message}`),
  };
}

function sessionLogger(base: Logger, context: unknown): Logger {
  return {
    warn: (message) => {
      base.warn(message);
      const notify = (context as SessionContext)?.ui?.notify;
      if (typeof notify === "function") notify(message, "warning");
    },
  };
}

export default async function piModelFilter(pi: any): Promise<void> {
  let piModule: any;
  try {
    piModule = await import("@earendil-works/pi-coding-agent");
  } catch (error) {
    console.warn(`[pi-model-filter] disabled: failed to load Pi runtime: ${String(error)}`);
    return;
  }

  const { getAgentDir, ModelRegistry, ModelRuntime } = piModule;
  if (typeof getAgentDir !== "function" || (!ModelRegistry && !ModelRuntime)) {
    console.warn("[pi-model-filter] disabled: getAgentDir or model runtime surfaces not available");
    return;
  }

  const log = factoryLogger();
  const path = join(getAgentDir(), "model-filter.json");
  const store = createConfigStore(path, log);
  const registryPatch = ModelRegistry
    ? patchModelRegistryPrototype(ModelRegistry.prototype, store, log)
    : undefined;
  const runtimePatch = ModelRuntime
    ? patchModelRuntimePrototype(ModelRuntime.prototype, store, log)
    : undefined;
  let watcher: WatcherHandle | undefined;

  pi.on?.("session_start", (_event: unknown, context: unknown) => {
    watcher?.close();
    const logForSession = sessionLogger(log, context);
    watcher = startConfigWatcher(store, logForSession, path);
  });
  pi.on?.("session_shutdown", () => {
    watcher?.close();
    watcher = undefined;
    registryPatch?.failOpen();
    runtimePatch?.failOpen();
  });
}
