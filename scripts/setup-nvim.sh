#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"
enable_error_trap

log "neovim bootstrap"
if ! is_dry_run; then
  need_cmd nvim
fi

if is_dry_run; then
  status plan 'nvim --headless "+Lazy! sync" +qa'
else
  status run 'nvim --headless "+Lazy! sync" +qa'
  nvim --headless "+Lazy! sync" +qa
fi
