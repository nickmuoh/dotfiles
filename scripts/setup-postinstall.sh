#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

log "postinstall"

if command -v gh >/dev/null 2>&1; then
  printf '%s\n' "gh auth login"
else
  log "gh not found; skipping auth reminder"
fi

printf '%s\n' "ssh-add ~/.ssh/nick_muoh.trimble-github.ed25519"
printf '%s\n' "source ~/.bashrc"

