# GitHub Copilot CLI

AI coding assistant for the terminal, installed as a gh extension wrapper.

## Install

```sh
curl -sSfL https://gh.io/copilot-install | bash
```

`setup-tools.sh` checks for `copilot` before running the installer. It runs this installer with `bash` because the installer uses Bash syntax. The setup library creates and exports `TMPDIR` when needed before installer scripts run.

## Config directory

`~/.copilot/` — runtime state lives here (session DB, logs, OAuth tokens) and is not tracked. `settings.json` and `mcp-config.json` are managed by the `copilot` stow package in this repo.

Bootstrap also installs `gnome-keyring` and `libsecret-1-0` so Copilot can use the system vault on Linux/WSL.
