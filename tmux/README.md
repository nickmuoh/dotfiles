# tmux setup

## Important configuration paths

- `~/.tmux.conf`
- `~/.tmux/plugins/tpm`
- `~/.tmux/plugins/nord-tmux`
- `~/.tmux/plugins/tmux-menus`
- `~/.tmux/plugins/treemux`
- `~/.tmux/plugins/tmux-autoreload`
- `~/.tmux/plugins/tmux-prefix-highlight`
- `~/.tmux/plugins/tmux-mighty-scroll`
- `~/.tmux/plugins/tmux-cpu-mem-monitor`
- `/home/nmuoh/.tmux/plugins/treemux/configs/treemux_init.lua`

## Installed plugins

- `tmux-plugins/tpm`
- `arcticicestudio/nord-tmux`
- `jaclu/tmux-menus` - <https://github.com/jaclu/tmux-menus>
- `kiyoon/treemux` - <https://github.com/kiyoon/treemux>
- `b0o/tmux-autoreload`
- `tmux-plugins/tmux-prefix-highlight`
- `noscript/tmux-mighty-scroll`
- `tmux-cpu-mem-monitor` (vendored fork, stowed from this repo)

## Current state

- tmux uses `default-terminal "tmux-256color"`.
- `terminal-features` enables RGB/truecolor for `tmux-256color` and `xterm-256color`.
- `update-environment` copies `DBUS_SESSION_BUS_ADDRESS`, `GNOME_KEYRING_CONTROL`, and `XDG_RUNTIME_DIR` from the attaching client so Copilot and other Secret Service clients can see the user keyring inside tmux.
- Mouse mode is enabled.
- The prefix key is `Ctrl-A`.
- Window and pane numbering both start at `1`.
- Windows are renumbered automatically.
- The status bar is positioned at the top.
- The right side of the status line uses `#{prefix_highlight}` for prefix state (`^A`) and shows CPU and memory usage with plugin icons (`` CPU, `` MEM), with date/time/host removed.
- `tmux-menus` is installed through TPM and opens popup menus with `<prefix> \` by default.
- Treemux is the tmux-side plugin layer that connects tmux with a Neovim tree client; in this setup it is configured to use `nvim-tree` and a Python interpreter at `/home/nmuoh/.local/share/treemux-venv/bin/python` created by `uv`.
- `tmux-cpu-mem-monitor` is vendored in `tmux-cpu-mem-monitor/` and stowed to `~/.tmux/plugins/tmux-cpu-mem-monitor`.
- Its `tmux_cpu_mem_monitor.tmux` wrapper is the source of truth for the CPU/MEM right status segment: it builds `status-right` and rewrites the `cpu`, `mem`, `disk`, and `battery` placeholders to `uv run --project ... src/*.py` commands.
- The tmux config keeps theme knobs for that segment (`@cpu_mem_*` and `@prefix_highlight_*`), invokes the vendored wrapper after TPM, then invokes `tmux-prefix-highlight` separately as the final rewrite step.
- TPM is initialized before the wrapper so Nord can finish its setup first, then the CPU/MEM wrapper restores the custom status line, and `tmux-prefix-highlight` patches the final string.

## Treemux shortcuts

Treemux is the tmux-side tree sidebar. It runs in a separate Neovim process and is
configured from `~/.tmux.conf`, not from the main LazyVim config.

- `prefix + Tab` — toggle the tree sidebar
- `prefix + Backspace` — toggle the tree sidebar and focus it
- `R` — refresh the tree
- `Enter` / `l` / `Ctrl-t` / double-click — open in treemux
- `v` / `Ctrl-v` — vertical split in treemux
- `Ctrl-x` — horizontal split in treemux
- `o` — open in the main pane without a tmux split
- `h` — close/collapse the current node
- `u` — change root upward
- `F1` — show node info
- `Space o` — toggle between `nvim-tree` and `oil.nvim`

Treemux is currently configured to use `nvim-tree`. The sidebar config enables
filesystem watchers and reload-on-bufenter, so external file/dir changes are
picked up automatically in addition to `R`. `scripts/setup-treemux.sh` installs
that config from `scripts/treemux_init.lua` on every bootstrap run.

Related paths:

- `~/.tmux.conf`
- `~/.tmux/plugins/treemux/configs/treemux_init.lua`
- `G:\My Drive\NMUOH-US-LE\.tmux\treemux-shortcuts.md`

## `tmux-cpu-mem-monitor` custom installation decisions

1. Keep the fork in the `tmux-cpu-mem-monitor` Stow package so it stays versioned with this repo.
2. Preserve the local `tmux_cpu_mem_monitor.tmux` wrapper if you reinstall or refresh the package; it owns the custom CPU/MEM `status-right` and the `disk`/`battery` placeholder handling.
3. Use `uv` for dependency execution instead of relying on system `venv`/`pip`, based on issue #11 behavior and local Python environment constraints.
4. Keep date/time/hostname removed from `status-right` and replace with CPU/MEM only.
5. Keep Nord look-and-feel by reusing Nord separators and color blocks in `status-right`.
6. Use plugin icons in the segment (`` for CPU, `` for MEM).
7. Keep the tmux config DRY by storing only theme knobs in user options, letting the vendored wrapper assemble `status-right`, and running `tmux-prefix-highlight` separately as the last rewrite.
8. Reload tmux safely with `tmux source-file ~/.tmux.conf` (do not kill tmux server from inside a running tmux session).

## History-backed setup notes

- `tmux`
- `tmux ls`
- `tmux attach -t 0`
- `tmux -n wsl`
- `tmux new wsl`
- `tmux source-file ~/.tmux.conf`
- If tmux was already running before the keyring session started, detach and reattach from a shell that already has the keyring env, or restart the tmux server so the updated environment is picked up.

No explicit TPM install command was found in `~/.bash_history`, but the plugin directories exist under `~/.tmux/plugins`.

## Caveats

- Older tmux panes that were opened before the `tmux-256color` change may still carry the old `TERM` value. New panes/sessions inherit the corrected terminal setting.
- `tmux-menus` requires tmux 3.0+ for native popup menus; this system is on tmux 3.6, so no fallback packages are needed.
- Treemux depends on `nvim-tree` integration and the configured Python environment path remaining valid.
- `tmux-mighty-scroll` is configured for pass-through fallback mode, so behavior depends on the terminal and application running in the pane.
