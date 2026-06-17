# shell_setup agent guide

This folder is living docs for `/home/nmuoh` shell and editor setup. Update docs when real config changes.

## Keep in sync

- Change `~/.bashrc` or `~/.bash_aliases` → update `bash/README.md`, `bat.md`, `fzf/README.md`, `gh.md`, `jq.md`, `starship/README.md`, `yq.md`, `zoxide.md`
- Change `~/.config/micro/*` or Micro plugins → update `micro/README.md`, `INSTALL.md`, and the plugin notes there
- Change `~/.tmux.conf` or tmux plugins → update `tmux/README.md` and `INSTALL.md`
- Change `~/.config/nvim/*` or Neovim plugins → update `nvim/README.md`, `neotree.md`, and `INSTALL.md`
- Add new tool or plugin → reflect it in `shell_setup` docs and `INSTALL.md`
- Change install steps for any tool/plugin → update `INSTALL.md`

## What this folder is for

- Record current state, not theory
- Explain why a tool/plugin is installed
- Note plugin repos, keybindings, commands, and dependencies
- Keep `README.md` package index current

## Micro specifics

- `settings.json` = plugin repos, options, status line, keybindings
- `bindings.json` = Micro keybindings
- `palettero.cfg` = custom palette commands
- `~/.config/micro/plug/` = installed plugin sources
- When adding a Micro plugin, document repo URL, install command, and extra deps

## Tmux safety

- **Never kill tmux server while running inside a session** — use `tmux source-file ~/.tmux.conf` to reload config instead
- Killing the server from within a session interrupts the current CLI context
- Only kill tmux if running from outside all sessions (check: `echo $TMUX` should be empty)

## Style

- Be brief, factual, current
- Prefer one doc per tool
- Do not create extra planning notes here
