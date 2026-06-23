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
- [lazygit](lazygit/README.md)
- [copilot](copilot/README.md)
- [snowflake](snowflake/README.md)

## Root docs

- `AGENTS.md`
- [`docs/`](docs/) — per-tool reference docs

## Layout

- Root docs stay at the repo root and are never stowed
- Package docs live beside their package config in `<package>/README.md`
- Generated/plugin content belongs in `bootstrap.sh`, not in Stow packages

## First run

Show bootstrap options and optional environment toggles with:

```sh
./bootstrap.sh --help
```

Preview the bootstrap actions first:

```sh
./bootstrap.sh --dry-run
```

Apply the bootstrap after the dry-run output looks correct:

```sh
./bootstrap.sh
```

If matching config files already exist in `$HOME`, adopt them on the first
bootstrap pass:

```sh
./bootstrap.sh --adopt
```

Set up the optional Treemux sidebar with:

```sh
ENABLE_TREEMUX=1 ./bootstrap.sh
```

Bootstrap clones generated/plugin content and stows the packages listed in
`scripts/setup-stow.sh`.

## Bootstrap output

Bootstrap output uses `==>` section headers and indented status labels:

- `plan` means the command is printed by `--dry-run`
- `run` means the command is executing
- `skip` means the target already exists or the step does not apply
- `get`, `unpack`, `link`, `install`, and `plug` describe install actions
- `todo` means a manual follow-up remains after bootstrap completes
- `error` reports the script, line, failed command, and exit code when a setup
  command fails

Colors are enabled only for interactive terminals. Set `NO_COLOR=1` to force
plain output.
