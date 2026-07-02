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

## Current behavior

- `tmux_cpu_mem_monitor.tmux` is the source of truth for the custom tmux CPU/MEM right status segment.
- The wrapper builds `status-right` with a `#{prefix_highlight}` placeholder, Nord-style separators, and the CPU/MEM icons.
- It rewrites `#{cpu}`, `#{mem}`, `#{disk}`, and `#{battery}` placeholders in `status-right`, `status-left`, and `status-format[0|1]` to `uv run --project ... src/*.py` commands.
- `tmux-prefix-highlight` is expected to run separately afterwards so the final status line keeps the custom `^A` prefix segment.

## tmux options used by the wrapper

- `@prefix_highlight_fg`
- `@prefix_highlight_bg`
- `@prefix_highlight_prefix_prompt`
- `@cpu_mem_lead_style`
- `@cpu_mem_metric_style`
- `@cpu_mem_metric_separator`
- `@cpu_mem_cpu_icon`
- `@cpu_mem_mem_icon`
