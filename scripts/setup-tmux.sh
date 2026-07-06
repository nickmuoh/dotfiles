#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap

log "tmux plugins"
if ! is_dry_run; then
  need_cmd git
fi

clone_if_missing "$HOME/.tmux/plugins/tpm" --depth 1 https://github.com/tmux-plugins/tpm

if [ -x "$HOME/.tmux/plugins/tpm/bin/install_plugins" ]; then
  run "$HOME/.tmux/plugins/tpm/bin/install_plugins"
fi

if [ -d "$HOME/.tmux/plugins/tmux-cpu-mem-monitor" ]; then
  if command -v uv >/dev/null 2>&1; then
    if is_dry_run; then
      status plan "cd $(printf '%q' "$HOME/.tmux/plugins/tmux-cpu-mem-monitor") && uv sync"
    else
      status run "cd $(printf '%q' "$HOME/.tmux/plugins/tmux-cpu-mem-monitor") && uv sync"
      (cd "$HOME/.tmux/plugins/tmux-cpu-mem-monitor" && uv sync)
    fi
  else
    status skip "uv not found; skipping tmux-cpu-mem-monitor sync"
  fi
fi
