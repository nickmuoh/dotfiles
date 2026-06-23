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
- [git](git/README.md)
- [copilot](copilot/README.md)
- [snowflake](snowflake/README.md)

## Root docs

- `AGENTS.md`
- [`docs/`](docs/) — per-tool reference docs

## Layout

- Root docs stay at the repo root and are never stowed
- Package docs live beside their package config in `<package>/README.md`
- Generated/plugin content belongs in `bootstrap.sh`, not in Stow packages

## Bootstrap and stow

Run bootstrap first to clone plugins and generated content, then stow the packages:

```sh
./bootstrap.sh --dry-run   # preview
./bootstrap.sh             # apply
```

If config files already exist in `$HOME`, use `--adopt` on the first stow pass:

```sh
stow -nv bash micro tmux nvim starship fzf local-bin bash-completions lazygit git copilot snowflake
stow -v  bash micro tmux nvim starship fzf local-bin bash-completions lazygit git copilot snowflake
```

To set up the Treemux sidebar (optional):

```sh
ENABLE_TREEMUX=1 ./bootstrap.sh
```
