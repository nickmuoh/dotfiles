# Pi

The `pi` package stows `~/.pi/agent` configuration and extensions.

Pi's Amazon Bedrock credential is stored in `pi/.pi/agent/auth.json`; its `AWS_PROFILE` must be `claude-bedrock`, which chains the `claude` SSO profile into `SuOps-BedrockInvokeRole`. The global `settings.json` environment is not authoritative when a provider credential already has a stored `env` object.

- `pi-model-filter` filters provider models with `model-filter.json`; its standalone project documentation remains in `pi/pi-model-filter/README.md`.
- `pi-ollama-models` discovers models from an Ollama-compatible endpoint, updates the tracked provider model list atomically, and leaves the persisted list unchanged on discovery failure. Its no-argument tools declare object input schemas for strict providers such as Amazon Bedrock.
- `pi-tmux-agent-indicator` maps Pi lifecycle events to `tmux-agent-indicator` states and does nothing when the plugin is absent.

Each extension subproject contains its own validation commands and runtime documentation.
