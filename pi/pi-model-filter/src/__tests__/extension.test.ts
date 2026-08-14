import { describe, expect, it } from "vitest";
import { isBlocked, patchModelRegistryPrototype, validateConfig, type ConfigStore } from "../extension";
const log = { warn: () => {} };
const store = (config: any): ConfigStore => ({ current: () => config, replace: (next) => { config = next; } });
describe("model filter", () => {
  it("validates and evaluates rules", () => { const c = validateConfig({ rules: [{ provider: "*", action: "block", match: { patterns: ["gpt-*"] } }], defaultAction: "allow" }, log); expect(c && isBlocked(c, { provider: "openai", id: "gpt-5" })).toBe(true); expect(validateConfig("bad", log)).toBeUndefined(); });
  it("fails open for malformed runtime matchers", () => {
    const malformed: any = { rules: [{ provider: "*", action: "block", match: { patterns: ["["] } }], defaultAction: "allow" };
    expect(() => isBlocked(malformed, { provider: "openai", id: "anything" })).not.toThrow();
    expect(isBlocked(malformed, { provider: "openai", id: "anything" })).toBe(false);
  });

  it("filters registry methods and supports reload", async () => { const models = [{ provider: "openai", id: "gpt-5" }, { provider: "openai", id: "claude" }]; const proto: any = { getAll() { return models; }, getAvailable() { return models; }, find(p: string, id: string) { return models.find((m) => m.provider === p && m.id === id); }, async getApiKeyAndHeaders(m: any) { return { ok: true, m }; }, refresh() {} }; const s = store({ rules: [{ provider: "*", action: "block", match: { ids: ["gpt-5"] } }], defaultAction: "allow" }); patchModelRegistryPrototype(proto, s, log); expect(proto.getAll()).toEqual([models[1]]); s.replace({ rules: [], defaultAction: "allow" }); expect(proto.find("openai", "gpt-5")).toBe(models[0]); expect((await proto.getApiKeyAndHeaders(models[0])).ok).toBe(true); });
});
