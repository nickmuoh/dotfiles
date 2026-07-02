# Treemux file-tree sidebar

## Architecture

Treemux uses a **separate Neovim process** for the sidebar — it is NOT part of the
main editor instance. When the sidebar is toggled (default: `<Tab>`), tmux spawns a
new Neovim pane configured by:

    ~/.tmux/plugins/treemux/configs/treemux_init.lua

This init file bootstraps `lazy.nvim` with its own plugin spec, independent of the
main LazyVim config at `~/.config/nvim/`.

## Active tree client: nvim-tree

The sidebar Neovim uses **nvim-tree** (`nvim-tree/nvim-tree.lua`) as the file explorer.
This is controlled by the tmux option in `~/.tmux.conf`:

    set -g @treemux-tree-client 'nvim-tree'

`nvim-tree-remote.nvim` is also loaded in the sidebar process — it handles the
"open file in main editor pane" communication back to the user's active editor.

The sidebar config also enables `nvim-tree` filesystem watchers, `reload_on_bufenter`,
and `sync_root_with_cwd`, so the tree stays in sync with filesystem changes even
when they happen outside Neovim. Manual refresh is still `R`.

## Plugin install location

The sidebar Neovim shares the same `lazy.nvim` plugin directory as the main editor:

    ~/.local/share/nvim/lazy/

Installed plugins (sidebar-relevant):
- `nvim-tree.lua`
- `nvim-tree-remote.nvim`
- `neo-tree.nvim` (installed but inactive — not the configured client)

## Main editor (LazyVim)

The main Neovim config (`~/.config/nvim/`) uses LazyVim and does **not** load any
file-tree plugin. File navigation in the main editor uses Telescope.

## Treemux init file

`~/.tmux/plugins/treemux/configs/treemux_init.lua` — the Neovim config for the
sidebar process. It is installed by `scripts/setup-treemux.sh` from the tracked
source file `scripts/treemux_init.lua` on every bootstrap run.

## Keybindings (default)

| Key | Action |
|-----|--------|
| `<Tab>` | Toggle sidebar |
| `<Backspace>` | Toggle sidebar + focus |
| `o` | Open file in main pane (new tab) |
| `v` | Open in vertical split |
| `<C-v>` | Open in vertical split |

## Configuration paths

- `~/.tmux.conf` — `@treemux-tree-client`, python path, init file path
- `~/.tmux/plugins/treemux/` — TPM-managed plugin source
- `~/.tmux/plugins/treemux/configs/treemux_init.lua` — sidebar nvim config
- `~/.local/share/treemux-venv/` — Python venv (created by `setup-treemux.sh`)
