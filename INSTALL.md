# Shell setup install guide

Install GNU Stow first, then bootstrap the generated content, then stow the packages.

## Tools

All packages and GitHub release binaries are declared in `scripts/setup-tools.sh`:

- **`APT_PACKAGES`** array — names installed via apt. Edit this to add/remove distro packages.
- **`GITHUB_INSTALLS`** array — pipe-delimited entries for GitHub release artifacts.
  Format: `"cmd|method|url"` or `"cmd|method|url|extra"`.
  Methods: `deb` (dpkg), `tarball` (extract to `~/.local/opt/`), `bin` (single binary to `~/.local/bin/`).
- **`SNAP_PACKAGES`** array — names installed via `sudo snap install`. Edit this to add/remove snap packages.
- **`INSTALLER_TOOLS`** array — pipe-delimited entries for tools with their own installer scripts (zoxide, uv, micro). Format: `"cmd|url"` or `"cmd|url|dest"`.
- **fzf** — installed via git clone + bundled install script (handled at the end of `setup-tools.sh`).

`scripts/setup-shell-tools.sh` is temporarily retained for keychain only, pending future refactor into `setup-tools.sh`.

Run `./bootstrap.sh --dry-run` to preview what will be installed.

## Shell tools (keychain)

```sh
mkdir -p ~/.local/bin ~/.local/share/bash-completion/completions
curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/keychain.sh -o ~/.local/bin/keychain
curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/completions/keychain.bash -o ~/.local/share/bash-completion/completions/keychain
```

## Bootstrap

Run the repo bootstrap script to install generated/plugin content:

```sh
cd /home/nmuoh/.dotfiles
./bootstrap.sh --dry-run
./bootstrap.sh
```

That bootstrap step clones `~/.fzf`, `~/.tmux/plugins/tpm`, and the Micro plugin repos.
If target config files already exist in `$HOME`, use `./bootstrap.sh --adopt` for the first stow pass.

### Treemux (optional)

To set up the Treemux file-tree sidebar for tmux, pass `ENABLE_TREEMUX=1`:

```sh
ENABLE_TREEMUX=1 ./bootstrap.sh
```

This creates the Python venv at `~/.local/share/treemux-venv/` that the Treemux
tmux plugin uses to launch the Neovim tree client.

## Stow

Dry run first:

```sh
stow -nv bash micro tmux nvim starship fzf local-bin bash-completions lazygit git
```

Then deploy:

```sh
stow -v bash micro tmux nvim starship fzf local-bin bash-completions lazygit git
```

## Git stow package

The `git` stow package manages `~/.gitconfig`. Before stowing, create `~/.gitconfig.local`
with your `[user]` name and email — this file is not tracked in the repo:

```gitconfig
[user]
    name = Your Name
    email = you@example.com
```

The tracked gitconfig uses `[include]` to pull in `~/.gitconfig.local`.

## Notes

- `bat` is invoked as `batcat` on this system.
- `preview` uses the `preview` command in Micro and depends on `pandoc`.
- Package-specific details live in `<package>/README.md`.
