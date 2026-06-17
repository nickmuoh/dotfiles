# Shell setup notes

This repo tracks the shell/editor setup under `/home/nmuoh/.dotfiles` and is organized for Stow.

## Package docs

- [bash](bash/README.md)
- [tmux](tmux/README.md)
- [micro](micro/README.md)
- [nvim](nvim/README.md)
- [starship](starship/README.md)
- [fzf](fzf/README.md)
- [local-bin](local-bin/README.md)
- [bash-completions](bash-completions/README.md)

## Root docs

- `INSTALL.md`
- `AGENTS.md`
- `plan.md`
- `bootstrap-plan.md`
- `bat.md`
- `gh.md`
- `jq.md`
- `keychain.md`
- `neotree.md`
- `wsl.md`
- `yq.md`
- `zoxide.md`

## Layout

- Root docs stay at the repo root and are never stowed
- Package docs live beside their package config in `<package>/README.md`
- Generated/plugin content belongs in `bootstrap.sh`, not in Stow packages

## Bootstrap

- `bootstrap.sh` orchestrates `scripts/`
- `./bootstrap.sh --dry-run` prints the full command plan without changing anything
