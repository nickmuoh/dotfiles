#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"
enable_error_trap

log "postinstall"

if command -v gh >/dev/null 2>&1; then
  status todo "gh auth login"
else
  status skip "gh not found; skipping auth reminder"
fi

status todo "ssh-add ~/.ssh/nick_muoh.trimble-github.ed25519"
status todo "source ~/.bashrc"
