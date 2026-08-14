# Pi

The `pi` package stows `~/.pi/agent` configuration and extensions.

- `pi-model-filter` filters provider models with `model-filter.json`; its standalone project documentation remains in `pi/pi-model-filter/README.md`.
- `pi-ollama-models` discovers models from an Ollama-compatible endpoint, updates the tracked provider model list atomically, and leaves the persisted list unchanged on discovery failure.
- `pi-tmux-agent-indicator` maps Pi lifecycle events to `tmux-agent-indicator` states and does nothing when the plugin is absent.

Each extension subproject contains its own validation commands and runtime documentation.
