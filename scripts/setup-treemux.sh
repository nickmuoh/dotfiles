#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

if [ "${ENABLE_TREEMUX:-0}" != "1" ]; then
  log "treemux disabled; skipping"
  exit 0
fi

log "treemux venv"
if ! is_dry_run; then
  need_cmd uv
fi

if is_dry_run; then
  printf '+ uv venv %q\n' "$HOME/.local/share/treemux-venv"
  printf '+ uv pip install --python %q neovim\n' "$HOME/.local/share/treemux-venv/bin/python"
else
  uv venv "$HOME/.local/share/treemux-venv"
  uv pip install --python "$HOME/.local/share/treemux-venv/bin/python" neovim
fi
