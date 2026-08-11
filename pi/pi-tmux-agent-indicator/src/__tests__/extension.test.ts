import { describe, expect, it } from "vitest";
import {
  default as install,
  resolveAgentStatePath,
  sendState,
  type SpawnFn,
} from "../extension.js";

function makeSpawnFn() {
  const calls: Array<{ cmd: string; args: string[] }> = [];
  let unrefs = 0;
  const spawnFn: SpawnFn = (cmd, args) => {
    calls.push({ cmd, args });
    return { unref: () => { unrefs += 1; } };
  };
  return { spawnFn, calls, get unrefs() { return unrefs; } };
}

describe("sendState", () => {
  it("calls agent-state.sh with the Pi state", () => {
    const helper = makeSpawnFn();
    sendState("running", "/fake/agent-state.sh", helper.spawnFn);
    expect(helper.calls).toEqual([{
      cmd: "/fake/agent-state.sh",
      args: ["--agent", "pi", "--state", "running"],
    }]);
    expect(helper.unrefs).toBe(1);
  });

  it.each(["done", "off"] as const)("passes %s state", (state) => {
    const helper = makeSpawnFn();
    sendState(state, "/fake/agent-state.sh", helper.spawnFn);
    expect(helper.calls[0]?.args).toContain(state);
  });

  it("swallows spawn failures", () => {
    const throwingSpawn: SpawnFn = () => { throw new Error("tmux unavailable"); };
    expect(() => sendState("running", "/fake/agent-state.sh", throwingSpawn)).not.toThrow();
  });
});

describe("resolveAgentStatePath", () => {
  it("returns undefined when the plugin is absent", () => {
    expect(resolveAgentStatePath("/home/user", () => false)).toBeUndefined();
  });

  it("returns the installed helper path", () => {
    expect(resolveAgentStatePath("/home/user", () => true)).toBe(
      "/home/user/.tmux/plugins/tmux-agent-indicator/scripts/agent-state.sh",
    );
  });
});

describe("Pi extension factory", () => {
  it("does nothing when no helper is available", () => {
    const handlers: Record<string, unknown> = {};
    const pi = { on: (event: string, fn: unknown) => { handlers[event] = fn; } };
    // An empty injected path models the missing optional plugin.
    install(pi, "");
    expect(handlers).toEqual({});
  });

  it("registers and dispatches all four lifecycle handlers", () => {
    const handlers: Record<string, () => void> = {};
    const pi = { on: (event: string, fn: () => void) => { handlers[event] = fn; } };
    const helper = makeSpawnFn();
    install(pi, "/fake/agent-state.sh", helper.spawnFn);

    expect(Object.keys(handlers)).toEqual([
      "before_agent_start",
      "tool_execution_start",
      "agent_settled",
      "session_shutdown",
    ]);
    handlers.before_agent_start();
    handlers.tool_execution_start();
    handlers.agent_settled();
    handlers.session_shutdown();
    expect(Object.keys(handlers)).toHaveLength(4);
    expect(helper.calls.map(({ args }) => args.at(-1))).toEqual([
      "running",
      "running",
      "done",
      "off",
    ]);
  });
});
