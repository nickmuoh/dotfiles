# Pi coding agent setup

The `pi` directory is a GNU Stow package for `~/.pi/agent`.

## Model filter

`pi/pi-model-filter/` contains the model-list filtering extension. Stow deploys
`~/.pi/agent/extensions/pi-model-filter.ts`, which re-exports the package's
single runtime source file.

Rules in `~/.pi/agent/model-filter.json` filter provider models by exact ID,
glob pattern, reasoning support, or context-window range. Rules use
first-match-wins evaluation and reload when the file changes. Invalid
configuration fails open.

Validate it with:

```sh
cd pi/pi-model-filter
npm install
npm test
npm run typecheck
npm run build
```

## Ollama models

`pi/pi-ollama-models/` contains the Ollama model-discovery extension. Stow
deploys `~/.pi/agent/extensions/pi-ollama-models.ts`, which re-exports the
package's single runtime source file.

The extension reads the `ollama` provider from `~/.pi/agent/models.json`,
queries its OpenAI-compatible `/models` endpoint, applies exact-ID
`modelOverrides`, and updates the provider's `models` array. Updates resolve
the Stow symlink and atomically replace its tracked target. Discovery failures
leave the tracked model list unchanged and register that persisted list.

Model visibility remains controlled by `~/.pi/agent/model-filter.json`.

Validate it with:

```sh
cd pi/pi-ollama-models
npm install
npm test
npm run typecheck
npm run build
```

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
