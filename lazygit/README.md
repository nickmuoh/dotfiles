# Lazygit

The `lazygit` binary is installed from the latest [Lazygit GitHub release](https://github.com/jesseduffield/lazygit/releases/latest) into `~/.local/bin` by `scripts/setup-tools.sh`.

The installer supports `x86_64` and `aarch64` Linux hosts and selects the matching release archive automatically. It queries the GitHub Releases API for the current version instead of using the distribution's potentially outdated `apt` package.

The package also stows:

- `~/.config/lazygit/config.yml`
- `~/.config/lazygit/git-commit-msg.prompt.md`

Run `./bootstrap.sh --dry-run` to preview the installation, or `./bootstrap.sh` to install Lazygit and stow its configuration.
