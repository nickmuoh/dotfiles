# tmux CPU/MEM monitor

The `tmux-cpu-mem-monitor` package vendors a fork of `hendrikmi/tmux-cpu-mem-monitor` at `~/.tmux/plugins/tmux-cpu-mem-monitor`.

Its wrapper owns the CPU/MEM `status-right` segment. It runs metrics through `uv`, rewrites CPU, memory, disk, and battery placeholders in tmux status formats, and preserves the `tmux-prefix-highlight` and agent-indicator placeholders. `uv sync` installs its `psutil==6.0.0` dependency.

The related tmux configuration is documented in [`tmux.md`](tmux.md).
