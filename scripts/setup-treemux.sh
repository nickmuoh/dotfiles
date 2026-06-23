#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"
enable_error_trap

if [ "${ENABLE_TREEMUX:-0}" != "1" ]; then
  log "treemux"
  status skip "disabled"
  exit 0
fi

log "treemux venv"
if ! is_dry_run; then
  need_cmd uv
fi

if is_dry_run; then
  status plan "uv venv $(printf '%q' "$HOME/.local/share/treemux-venv")"
  status plan "uv pip install --python $(printf '%q' "$HOME/.local/share/treemux-venv/bin/python") neovim"
else
  status run "uv venv $(printf '%q' "$HOME/.local/share/treemux-venv")"
  uv venv "$HOME/.local/share/treemux-venv"
  status run "uv pip install --python $(printf '%q' "$HOME/.local/share/treemux-venv/bin/python") neovim"
  uv pip install --python "$HOME/.local/share/treemux-venv/bin/python" neovim
fi
