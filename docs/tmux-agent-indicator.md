# tmux-agent-indicator evaluation

Source inspected: [`accessd/tmux-agent-indicator`](https://github.com/accessd/tmux-agent-indicator), commit `8d2e84b0d76f0494b8851bef5057a536c0ba76c7`.

## Fit for this setup

`tmux-agent-indicator` is an ambient notification layer rather than a sidebar.
It tracks `running`, `needs-input`, and `done` per pane, then exposes state with:

- status-bar indicators through `#{agent_indicator}`;
- cross-session dots through `#{agent_session_dots}`;
- pane borders and window-title colors;
- optional notifications using `tmux display-message`;
- optional process detection fallback.

This better matches the need for passive awareness across several tmux sessions:
state remains visible without opening a popup. It does not provide a detailed
cross-session activity browser; the dots indicate that sessions need attention,
while the existing tmux session/window controls are still used to locate them.

## Pi integration

The plugin exposes a generic command:

```sh
~/.tmux/plugins/tmux-agent-indicator/scripts/agent-state.sh \
  --agent pi --state running
```

Supported states are `running`, `needs-input`, `done`, and `off`. The command
stores pane/session state in tmux global environment variables and can be called
by a Pi extension or wrapper. No Rust adapter or cache protocol is required.

Recommended Pi mapping:

```text
before_agent_start / tool_execution_start → running
agent_settled                              → done
session_shutdown                           → off
```

Pi does not have a direct Claude-style permission-request state, so
`needs-input` should not be emitted until a concrete Pi extension workflow
identifies an attention-needed condition. A later extension can map explicit
user confirmations or queued input to `needs-input`.

Cortex/Coco and Copilot can initially use the plugin's configurable process
fallback for presence-only indication. A wrapper can provide richer transitions
when those tools have a reliable start/finish boundary.

## Cross-session awareness

Enable the session-dot format in the tmux status line:

```tmux
#{agent_session_dots}
```

The project tracks sessions with agent state and highlights the current session
and sessions in configured attention states. This is less detailed than a
sidebar but is always visible and avoids the previous popup-only workflow.

The local patch makes dots a worker-state summary with this precedence per
session: `needs-input` > `running` > `done` > current idle > inactive. The
configured display is:

```text
!  yellow      needs input
◉  bright cyan one or more workers running
✓  green       all tracked workers done
●              current session with no tracked state
○              inactive session with no tracked state
```

Dots are separated by one space. The patch restores the configured Nord
CPU/MEM foreground/background after each colored dot; the icon has two spaces
before it and one after it, so no agent state color can leak into or crowd the
rest of the status line.

The dot order is tmux's `list-sessions` order. A session needs no manually
opened popup to expose its current worker state.

## Bell/notification combination

The plugin's default notifications use `tmux display-message` for `needs-input`
and `done`, including agent/session/window names. Its
`@agent-indicator-notification-command` option can run an additional command.
That provides a seam for a bell experiment:

```tmux
set -g @agent-indicator-notification-enabled on
set -g @agent-indicator-notification-states 'needs-input,done'
```

The safest initial notification is the plugin's display message. If a terminal
BEL is desired, test a helper that targets the source pane's `#{pane_tty}` rather
than injecting input with `tmux send-keys`; terminal BEL behavior depends on the
terminal emulator and tmux bell settings.

The separate tmux bell settings are compatible as an experiment:

```tmux
setw -g monitor-bell on
set -g bell-action other
setw -g window-status-bell-style 'fg=#787487 underscore'
```

Do not assume `tmux display-message` itself rings the terminal bell. Validate
that a BEL written to the pane tty produces the desired inactive-window signal.

## Nord/status-right integration

The plugin replaces placeholders in the status options that already contain
them. This repository's CPU/MEM wrapper rebuilds `status-right`, so the
indicator must be integrated after the CPU/MEM and prefix-highlight run-shell
steps, or the final status string must explicitly include the placeholders
before the indicator entrypoint runs:

```tmux
#{agent_session_dots} #{agent_indicator}
```

Avoid allowing the plugin to own or reconstruct the entire Nord status line.
Use its placeholders as one final appended segment, preserving the existing
CPU/MEM styling and separators.

## Recommended experiment

1. Install the plugin through TPM or a bootstrap clone, but do not enable pane
   background coloring initially.
2. Add `pi` to `@agent-indicator-processes` for fallback detection.
3. Add `#{agent_session_dots} #{agent_indicator}` after the existing CPU/MEM and
   prefix-highlight status segments.
4. Add a small Stow-managed Pi extension that calls `agent-state.sh` asynchronously.
5. Enable `done`/`needs-input` display messages.
6. Test terminal BEL separately; add it only if the inactive-session signal is
   useful and does not disturb the terminal.
7. Keep pane borders/window titles conservative because Nord and Treemux already
   provide visual styling.

This is a focused experiment and should not bring back a persistent sidebar or
popup. Remove it if session dots and notifications do not provide enough context.

## Local implementation

The experiment is implemented in this repository:

- `tmux/.tmux.conf` installs the plugin through TPM, appends its placeholders after the CPU/MEM wrapper, enables the configurable worker-state session dots, and configures Pi (`π`), Cortex, Coco, and Copilot process fallback.
- `pi/patches/tmux-agent-indicator-session-dots.patch` extends the upstream session-dot script, handles stale seen-session markers without blanking the dot segment, and clears `needs-input` once its source pane is focused; `scripts/setup-tmux.sh` applies it after TPM installation.
- `tmux-cpu-mem-monitor/.tmux/plugins/tmux-cpu-mem-monitor/tmux_cpu_mem_monitor.tmux` preserves the Nord CPU/MEM segment while carrying the indicator placeholders to the final interpolation step.
- `pi/pi-tmux-agent-indicator/` contains the Stow-managed Pi extension.
- `pi/.pi/agent/extensions/pi-tmux-agent-indicator.ts` is the deployed extension entrypoint.

The extension is deliberately silent when the plugin is absent and never blocks
Pi while calling `agent-state.sh`.
