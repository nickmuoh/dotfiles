# GitHub Copilot CLI

The `copilot` package stows `~/.copilot/settings.json` and `~/.copilot/mcp-config.json`.

Copilot is installed by `scripts/setup-tools.sh` with the GitHub Copilot installer and depends on `gh`. Runtime state, including sessions, logs, and OAuth tokens, remains under `~/.copilot/` and is not tracked. Bootstrap installs `gnome-keyring` and `libsecret-1-0` for the Linux/WSL system vault.
