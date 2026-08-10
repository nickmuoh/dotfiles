# Neovim setup

## Important configuration paths

- `~/.config/nvim/init.lua`
- `~/.config/nvim/lua/config/lazy.lua`
- `~/.config/nvim/lua/config/options.lua`
- `~/.config/nvim/lua/plugins/nord.lua`
- `~/.config/nvim/lua/plugins/legendary.lua`
- `~/.config/nvim/lua/plugins/render-markdown.lua`
- `~/.config/nvim/lazy-lock.json`
- `~/.config/nvim/lazyvim.json`
- `~/.local/share/nvim/lazy/`
- `~/.vimrc` (separate Vim config, not used by Neovim)

## Binary install

The `nvim` binary is NOT installed via apt. `setup-binaries.sh` downloads the official
GitHub release tarball and extracts it to `~/.local/opt/nvim-linux-x86_64/` with a
symlink at `~/.local/bin/nvim`.

## Bootstrap

After the `nvim` package is stowed, `scripts/setup-nvim.sh` runs
`nvim --headless "+Lazy! sync" +qa`. This installs or updates `lazy.nvim` plugins
from `lazy-lock.json`, including render-markdown.nvim and its declared
Tree-sitter/icon dependencies. Run the complete bootstrap with:

```sh
./bootstrap.sh
```

Use `./bootstrap.sh --dry-run` to preview the commands without changing the
system. The plugin snapshot is committed in `lazy-lock.json`; rerun the headless
Lazy sync after intentionally changing plugin specifications.

## Current state

- Neovim is using the LazyVim starter-style layout:
  - `init.lua` delegates to `require("config.lazy")`
  - `lazy.lua` bootstraps `lazy.nvim` and imports `LazyVim/LazyVim` plus local `plugins`
- Editor options set in `options.lua`:
  - `termguicolors = true`
  - line numbers + relative numbers
  - 2-space indentation
  - `smartindent`
  - `wrap = true`
  - `mouse = "a"`
  - `clipboard = "unnamedplus"`
  - `autoread = true`
  - buffers reload on external file changes via `checktime` autocmds on focus/enter/idle events
- Theme selection:
  - `LazyVim` colorscheme option is set to `nord`
  - the theme plugin is `arcticicestudio/nord-vim`
  - a custom `ColorScheme` autocmd clears background on several highlight groups so Neovim inherits the terminal background
- `lazyvim.json` shows LazyVim metadata version `8`

## Installed plugins observed at runtime

- `LazyVim`
- `arcticicestudio/nord-vim`
- `lazy.nvim`
- `blink.cmp`
- `bufferline.nvim`
- `catppuccin`
- `conform.nvim`
- `flash.nvim`
- `friendly-snippets`
- `gitsigns.nvim`
- `grug-far.nvim`
- `lazydev.nvim`
- `lualine.nvim`
- `mason.nvim`
- `mason-lspconfig.nvim`
- `mini.ai`
- `mini.icons`
- `mini.pairs`
- `noice.nvim`
- `nui.nvim`
- `nvim-lint`
- `nvim-lspconfig`
- `nvim-treesitter`
- `nvim-treesitter-textobjects`
- `nvim-ts-autotag`
- `persistence.nvim`
- `plenary.nvim`
- `nvim-telescope/telescope.nvim`
- `stevearc/dressing.nvim` — routes `vim.ui.select` to Telescope
- `mrjones2014/legendary.nvim` — Sublime-style command palette (`<leader>p`); frecency-sorted via `kkharji/sqlite.lua`
- `kkharji/sqlite.lua` — SQLite FFI binding (requires `libsqlite3-dev` on Debian/Ubuntu)
- `MeanderingProgrammer/render-markdown.nvim` — renders Markdown headings, code blocks, lists, checkboxes, tables, links, callouts, and quotes in place; lazy-loads for `markdown` buffers
- `nvim-treesitter/nvim-treesitter` — parses Markdown for render-markdown.nvim
- `nvim-mini/mini.icons` — supplies icons for rendered code blocks
- `snacks.nvim`
- `todo-comments.nvim`
- `tokyonight.nvim`
- `trouble.nvim`
- `ts-comments.nvim`
- `which-key.nvim`

## Markdown rendering

`MeanderingProgrammer/render-markdown.nvim` is configured in
`lua/plugins/render-markdown.lua`. It loads when a `markdown` buffer is opened,
uses the existing `nvim-treesitter` and `mini.icons` plugins as dependencies.
Rendering is explicitly enabled and automatically shown in normal, command-line,
and terminal modes when a Markdown buffer is opened.
The plugin requires Neovim 0.9 or newer; this setup uses Neovim 0.12 and already
includes the required Markdown Tree-sitter parsers through the LazyVim
configuration.

Useful commands:

- `<leader>p`, then `Render the current Markdown buffer` — enable rendering from the Legendary command palette
- `<leader>p`, then `Use the raw current Markdown buffer` — disable rendering from the Legendary command palette
- `:RenderMarkdown toggle` — toggle rendering globally
- `:RenderMarkdown buf_toggle` — toggle rendering for the current buffer
- `:RenderMarkdown preview` — show a rendered preview beside the current buffer
- `:RenderMarkdown log` — open the plugin log when troubleshooting

The upstream project documentation and configuration reference are available at
`https://github.com/meanderingprogrammer/render-markdown.nvim`.

## Lockfile note

- `~/.config/nvim/lazy-lock.json` is the plugin version snapshot.
- The current Nord entry is:
  - `nord-vim` -> `f13f5dfbb784deddbc1d8195f34dfd9ec73e2295`

## History-backed setup notes

- Note: Git's global editor is configured to `nvim` for this user (`git config --global core.editor 'nvim'`).

The Bash history only shows repeated `nvim` launches, not the full build-out of the Neovim config. The current structured setup is most reliably reconstructed from the files above.

Recent state that matters:

- Neovim was converted to LazyVim-style bootstrapping
- the Nord theme was switched to `arcticicestudio/nord-vim`
- transparency was added via a custom colorscheme autocmd
- tmux terminal settings were updated so Nord renders correctly inside tmux
- `nvim-telescope/telescope.nvim` installed (2026-06-02) via `lazy.nvim`; created `~/.config/nvim/lua/plugins/telescope.lua` and ran `require('lazy').sync()` to fetch the plugin
- `MeanderingProgrammer/render-markdown.nvim` installed via `lazy.nvim`; created `~/.config/nvim/lua/plugins/render-markdown.lua` and ran `nvim --headless "+Lazy! sync" +qa` to fetch it and update `lazy-lock.json`

## Keymaps

- `<leader>p` (n/i/v) — open legendary.nvim command palette (`:Legendary`)
- `<C-s>` (n/i/v) — save file (`:w`)

## Caveats

- Neovim now depends on tmux advertising a modern terminal type if it is run inside tmux; older tmux panes may still show weaker colors until restarted.
- The transparent background is not a stock Nord behavior here; it is enforced by a local highlight override in `lua/plugins/nord.lua`.
- `~/.vimrc` is configured separately for Vim and should not be confused with the Neovim/LazyVim setup.
- `lazy-lock.json` should be preserved if you want reproducible plugin versions.
- Markdown rendering uses Nerd Font symbols when available; install a Nerd Font if rendered icons appear as missing glyphs.
- `lazy-lock.json` still contains historical entries for `neo-tree.nvim`, `nvim-tree.lua`, and `nvim-tree-remote.nvim`, but the current active LazyVim runtime does not load either `neo-tree.nvim` or `nvim-tree.lua`.
