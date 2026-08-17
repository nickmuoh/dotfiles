# tmux

The `tmux` package manages `~/.tmux.conf` and configures TPM plugins.

## Current configuration

- tmux uses `tmux-256color`, truecolor terminal features, CSI-u extended keys, `Ctrl-A` prefix, one-based pane/window numbering, mouse mode, and a bottom status bar.
- `update-environment` carries the D-Bus, GNOME keyring, and runtime-directory variables from attaching clients into tmux.
- The status bar combines Nord styling, prefix highlighting, CPU/MEM metrics, and tmux-agent-indicator session markers (numbered icons identify idle sessions).
- `tmux-menus` opens a popup menu with `prefix + \\`; `prefix + Ctrl-Y` opens Lazygit and `prefix + Ctrl-T` opens a shell popup.
- `tmux-fzf` replaces `prefix + f` with its selector.
- Copy mode uses Vim keys: `Space` starts selection, `y` copies and exits, and `q` exits.

## Layout keys

`Ctrl-W` or `prefix + Ctrl-W` enters the layout table: `h`/`j`/`k`/`l` moves
focus, uppercase variants swap panes, `z` toggles zoom, `|` and `-` split, `x`
closes a pane, and `1` through `4` select common layouts. `Tab` and `Shift-Tab`
mark selector items where tmux-fzf supports multiple selection.

Reload a running server with `tmux source-file ~/.tmux.conf`; never run `tmux kill-server` inside a session.

See [`treemux.md`](treemux.md) for the sidebar and [`tmux-cpu-mem-monitor.md`](tmux-cpu-mem-monitor.md) for the vendored metric wrapper.
