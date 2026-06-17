# Setup Script Plan for nmuoh Shell Setup

## Overview

This is a plan for **creating setup scripts** that provision a fresh WSL/Ubuntu machine to match the documented state in `~/.dotfiles`. The goal is not one giant command file, but a small script set with a master orchestrator and per-tool setup scripts:

1. A root `bootstrap.sh` that calls the other scripts in order
2. Per-tool setup scripts for system packages, shell tools, config symlinks, and plugins
3. Small scripts for special cases such as WSL, tmux plugins, micro plugins, and Neovim bootstrap
4. Clear separation between stowed config, generated assets, and interactive post-install steps

The target environment is WSL2 / Ubuntu with systemd enabled. Non-WSL Linux machines skip the WSL pre-flight step only.

---

## Planned Script Layout

```text
~/.dotfiles/
├─ bootstrap.sh                  # master orchestrator
├─ scripts/
│  ├─ setup-wsl.sh               # /etc/wsl.conf and restart notes
│  ├─ setup-packages.sh          # apt / package-manager installs
│  ├─ setup-shell-tools.sh       # zoxide, fzf, micro, keychain
│  ├─ setup-stow.sh              # stow packages and adopt flow
│  ├─ setup-micro.sh             # micro plugins and pluginrepos
│  ├─ setup-tmux.sh              # TPM, tmux-cpu-mem-monitor, uv sync
│  ├─ setup-treemux.sh           # optional treemux venv and reconciliation
│  ├─ setup-nvim.sh              # lazy.nvim bootstrap
│  └─ setup-postinstall.sh       # gh auth, SSH, shell reload
```

Each script should do one job, be idempotent where practical, and leave the docs in `README.md` / package `README.md` files as the source of truth.

---

## Special Handling vs. Straightforward Installation

### Straightforward (apt, no post-install quirks)

| Tool | Package name |
|------|-------------|
| curl | `curl` |
| git | `git` |
| bash-completion | `bash-completion` |
| ctags | `ctags` |
| bat | `bat` (**but see bat note below**) |
| jq | `jq` |
| yq | `yq` |
| tmux | `tmux` |
| pandoc | `pandoc` |
| starship | `starship` |
| gh (GitHub CLI) | `gh` |
| neovim | `neovim` |
| stow | `stow` |
| uv | `uv` (or install via `curl -LsSf https://astral.sh/uv/install.sh | sh`) |

### Needs Special Handling

| Tool | Reason |
|------|--------|
| **bat** | Installed as `batcat` on Ubuntu/Debian; alias `bat='batcat'` must exist before anything that calls `bat` |
| **fzf** | Must be installed by cloning `~/.fzf` and running `~/.fzf/install` to generate `~/.fzf.bash` shell integration; the apt package alone does not set this up |
| **zoxide** | Installed via upstream curl script; init hook `eval "$(zoxide init bash)"` must be in `~/.bashrc` |
| **micro** | Binary fetched via `curl https://getmic.ro \| bash && sudo mv micro /usr/bin`; not in apt |
| **micro plugins** | Three plugins require custom `pluginrepos` entries in `settings.json`; all seven plugins then need explicit install or `git clone` commands; must run **after** the micro config is in place |
| **keychain** | Installed as a single shell script via curl into `~/.local/bin`; bash completion installed separately; not in apt |
| **tmux TPM + plugins** | TPM must be cloned first; plugins activate only after launching tmux and pressing `<prefix> I` (or running `~/.tmux/plugins/tpm/bin/install_plugins`) |
| **tmux-cpu-mem-monitor** | After TPM activation, `uv sync` must be run in `~/.tmux/plugins/tmux-cpu-mem-monitor` to install `psutil` |
| **Neovim (LazyVim)** | `lazy.nvim` bootstraps itself on first `nvim` launch; no manual plugin installs needed, but first launch must complete before the editor is usable |
| **Treemux** | Needs a Python interpreter at `~/.local/share/treemux-venv/bin/python`; the venv must be created manually; note `nvim-tree` is currently the configured client but is not loaded — reconcile before using Treemux |
| **WSL `/etc/wsl.conf`** | Requires `sudo` and a `wsl --shutdown` from Windows after writing; cannot be applied from inside the distro without a restart |
| **SSH key** | `~/.ssh/nick_muoh.trimble-github.ed25519` must exist before keychain initialization works; provision separately |
| **gh auth** | `gh auth login` is interactive and must be run manually after install |

---

## Planned Script Responsibilities

### `scripts/setup-wsl.sh` — WSL Pre-flight (WSL targets only)

```bash
# Run from Windows PowerShell BEFORE entering the distro, or from a root shell
sudo tee /etc/wsl.conf > /dev/null << 'EOF'
[boot]
systemd=true

[user]
default=nmuoh

[automount]
options = "metadata"
EOF
# Then from Windows: wsl --shutdown
# Restart distro before continuing
```

### `scripts/setup-packages.sh` — System Packages

```bash
sudo apt-get update
sudo apt-get install -y \
  git ctags fzf bat jq yq tmux pandoc \
  starship gh neovim stow uv
```

> `uv` may not be in apt; if the above fails for `uv`, install it separately:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

### `scripts/setup-shell-tools.sh` — Shell Tool Installs (non-apt)

```bash
# zoxide
curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh

# fzf (clone + shell integration)
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
~/.fzf/install --all --no-update-rc   # writes ~/.fzf.bash; --no-update-rc leaves .bashrc edits to stow

# micro
curl https://getmic.ro | bash
sudo mv micro /usr/bin/micro

# keychain binary + bash completion
mkdir -p ~/.local/bin ~/.local/share/bash-completion/completions
curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/keychain.sh \
  -o ~/.local/bin/keychain
chmod +x ~/.local/bin/keychain
curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/completions/keychain.bash \
  -o ~/.local/share/bash-completion/completions/keychain
```

> **Note:** `fzf/install --no-update-rc` skips modifying `.bashrc` automatically. The Stow-managed `.bashrc` already contains the `[ -f ~/.fzf.bash ] && source ~/.fzf.bash` line, so no double-write occurs.

### `scripts/setup-stow.sh` — Stow Config Symlinks

```bash
cd ~/.dotfiles   # or wherever the dotfiles repo lives

# Core configs
stow -v bash          # ~/.bashrc, ~/.bash_aliases
stow -v micro         # ~/.config/micro/{settings.json,bindings.json,palettero.cfg,colorschemes/}
stow -v tmux          # ~/.tmux.conf
stow -v nvim          # ~/.config/nvim/
stow -v starship      # ~/.config/starship.toml
stow -v local-bin     # ~/.local/bin/keychain  (if managed via stow instead of curl)
stow -v bash-completions  # ~/.local/share/bash-completion/completions/keychain
```

> `micro/plug/` must be in `micro/.stow-local-ignore` so plugin clones are not stowed.

### `scripts/setup-micro.sh` — Micro Plugin Install

> Run **after** `scripts/setup-stow.sh` so `settings.json` (with `pluginrepos`) is in place.

```bash
# Plugins from custom repos (registered in settings.json pluginrepos)
micro -plugin install gitStatus
micro -plugin install preview
micro -plugin install fzfinder

# Plugins installed by direct git clone
git clone https://github.com/terokarvinen/palettero    ~/.config/micro/plug/palettero
git clone https://github.com/terokarvinen/micro-jump   ~/.config/micro/plug/jump
git clone https://github.com/dalekirkwood/Micro_Editor_Iconic_Tabs ~/.config/micro/plug/iconic_tabs
git clone https://github.com/adamnpeace/micro-wc-plugin ~/.config/micro/plug/wc
```

Plugin runtime dependencies must be present:
- `git` → gitStatus
- `fzf` + `batcat` → fzfinder (preview in file picker)
- `pandoc` → preview
- `fzf`, `ctags`, `git` → jump
- `fzf`, `bash` → palettero
- Nerd Font terminal → iconic\_tabs

### `scripts/setup-tmux.sh` — tmux Plugin Install

```bash
# Install TPM if not present
git clone --depth 1 https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# Install remaining plugins non-interactively
~/.tmux/plugins/tpm/bin/install_plugins
# OR: start a tmux session and press <prefix> I

# uv sync for cpu/mem monitor
cd ~/.tmux/plugins/tmux-cpu-mem-monitor
uv sync
```

> If tmux is already running, reload config with `tmux source-file ~/.tmux.conf` — never kill the server from inside a session.
>
> The local `tmux-cpu-mem-monitor` checkout is customized: `tmux_cpu_mem_monitor.tmux` runs `uv sync` and rewrites `cpu`, `mem`, `disk`, and `battery` placeholders. Preserve that wrapper if you reinstall or refresh the plugin, or split it into its own tracked setup step if you decide to vendor the plugin.

### `scripts/setup-nvim.sh` — Neovim Plugin Bootstrap

```bash
# First launch triggers lazy.nvim self-bootstrap and plugin sync
nvim --headless "+Lazy! sync" +qa
```

LazyVim fetches all plugins declared in `~/.config/nvim/lua/plugins/` and locks versions in `lazy-lock.json`. No manual Mason/LSP installs are scripted here; run `:MasonInstall <lsp>` interactively as needed.

### `scripts/setup-treemux.sh` — Treemux Python Venv (optional, if using Treemux)

```bash
uv venv ~/.local/share/treemux-venv
uv pip install --python ~/.local/share/treemux-venv/bin/python neovim
```

> **Caveat:** `nvim-tree` is currently not loaded in the active Neovim config. Treemux with `@treemux-tree-client 'nvim-tree'` will not work until `nvim-tree.lua` is re-enabled or the Treemux client config is updated.

### `scripts/setup-postinstall.sh` — Interactive Post-install Steps

These cannot be scripted:

```bash
gh auth login                            # GitHub CLI authentication
ssh-add ~/.ssh/nick_muoh.trimble-github.ed25519  # Add SSH key (keychain will cache after first eval)
```

### `scripts/setup-postinstall.sh` — Reload Shell

```bash
source ~/.bashrc
```

Verify the following are active:
- `starship` prompt rendering (Nerd Font glyphs visible)
- `z <dir>` works (zoxide)
- `bat <file>` works via alias
- `keychain` initialized (no passphrase prompt on second shell open)
- `micro` launches with plugins and Nord colorscheme

---

## Per-Tool Notes

### bat

- Ubuntu/Debian installs the binary as `batcat`, not `bat`.
- The alias `bat='batcat'` and `bathelp='bat --plain --language=help'` live in `~/.bash_aliases` (stowed).
- The `help()` shell function pipes `--help` output through `bathelp`.
- Micro's `fzfinder` preview calls `batcat` directly (`fzfarg = "--preview 'batcat -f -p {}'"`), so `batcat` must be on `PATH` even without the alias.

### keychain

- Binary is a single shell script at `~/.local/bin/keychain` (not from apt).
- Bash completion file at `~/.local/share/bash-completion/completions/keychain`.
- `~/.local/bin` must be on `PATH` before `keychain` runs — the Stow-managed `.bashrc` already ensures this.
- Init line in `.bashrc`: `eval "$(keychain --quiet --eval nick_muoh.trimble-github.ed25519)"`
- The SSH key `~/.ssh/nick_muoh.trimble-github.ed25519` must already exist; keychain does not generate keys.

### micro plugins and pluginrepos

- `settings.json` must be symlinked (via stow) before running `micro -plugin install` so the custom `pluginrepos` URLs are present.
- Three custom repos to register:
  - `https://raw.githubusercontent.com/weebi/micro-preview/master/repo.json`
  - `https://raw.githubusercontent.com/Neko-Box-Coder/git-status/refs/heads/main/repo.json`
  - `https://raw.githubusercontent.com/MuratovAS/micro-fzfinder/main/repo.json`
- Four plugins use git clone directly (palettero, jump, iconic\_tabs, wc) — micro's plugin manager does not handle these.
- `palettero.cfg` (stowed) stores custom command palette entries; it is read by micro at runtime, not at install time.
- Nord colorschemes (`nord-16`, `nord-16-light`, `nord-tc`, `nord-tc-light`) live in `~/.config/micro/colorschemes/` and are stowed with the micro package.

### tmux plugin activation and uv sync

- TPM must be in `~/.tmux/plugins/tpm` before tmux loads the config; clone it before first tmux start.
- `~/.tmux/plugins/tpm/bin/install_plugins` can run headlessly for scripted setup.
- The local checkout includes a `tmux_cpu_mem_monitor.tmux` wrapper that updates `status-left` and `status-right` and maps `cpu`, `mem`, `disk`, and `battery` placeholders to the Python scripts in `src/`.
- `tmux-cpu-mem-monitor` calls Python scripts via `uv run --project ~/.tmux/plugins/tmux-cpu-mem-monitor`; `uv sync` in that directory creates the venv and installs `psutil==6.0.0`.
- The `@cpu_mem_plugin_dir` user option in `.tmux.conf` is hard-coded to `/home/nmuoh/.tmux/plugins/tmux-cpu-mem-monitor` — update if the username differs.
- Reload config from inside tmux: `tmux source-file ~/.tmux.conf` (never `tmux kill-server` from inside a session).

### Neovim plugin bootstrap

- `init.lua` → `config.lazy` → lazy.nvim self-bootstrap on first run.
- `lazy-lock.json` pins plugin commit hashes; preserve it for reproducible installs.
- The Nord colorscheme uses `arcticicestudio/nord-vim` with a custom transparency autocmd in `lua/plugins/nord.lua`.
- `neo-tree` and `nvim-tree` entries in `lazy-lock.json` are stale; neither is currently active.
- Treemux's `@treemux-tree-client 'nvim-tree'` in `.tmux.conf` is a known mismatch — needs reconciliation before Treemux file-tree integration works.

### WSL target handling

- `/etc/wsl.conf` requires `sudo` write access and a `wsl --shutdown` from Windows to apply.
- This file is **not managed by Stow** — apply it manually or via a bootstrap script that requires `sudo`.
- `systemd=true` requires Windows 11+ with WSL build that supports systemd; verify with `systemctl --version` after restart.
- Windows drive mounts appear under `/mnt/c/`, etc.; `automount options = "metadata"` preserves POSIX permission metadata on those mounts.

### zoxide init

- No config file; behavior comes entirely from `eval "$(zoxide init bash)"` in `.bashrc`.
- Init line is in the Stow-managed `.bashrc`; active immediately after `source ~/.bashrc`.

### starship init

- Init line in `.bashrc`: `eval "$(starship init bash)"`.
- Config at `~/.config/starship.toml` (stowed).
- Uses Nerd Font glyphs extensively; terminal must support Nerd Fonts or glyphs will render as boxes/question marks.
- `command_timeout = 1500` set in `starship.toml` to avoid slow-prompt warnings.

---

## What Must Stay Out of Stow

The following items must be handled by the bootstrap script or manual steps — **do not stow these**:

| Item | Reason |
|------|--------|
| `/etc/wsl.conf` | System-level, requires `sudo`; not under `$HOME` |
| `~/.tmux/plugins/` | Third-party plugin clones; large, versioned separately by TPM |
| `~/.config/micro/plug/` | Plugin source clones; excluded via `micro/.stow-local-ignore` |
| `~/.fzf/` | Install-time generated repo; `~/.fzf.bash` is generated by `~/.fzf/install` |
| `~/.local/share/nvim/` | lazy.nvim managed plugin store; not config, not stowed |
| `~/.local/share/treemux-venv/` | Runtime Python venv; not config |
| `~/.local/bin/keychain` | Binary fetched via curl; stow it only if the dotfiles repo includes the script file |
| `~/.ssh/` | SSH keys and agent config; secret material, never in a dotfiles repo |
| `gh` auth state (`~/.config/gh/`) | Authentication tokens; interactive only |
| `lazy-lock.json` | May be stowed or committed but should not be auto-overwritten by bootstrap |

---

## Script Checklist

```
[x] `scripts/setup-wsl.sh` written and documented (WSL only)
[x] `scripts/setup-packages.sh` written for apt/base package installs
[x] `scripts/setup-shell-tools.sh` written for zoxide, fzf, micro, keychain
[x] `scripts/setup-stow.sh` written for config symlinks and adopt flow
[x] `scripts/setup-micro.sh` written for micro plugins and pluginrepos
[x] `scripts/setup-tmux.sh` written for TPM + tmux-cpu-mem-monitor + uv sync
[x] `scripts/setup-treemux.sh` written for the optional Treemux venv
[x] `scripts/setup-nvim.sh` written for lazy.nvim bootstrap
[x] `scripts/setup-postinstall.sh` written for gh auth, SSH, and shell reload
[x] Root `bootstrap.sh` documented as the orchestrator that calls the above
```
