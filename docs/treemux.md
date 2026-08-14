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

### Everyday file operations

Use normal Neovim motion keys such as `j` and `k` to select an entry. The
following `nvim-tree` defaults remain available in the sidebar:

| Task | Key | Notes |
| --- | --- | --- |
| Open or expand the selection | `Enter` or `l` | A selected file opens in the main Treemux editor; a directory opens locally in the tree. |
| Close a directory | `h` or `Backspace` | Both close the selected directory node without closing the tree. |
| Make the selected directory the root | `u` or `Ctrl-]` | `u` is the configured shortcut; `Ctrl-]` is the nvim-tree default. |
| Create a file or directory | `a` | Enter a name for a file, or end the name with `/` for a directory. |
| Rename | `r` | `e` renames only the basename. |
| Copy / cut / paste | `c` / `x` / `p` | Select the destination directory before pasting. |
| Delete / move to trash | `d` / `D` | Confirm the prompted operation. |
| Copy filename / relative path / absolute path | `y` / `Y` / `gy` | Copies to the nvim-tree clipboard. |
| Show or hide dotfiles | `H` | |
| Expand or collapse the entire tree | `E` / `W` | |
| Filter entries | `f` / `F` | Start / clear the live filter. |
| Show the live keymap | `g?` | This is the source of truth after plugin updates. |

`-` (change root to the parent directory), `Ctrl-k` (node information), `O`
(open without the window picker), and `q` (close the tree) are intentionally
disabled by the Treemux configuration. The configured `F1` replaces the
node-information shortcut. Use `Ctrl-a Tab` only when you intentionally want
to hide the whole Treemux sidebar.

### Customizing mappings

Mappings are buffer-local and are defined by the `nvim_tree_on_attach`
function in `treemux/.tmux/plugins/treemux/configs/treemux_init.lua`. It first
loads the nvim-tree defaults, then adds, replaces, or removes mappings. To
customize a key, add or replace a `vim.keymap.set` call in that function; use
the nvim-tree API action that describes the intended behavior.

For example, this changes `?` to open the built-in keymap help without
discarding the configured defaults:

```lua
vim.keymap.set("n", "?", api.tree.toggle_help, opts("Help"))
```

Use `g?` before choosing a key: it shows the actual mappings for the installed
nvim-tree version and helps avoid replacing an action you still need.

### File-explorer switching

| Key | Action |
| --- | --- |
| `Space o` | Toggle between `nvim-tree` and Oil while preserving the selected file or directory. |
| `Space nn` | Toggle Neo-tree. |

In the Neo-tree window, `Space o` opens the selected location in Oil. Neo-tree
also routes its normal file-open requests through Treemux, so files still open
in the main editor instead of the sidebar process.
