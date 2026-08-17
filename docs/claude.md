# Claude Code

The `claude` package stows `~/.claude/settings.json`.

Claude Code is installed by `scripts/setup-tools.sh` using the installer at `https://claude.ai/install.sh`.

The managed settings register `UserPromptSubmit`, `PermissionRequest`, and `Stop` hooks for `tmux-agent-indicator`. New Claude processes load these hooks; use `/hooks` in a new tmux session to inspect and trust pending registrations.
