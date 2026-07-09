# Shell setup notes

This repo tracks the shell/editor setup under `/home/nmuoh/.dotfiles` and is organized for Stow.

## Package docs

- [bash](bash/README.md)
- [tmux](tmux/README.md)
- [treemux](treemux/README.md)
- [micro](micro/README.md)
- [nvim](nvim/README.md)
- [starship](starship/README.md)
- [fzf](fzf/README.md)
- [local-bin](local-bin/README.md)
- [bash-completions](bash-completions/README.md)
- [git](git/README.md)
- [lazygit](lazygit/README.md)
- [copilot](copilot/README.md)
- [claude](claude/README.md)
- [snowflake](snowflake/README.md)
- [agents](agents/README.md)
- [fnm](fnm/README.md)
- [tmux-cpu-mem-monitor](tmux-cpu-mem-monitor/README.md)

## Root docs

- `AGENTS.md`
- [`docs/`](docs/) — per-tool reference docs
- [`docs/fd.md`](docs/fd.md)
- [`docs/fnm.md`](docs/fnm.md)
- [`docs/uv.md`](docs/uv.md)

## Layout

- Root docs stay at the repo root and are never stowed
- Package docs live beside their package config in `<package>/README.md`
- Generated content belongs in `bootstrap.sh`; vendored tool source can also live in a dedicated Stow package

## Working with Stow

Each package directory mirrors the file path that should exist under `$HOME`.
For example, `tmux/.tmux.conf` is deployed as `~/.tmux.conf`.

Edit the package file in this repo when changing config:

```sh
$EDITOR tmux/.tmux.conf
```

Check that the deployed file is linked back to the package:

```sh
ls -l ~/.tmux.conf
```

Preview Stow changes before applying them:

```sh
stow -nv tmux
```

Apply the package after the preview looks correct:

```sh
stow -v tmux
```

If a config already exists in `$HOME` before the package is stowed, move,
adopt, or overwrite that file before deploying the package. Stow does not
overwrite unrelated files by default.

After changing tmux config, reload it in a running tmux session with:

```sh
tmux source-file ~/.tmux.conf
```

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

To replace existing matching files in `$HOME` with the tracked files from this
repo, run:

```sh
./bootstrap.sh --overwrite
```

`--overwrite` removes existing file and symlink targets for configured Stow
packages before running Stow. It does not remove directory targets.

By default, tool setup checks local package or command state and skips installed
tools before doing network install work. To reinstall or refresh tools, run:

```sh
./bootstrap.sh --reinstall-tools
```

Treemux is enabled by default. Disable it with:

```sh
ENABLE_TREEMUX=0 ./bootstrap.sh
```

Bootstrap clones generated/plugin content and stows the packages listed in
`scripts/setup-stow.sh`.
After stowing `local-bin`, `setup-postinstall.sh` runs `sync-agent-skills`
when `~/.agents/.skill-lock.json` and the Node tooling are available.

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
