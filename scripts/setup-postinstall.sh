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

if command -v fnm >/dev/null 2>&1; then
  status todo "fnm install --lts"
  status todo "fnm default lts-latest"
  status todo "node --version"
  status todo "npm --version"
else
  status skip "fnm not found; skipping Node LTS reminder"
fi

if command -v uv >/dev/null 2>&1; then
  status todo "uv python install 3.12"
  status todo "python3.12 --version"
else
  status skip "uv not found; skipping Python 3.12 reminder"
fi

status todo "ssh-add ~/.ssh/nick_muoh.trimble-github.ed25519"
status todo "source ~/.bashrc"
