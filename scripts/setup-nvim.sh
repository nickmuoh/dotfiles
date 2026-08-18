#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap
parse_dry_run_args scripts/setup-nvim.sh "$@"

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
