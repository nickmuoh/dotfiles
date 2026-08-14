# Treemux sidebar

The `treemux` package stows `~/.tmux/plugins/treemux/configs/treemux_init.lua`.

Treemux runs a separate Neovim sidebar process, independent of the main LazyVim editor. It uses `nvim-tree`, `nvim-tree-remote.nvim`, filesystem watchers, and reload-on-buffer-enter. The main editor does not load a tree plugin.

`~/.tmux.conf` selects `nvim-tree` and the Python environment created by `scripts/setup-treemux.sh` at `~/.local/share/treemux-venv/`.

## Keybindings

| Key | Action |
| --- | --- |
| `prefix + Tab` | Toggle sidebar |
| `prefix + Backspace` | Toggle and focus sidebar |
| `R` | Refresh tree |
| `o` | Open in main pane |
| `v` / `Ctrl-v` | Open in vertical split |
| `Ctrl-x` | Open in horizontal split |

Additional tree interactions use `Enter`, `l`, `Ctrl-t`, `h`, `u`, `F1`, and `Space o`.
