# Neovim

The `nvim` package manages the LazyVim-style configuration under `~/.config/nvim/`, including local plugin specifications and `lazy-lock.json`.

`scripts/setup-tools.sh` installs Neovim from the official release tarball in `~/.local/opt/nvim-linux-x86_64/` and links `~/.local/bin/nvim`. After stowing, `scripts/setup-nvim.sh` runs `nvim --headless "+Lazy! sync" +qa`.

## Current configuration

- LazyVim imports local plugins; the configured colorscheme is Nord with a local transparent-background override.
- Options enable truecolor, relative line numbers, two-space indentation, wrapping, mouse support, and clipboard integration.
- Folding uses Tree-sitter-based `foldexpr`, starts fully unfolded (`foldlevelstart = 99`), and exposes quick fold-level/fold-method commands through the Legendary command palette.
- `legendary.nvim` provides the `<leader>p` command palette and `render-markdown.nvim` provides Markdown rendering.
- `lazy-lock.json` is the plugin version snapshot. Do not duplicate its full inventory in prose.

`nvim-tree` is used only by the separate Treemux sidebar process; the main LazyVim editor uses Telescope for file navigation. See [`treemux.md`](treemux.md).

## Key commands

- `<leader>p` opens the Legendary command palette.
- The command palette includes fold controls: `zM`/`zR`/`za`/`zc`/`zo`, `:set foldlevel={0,1,2,3,99}`, and `:set foldmethod={indent,expr,manual}`.
- `<C-s>` saves the current file; `<C-z>` undoes the last change (mapped to `u`) in normal, insert, and visual modes, alongside the default `u`/`<C-r>` undo/redo keys.
- `:RenderMarkdown toggle`, `:RenderMarkdown buf_toggle`, and `:RenderMarkdown preview` control Markdown rendering.
- `:RenderMarkdown log` opens the renderer log for troubleshooting.
