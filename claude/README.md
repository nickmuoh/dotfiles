# Claude Code

Stow package for Claude Code CLI config under `~/.claude/`.

## Install

- Repo: `https://claude.ai`
- Installer: `curl -fsSL https://claude.ai/install.sh | bash`
- Bootstrap entry: `claude|https://claude.ai/install.sh||bash`

## Managed files

- `~/.claude/settings.json`

## tmux-agent-indicator hooks

`settings.json` registers `UserPromptSubmit`, `PermissionRequest`, and `Stop`
command hooks for `tmux-agent-indicator`. They mark Claude panes as `running`,
`needs-input`, or `done` through the plugin's `agent-state.sh` command.

Existing Claude processes keep the hooks they loaded at startup. Let active work
finish, then start a new Claude process in tmux. Run `/hooks` in the new session
to inspect and trust any pending command-hook registrations.
