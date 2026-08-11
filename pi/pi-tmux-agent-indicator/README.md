# pi-tmux-agent-indicator

Pi extension that drives [tmux-agent-indicator](https://github.com/accessd/tmux-agent-indicator) state transitions for Pi lifecycle events.

## How it works

The extension maps Pi lifecycle events to `agent-state.sh` calls:

| Pi event | State sent |
|---|---|
| `before_agent_start` | `running` |
| `tool_execution_start` | `running` |
| `agent_settled` | `done` |
| `session_shutdown` | `off` |

Each call is fire-and-forget: `agent-state.sh` is spawned detached so it never blocks Pi. Errors (tmux absent, script missing) are swallowed silently.

## Requirements

- tmux-agent-indicator installed at `~/.tmux/plugins/tmux-agent-indicator/`
- tmux running (calls are no-ops when tmux is not present)

When the plugin is not installed the extension registers no handlers and does nothing.

## Installation

The package is registered in `pi/.pi/agent/settings.json` as a local path and deployed through the `pi` Stow package:

```sh
stow -nv pi    # preview
stow -v  pi    # apply
```

Pi picks up the package on next start. No manual `pi install` is needed.

## Development

```sh
cd pi/pi-tmux-agent-indicator
npm install
npm test
npm run build
```

## `needs-input` state

The `needs-input` state is intentionally not mapped. Pi has no direct permission-request lifecycle event that reliably signals a blocked state. Add a mapping here when a concrete Pi extension workflow identifies an attention-needed condition.
