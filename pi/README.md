# Pi coding agent setup

The `pi` directory is a GNU Stow package for `~/.pi/agent`.

## tmux-agent-indicator

`pi/pi-tmux-agent-indicator/` contains the local Pi extension that sends Pi
lifecycle states to `tmux-agent-indicator`. Stow deploys it as
`~/.pi/agent/extensions/pi-tmux-agent-indicator.ts`.

The extension calls the indicator's `agent-state.sh` asynchronously and maps:

- `before_agent_start` / `tool_execution_start` to `running`;
- `agent_settled` to `done`;
- `session_shutdown` to `off`.

It remains a no-op when the tmux plugin is not installed. The tracked
`pi/patches/tmux-agent-indicator-session-dots.patch` makes running and done
states visible in every session dot; `scripts/setup-tmux.sh` applies it after
TPM installs the plugin.

Validate it with:

```sh
cd pi/pi-tmux-agent-indicator
npm install
npm test
npm run typecheck
```
