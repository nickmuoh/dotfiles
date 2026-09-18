# Pi

The `pi` package stows `~/.pi/agent` configuration and extensions.

Pi's Amazon Bedrock credential is stored in `pi/.pi/agent/auth.json`; its `AWS_PROFILE` must be `claude-bedrock`, which chains the `claude` SSO profile into `SuOps-BedrockInvokeRole`. The global `settings.json` environment is not authoritative when a provider credential already has a stored `env` object.

- `pi-model-filter` filters provider models with `model-filter.json`; its standalone project documentation remains in `pi/pi-model-filter/README.md`.
- `pi-ollama-models` discovers models from an Ollama-compatible endpoint, updates the tracked provider model list atomically, and leaves the persisted list unchanged on discovery failure. Its no-argument tools declare object input schemas for strict providers such as Amazon Bedrock.
- `pi-tmux-agent-indicator` maps Pi lifecycle events to `tmux-agent-indicator` states and does nothing when the plugin is absent.
- `pi/.pi/agent/extensions/cwd-shortener.ts` replaces the interactive footer via `ctx.ui.setFooter` to shorten the working-directory line: the leaf and its immediate parent stay full, every earlier segment collapses to its first character (two characters if that first character isn't a letter/digit, e.g. `_SketchUp` -> `_S`), and the whole line is capped at 80 characters. It rebuilds the stats/cost/context%/model/effort line from public `ExtensionContext` data since Pi's own formatting helpers for that line aren't exported by the package. Single-file extension, no build step, auto-discovered like the others.

Each extension subproject contains its own validation commands and runtime documentation.
