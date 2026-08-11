import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** States accepted by agent-state.sh. */
export type AgentState = "running" | "needs-input" | "done" | "off";

/** Minimal interface for the spawn function, replaceable in tests. */
export type SpawnFn = (
  cmd: string,
  args: string[],
  opts: { stdio: "ignore"; detached: boolean },
) => { unref(): void };

// ---------------------------------------------------------------------------
// Plugin path resolution
// ---------------------------------------------------------------------------

const PLUGIN_RELATIVE =
  ".tmux/plugins/tmux-agent-indicator/scripts/agent-state.sh";

/**
 * Returns the absolute path to agent-state.sh, or undefined when the plugin
 * is not installed.
 */
export function resolveAgentStatePath(
  home?: string,
  exists: (path: string) => boolean = existsSync,
): string | undefined {
  const h = home ?? homedir();
  const candidate = join(h, PLUGIN_RELATIVE);
  return exists(candidate) ? candidate : undefined;
}

// ---------------------------------------------------------------------------
// State dispatch
// ---------------------------------------------------------------------------

/**
 * Fire-and-forget call to agent-state.sh.
 *
 * Errors (script not found, tmux not running, etc.) are swallowed so the
 * extension never interrupts Pi. The script is spawned detached and
 * immediately unreffed, so it does not block the Node.js event loop.
 */
export function sendState(
  state: AgentState,
  scriptPath: string,
  spawnFn: SpawnFn = spawn,
): void {
  try {
    const child = spawnFn(scriptPath, ["--agent", "pi", "--state", state], {
      stdio: "ignore",
      detached: true,
    });
    child.unref();
  } catch {
    // Intentionally silent: plugin may not be running or tmux may be absent.
  }
}

// ---------------------------------------------------------------------------
// Extension entry point
// ---------------------------------------------------------------------------

export default function piTmuxAgentIndicator(
  pi: any,
  scriptPath: string | undefined = resolveAgentStatePath(),
  spawnFn: SpawnFn = spawn,
): void {
  if (!scriptPath) {
    // Plugin not installed; extension is a no-op but does not error.
    return;
  }

  // before_agent_start: user submitted a prompt; agent loop is about to start.
  pi.on("before_agent_start", () => {
    sendState("running", scriptPath, spawnFn);
  });

  // tool_execution_start: a tool invocation begins inside a running agent turn.
  pi.on("tool_execution_start", () => {
    sendState("running", scriptPath, spawnFn);
  });

  // agent_settled: Pi will not continue running automatically; agent is idle.
  pi.on("agent_settled", () => {
    sendState("done", scriptPath, spawnFn);
  });

  // session_shutdown: session is ending; clear indicator.
  pi.on("session_shutdown", () => {
    sendState("off", scriptPath, spawnFn);
  });
}
