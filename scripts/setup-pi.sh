#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap
parse_dry_run_args scripts/setup-pi.sh "$@"

if ! registry_hook_selected setup-pi; then
  exit 0
fi

log "pi"

npm_dir="$HOME/.pi/agent/npm"

if [ ! -d "$npm_dir" ]; then
  status skip "~/.pi/agent/npm not found; pi not installed"
  exit 0
fi

sublog "npm patches"
if is_dry_run; then
  status plan "npm install --prefix $npm_dir"
else
  run npm install --prefix "$npm_dir"
fi
