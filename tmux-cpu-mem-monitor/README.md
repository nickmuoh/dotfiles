# tmux-cpu-mem-monitor

Vendored fork of <https://github.com/hendrikmi/tmux-cpu-mem-monitor>.

## Installed path

- `~/.tmux/plugins/tmux-cpu-mem-monitor`

## Install

```sh
stow -v tmux-cpu-mem-monitor
```

Or run the repo bootstrap, which also syncs the plugin dependencies:

```sh
./bootstrap.sh
```

## Dependencies

- `uv` via `bootstrap.sh`
- `psutil==6.0.0` via `uv sync`
