#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap

log "tmux plugins"
if ! is_dry_run; then
  need_cmd git
  need_cmd patch
fi

repo_root="$(bootstrap_root)"
indicator_dir="$HOME/.tmux/plugins/tmux-agent-indicator"
indicator_patch="$repo_root/tmux/patches/tmux-agent-indicator-session-dots.patch"

clone_if_missing "$HOME/.tmux/plugins/tpm" --depth 1 https://github.com/tmux-plugins/tpm

if [ -x "$HOME/.tmux/plugins/tpm/bin/install_plugins" ]; then
  run "$HOME/.tmux/plugins/tpm/bin/install_plugins"
fi

# The upstream dots mark only current/inactive/attention sessions. Extend them
# with numbered idle sessions plus running and done states so worker state stays
# visible and identifiable cross-session.
if [ -f "$indicator_patch" ] && [ -d "$indicator_dir" ]; then
  if grep -q '^RUNNING_SYMBOL=' "$indicator_dir/scripts/session-dots.sh" 2>/dev/null \
    && grep -q '^RESET_STYLE=' "$indicator_dir/scripts/session-dots.sh" 2>/dev/null \
    && grep -q '^DOT_SEPARATOR=' "$indicator_dir/scripts/session-dots.sh" 2>/dev/null \
    && grep -q '^IDLE_SYMBOLS=' "$indicator_dir/scripts/session-dots.sh" 2>/dev/null \
    && grep -q 'Associative arrays reject an empty subscript' "$indicator_dir/scripts/session-dots.sh" 2>/dev/null \
    && grep -q 'Needs-input is acknowledged only when focus returns' "$indicator_dir/scripts/pane-focus-in.sh" 2>/dev/null; then
    status skip "tmux-agent-indicator session-dot patch already applied"
  elif grep -q '^RUNNING_SYMBOL=' "$indicator_dir/scripts/session-dots.sh" 2>/dev/null \
    && [ -d "$indicator_dir/.git" ] && ! is_dry_run; then
    # Rebase an older copy of this patch onto the plugin before applying the
    # current patch; patch cannot match a file that already contains the old hunks.
    run git -C "$indicator_dir" checkout -- scripts/session-dots.sh scripts/pane-focus-in.sh
    run rm -f "$indicator_dir/scripts/session-dots.sh.orig" "$indicator_dir/scripts/session-dots.sh.rej"
    run_sh "patch -d $(printf '%q' "$indicator_dir") -p1 < $(printf '%q' "$indicator_patch")"
  elif is_dry_run; then
    status plan "patch -d $(printf '%q' "$indicator_dir") -p1 < $(printf '%q' "$indicator_patch")"
  else
    run_sh "patch -d $(printf '%q' "$indicator_dir") -p1 < $(printf '%q' "$indicator_patch")"
  fi
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
