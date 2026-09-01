import { chmod, lstat, mkdtemp, readFile, stat, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it, vi } from "vitest";
import { discoverAndSync, startPiOllamaModels } from "../extension.js";

describe("Ollama model discovery", () => {
  it("discovers, deduplicates, sorts, applies overrides, and rewrites the resolved target", async () => {
    const root = await mkdtemp(join(tmpdir(), "ollama-models-test-"));
    const target = join(root, "real-models.json");
    const link = join(root, "models.json");
    await writeFile(target, JSON.stringify({
      other: { untouched: true },
      providers: { ollama: {
        baseUrl: "http://ollama.test/v1/",
        api: "openai-completions",
        modelOverrides: { alpha: { name: "Alpha", contextWindow: 123 } },
        models: [{ id: "old" }],
      } },
    }, null, 2));
    await symlink(target, link);

    const fetchFn = vi.fn(async (url: string) => {
      expect(url).toBe("http://ollama.test/v1/models");
      return new Response(JSON.stringify({ data: [{ id: "zeta" }, { id: "alpha" }, { id: "alpha" }] }), { status: 200 });
    });
    const result = await discoverAndSync(link, fetchFn);
    expect(result.names).toEqual(["alpha", "zeta"]);
    expect(result.changed).toBe(true);
    expect(JSON.parse(await readFile(target, "utf8"))).toMatchObject({
      other: { untouched: true },
      providers: { ollama: { models: [
        { id: "alpha", name: "Alpha", contextWindow: 123 },
        { id: "zeta" },
      ] } },
    });
    expect(await readFile(link, "utf8")).toBe(await readFile(target, "utf8"));
  });

  it("sends configured headers and conditional bearer authentication", async () => {
    const root = await mkdtemp(join(tmpdir(), "ollama-models-test-"));
    const path = join(root, "models.json");
    await writeFile(path, JSON.stringify({ providers: { ollama: {
      baseUrl: "http://x", apiKey: "secret", authHeader: true,
      headers: { "X-Trace": "yes", "X-Number": 42 }, models: [],
    } } }));
    const fetchFn = vi.fn(async (_url: string, init?: RequestInit) => {
      expect(init?.headers).toEqual({ "X-Trace": "yes", Authorization: "Bearer secret" });
      expect(init?.signal).toBeInstanceOf(AbortSignal);
      return new Response(JSON.stringify({ data: [] }));
    });
    await discoverAndSync(path, fetchFn, 10_000);
    expect(fetchFn).toHaveBeenCalledOnce();

    await writeFile(path, JSON.stringify({ providers: { ollama: {
      baseUrl: "http://x", apiKey: "${OLLAMA_API_KEY}", authHeader: true, models: [],
    } } }));
    const noAuthFetch = vi.fn(async (_url: string, init?: RequestInit) => {
      expect(init?.headers).toBeUndefined();
      return new Response(JSON.stringify({ models: [] }));
    });
    await discoverAndSync(path, noAuthFetch);
  });

  it.each([
    ["HTTP", async () => new Response("no", { status: 503 })],
    ["JSON", async () => new Response("not json")],
  ])("leaves persisted JSON untouched on %s discovery failure", async (_kind, fetchFn) => {
    const root = await mkdtemp(join(tmpdir(), "ollama-models-test-"));
    const path = join(root, "models.json");
    const original = JSON.stringify({ providers: { ollama: { baseUrl: "http://x", models: [{ id: "old" }] } } });
    await writeFile(path, original);
    await expect(discoverAndSync(path, fetchFn as never)).rejects.toThrow();
    expect(await readFile(path, "utf8")).toBe(original);
  });

  it("registers persisted models on discovery failure with no writer-only keys", async () => {
    const root = await mkdtemp(join(tmpdir(), "ollama-models-test-"));
    const path = join(root, "models.json");
    await writeFile(path, JSON.stringify({ providers: { ollama: {
      baseUrl: "http://x", api: "openai-completions", apiKey: "key", authHeader: true,
      compat: { supportsDeveloperRole: false, thinkingFormat: "openai" },
      prefix: "/v1", version: 1, filter: "x", modelOverrides: { old: { name: "Old" } },
      models: [{ id: "old", name: "Old" }],
    } } }));
    const pi = { registerProvider: vi.fn() };
    await startPiOllamaModels(pi, { getAgentDir: () => root, fetchFn: async () => { throw new Error("offline"); } });
    expect(pi.registerProvider).toHaveBeenCalledWith("ollama", expect.objectContaining({
      models: [{
        id: "old",
        name: "Old",
        reasoning: false,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128_000,
        maxTokens: 16_384,
        compat: { supportsDeveloperRole: false, thinkingFormat: "openai" },
      }],
    }));
    const registered = pi.registerProvider.mock.calls[0][1];
    expect(registered).not.toHaveProperty("modelOverrides");
    expect(registered).not.toHaveProperty("prefix");
    expect(registered).not.toHaveProperty("version");
    expect(registered).not.toHaveProperty("filter");
  });

  it("registers no-argument tools with object parameter schemas", async () => {
    const root = await mkdtemp(join(tmpdir(), "ollama-models-test-"));
    await writeFile(join(root, "models.json"), JSON.stringify({ providers: { ollama: {
      baseUrl: "http://x", models: [],
    } } }));
    const pi = {
      registerProvider: vi.fn(),
      registerCommand: vi.fn(),
      registerTool: vi.fn(),
    };

    await startPiOllamaModels(pi, {
      getAgentDir: () => root,
      fetchFn: async () => { throw new Error("offline"); },
    });

    expect(pi.registerTool.mock.calls.map(([tool]) => [tool.name, tool.parameters])).toEqual([
      ["ollama_status", { type: "object", properties: {} }],
      ["ollama_refresh", { type: "object", properties: {} }],
    ]);
  });

  it("uses an atomic rewrite that preserves the target mode and symlink", async () => {
    const root = await mkdtemp(join(tmpdir(), "ollama-models-test-"));
    const target = join(root, "real.json");
    const link = join(root, "models.json");
    await writeFile(target, JSON.stringify({ providers: { ollama: { baseUrl: "http://x", models: [] } } }));
    await chmod(target, 0o640);
    await symlink(target, link);
    await discoverAndSync(link, async () => new Response(JSON.stringify({ data: [{ id: "new" }] })));
    expect((await stat(target)).mode & 0o777).toBe(0o640);
    expect((await lstat(link)).isSymbolicLink()).toBe(true);
  });

  it("skips a byte-identical rewrite", async () => {
    const root = await mkdtemp(join(tmpdir(), "ollama-models-test-"));
    const path = join(root, "models.json");
    const config = { providers: { ollama: { baseUrl: "http://x", models: [] } } };
    await writeFile(path, `${JSON.stringify(config, null, 2)}\n`);
    const result = await discoverAndSync(path, async () => new Response(JSON.stringify({ models: [] })));
    expect(result.changed).toBe(false);
  });
});
