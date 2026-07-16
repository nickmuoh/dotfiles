# Bash shell state

## Important configuration paths

- `~/.bashrc`
- `~/.bash_aliases`
- `~/.config/starship.toml`
- `~/.fzf.bash`
- `~/.fnm/` — managed by the `fnm` stow package
- `~/.1password/agent-bridge.sh`
- `~/.local/bin/keychain`
- `~/.local/share/fnm/`
- `~/.local/bin/gh-browser`
- `BROWSER` is exported from `~/.bashrc` when `gh-browser` is available

## Aliases from `~/.bash_aliases`

- `alias bat='batcat'`
- `alias bathelp='bat --plain --language=help'`
- `help()` shell function:
  - runs the given command with `--help`
  - captures stderr/stdout
  - pipes the result through `bathelp`

## Current state

- Git core.editor is set to `nvim` (global git config). To ensure other tools use Neovim, consider exporting `EDITOR` and `VISUAL` in your shell rc: `export EDITOR=nvim` and `export VISUAL=nvim`.

- `~/.bashrc` is still mostly the default Debian/Ubuntu shell startup file.
- Bash completion is enabled when the system completion files exist.
- `MICRO_TRUECOLOR=1` is exported, which helps micro render truecolor themes.
- `~/.local/bin` is prepended to `PATH` from `~/.bashrc` before the `keychain` startup block runs.
- `~/.bashrc` adds `~/.fnm` to `PATH` before initializing fnm.
- `starship`, `fzf`, `zoxide`, and `fnm` are initialized from `~/.bashrc` when their startup files or commands are available.
- `gh` is installed and on `PATH`; `gh-browser` handles auth login browser launches, but there is no `gh` alias or completion hook in the Bash config.
- `gh auth login` uses `gh-browser` through the `BROWSER` environment variable.
- `~/.bash_aliases` is sourced from `~/.bashrc` when the file exists.
- SSH auth for `nick_muoh.trimble-github.ed25519` is initialized separately by `keychain` instead of starting a fresh `ssh-agent` per shell.
- The 1Password WSL bridge is a separate flow and does not depend on `keychain`.
- Keychain stays in `~/.bashrc` here on purpose so tmux panes and nested interactive shells inherit the agent setup; if you prefer strict login-shell behavior, put the eval in `~/.bash_profile` and source `~/.bashrc` from there.

## Tools initialized from Bash

- Starship: `command -v starship >/dev/null 2>&1` then `eval "$(starship init bash)"`
- fzf: `[ -f ~/.fzf.bash ] && source ~/.fzf.bash`
- zoxide: `command -v zoxide >/dev/null 2>&1` then `eval "$(zoxide init bash)"`
- fnm: add `FNM_PATH` to `PATH` when it exists, then `eval "$(fnm env --use-on-cd --shell bash)"`
- keychain: `eval "$(keychain add --quiet --eval "$HOME/.ssh/nick_muoh.trimble-github.ed25519")"`
- gh-browser: a small helper that prefers `wslview`, then `xdg-open`, then `explorer.exe`, then `cmd.exe /c start`
- `1Password SSH agent bridge`: sources `~/.1password/agent-bridge.sh`, exports `SSH_AUTH_SOCK=$HOME/.1password/agent.sock`, and starts `socat` plus `npiperelay.exe` when needed; this requires 1Password for Windows with Developer > `Use the SSH agent` enabled
- `bat` behavior is documented separately in `bat.md`

## History-backed setup notes

- `sudo apt install starship`
- `curl https://getmic.ro | bash && sudo mv micro /usr/bin`
- `git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf`
- `~/.fzf/install`
- `curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh`
- `curl -fsSL https://gh.io/copilot-install | bash`
- `curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell --install-dir "$HOME/.fnm"`
- `curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/keychain.sh -o ~/.local/bin/keychain`
- `curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/completions/keychain.bash -o ~/.local/share/bash-completion/completions/keychain`
- `npiperelay.exe` is installed by `scripts/setup-tools.sh` from the `jstarks/npiperelay` release zip
- multiple `source ~/.bashrc` runs after edits

## Caveats

- The shell config is a mix of distro defaults and personal additions; most customization lives at the bottom of `~/.bashrc`.
- There is no separate tracked config for zoxide; when `zoxide` is on `PATH`, its behavior comes from the default `zoxide init bash` output.
- `gh` currently behaves like a standard installed CLI binary rather than a tool with extra Bash integration.
- `starship`, `fzf`, `zoxide`, `fnm`, `keychain`, and the 1Password bridge are only initialized for interactive Bash shells.
