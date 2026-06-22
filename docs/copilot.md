# GitHub Copilot CLI

AI coding assistant for the terminal, installed as a gh extension wrapper.

## Install

```sh
curl -fsSL https://gh.io/copilot-install | bash
```

## Config directory

`~/.copilot/` — runtime state lives here (session DB, logs, OAuth tokens) and is not tracked. `settings.json` and `mcp-config.json` are managed by the `copilot` stow package in this repo.

