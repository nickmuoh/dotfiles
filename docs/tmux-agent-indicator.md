# tmux-agent-indicator

`tmux-agent-indicator` is configured in this repository:

- `tmux/.tmux.conf` configures the plugin through TPM, appends its placeholders after the CPU/MEM wrapper, enables the configurable worker-state session dots, and configures Pi (`π`), Cortex, Coco, and Copilot process fallback. `scripts/setup-tmux.sh` installs TPM and its plugins.
- `pi/patches/tmux-agent-indicator-session-dots.patch` extends the upstream session-dot script, handles stale seen-session markers without blanking the dot segment, and clears `needs-input` once its source pane is focused; `scripts/setup-tmux.sh` applies it after TPM installation.
- `tmux-cpu-mem-monitor/.tmux/plugins/tmux-cpu-mem-monitor/tmux_cpu_mem_monitor.tmux` preserves the Nord CPU/MEM segment while carrying the indicator placeholders to the final interpolation step.
- `pi/pi-tmux-agent-indicator/` contains the Stow-managed Pi extension.
- `pi/.pi/agent/extensions/pi-tmux-agent-indicator.ts` is the deployed extension entrypoint.

The extension is silent when the plugin is absent and does not block Pi while
calling `agent-state.sh`.
