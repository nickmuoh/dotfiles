# Neo-tree / file-tree state

## Important configuration paths

- `~/.config/nvim/lazy-lock.json`
- `~/.config/nvim/`
- `~/.tmux.conf`

## Current state

- `neo-tree.nvim` is **not active** in the current Neovim runtime.
- `nvim-tree.lua` is also **not active** in the current Neovim runtime.
- A runtime check against the current LazyVim config showed:
  - `neo-tree=false`
  - `nvim-tree=false`

## Historical traces

- `~/.config/nvim/lazy-lock.json` still contains entries for:
  - `neo-tree.nvim`
  - `nvim-tree.lua`
  - `nvim-tree-remote.nvim`
- `~/.tmux.conf` configures Treemux with:
  - `@treemux-tree-client 'nvim-tree'`
- Treemux reference:
  - <https://github.com/kiyoon/treemux>
  - Treemux is the tmux plugin/library in this setup that expects to talk to a Neovim tree client such as `nvim-tree`

## What this likely means

- You previously had a Neovim setup that used file-tree plugins such as Neo-tree and/or nvim-tree.
- Your current Neovim config was later changed to a different active plugin set, but the lockfile still carries some older plugin entries.
- tmux/Treemux still assumes `nvim-tree`, which may no longer match the current Neovim setup.

## Caveats

- Do not treat the presence of `neo-tree.nvim` in `lazy-lock.json` as proof that Neo-tree is currently configured or usable.
- If you want file-tree behavior restored or documented as an active part of the setup, the Neovim config and the Treemux integration should be reconciled.
