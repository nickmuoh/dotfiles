#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

log "neovim bootstrap"
if ! is_dry_run; then
  need_cmd nvim
fi

if is_dry_run; then
  printf '+ nvim --headless "+Lazy! sync" +qa\n'
else
  nvim --headless "+Lazy! sync" +qa
fi
