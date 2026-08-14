# Treemux sidebar

The `treemux` package stows `~/.tmux/plugins/treemux/configs/treemux_init.lua`.

Treemux runs a separate Neovim sidebar process, independent of the main LazyVim editor. It uses `nvim-tree`, `nvim-tree-remote.nvim`, filesystem watchers, and reload-on-buffer-enter. The main editor does not load a tree plugin.

`~/.tmux.conf` selects `nvim-tree` and the Python environment created by `scripts/setup-treemux.sh` at `~/.local/share/treemux-venv/`.

## Keybindings

`prefix` is `Ctrl-a` in this tmux configuration. The sidebar is a Neovim
window: use these tree keys only after focusing it.

### Sidebar controls

| Key | Action |
| --- | --- |
| `prefix + Tab` | Toggle the sidebar. |
| `prefix + Backspace` | Toggle the sidebar and focus it. |

### nvim-tree navigation and opening

Treemux first installs `nvim-tree`'s default buffer-local mappings, then
replaces the following bindings to send the selected path to the main editor
or a tmux split.

| Key | Action |
| --- | --- |
| `R` | Refresh the tree. |
| `u` | Change the tree root to the selected directory. |
| `h` | Close the current directory node. |
| `Enter`, `l`, `Ctrl-t`, or double-click | Open the selected path in Treemux. |
| `o` | Open the selected path in the main pane without creating a tmux split. |
| `v` or `Ctrl-v` | Open the selected path in a vertical tmux split. |
| `Ctrl-x` | Open the selected path in a horizontal tmux split. |
| `F1` | Show information about the selected node. |

The remaining default `nvim-tree` mappings are available in the sidebar and
depend on the installed plugin version; use its in-editor help for the live
keymap.

### File-explorer switching

| Key | Action |
| --- | --- |
| `Space o` | Toggle between `nvim-tree` and Oil while preserving the selected file or directory. |
| `Space nn` | Toggle Neo-tree. |

In the Neo-tree window, `Space o` opens the selected location in Oil. Neo-tree
also routes its normal file-open requests through Treemux, so files still open
in the main editor instead of the sidebar process.
