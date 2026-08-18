#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap
parse_dry_run_args scripts/setup-treemux.sh "$@"

log "treemux venv"
if ! is_dry_run; then
  need_cmd uv
fi

if is_dry_run; then
  status plan "uv venv $(printf '%q' "$HOME/.local/share/treemux-venv")"
  status plan "uv pip install --python $(printf '%q' "$HOME/.local/share/treemux-venv/bin/python") neovim"
else
  status run "uv venv $(printf '%q' "$HOME/.local/share/treemux-venv")"
  uv venv --clear "$HOME/.local/share/treemux-venv"

  status run "uv pip install --python $(printf '%q' "$HOME/.local/share/treemux-venv/bin/python") neovim"
  uv pip install --python "$HOME/.local/share/treemux-venv/bin/python" neovim
fi
