#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap

log "postinstall"

check_status() {
  local message=$1
  shift
  if "$@" >/dev/null 2>&1; then
    status done "$message"
  else
    status todo "$message"
  fi
}

if command -v gh >/dev/null 2>&1; then
  check_status "gh auth login" gh auth status -t
else
  status skip "gh not found; skipping auth reminder"
fi

if command -v fnm >/dev/null 2>&1; then
  check_status "fnm install --lts" bash -lc 'fnm list | grep -q "lts-latest"'
  check_status "fnm default lts-latest" bash -lc 'fnm list | grep -q "default, lts-latest"'
  check_status "node --version" node --version
  check_status "npm --version" npm --version
else
  status skip "fnm not found; skipping Node LTS reminder"
fi

if command -v uv >/dev/null 2>&1; then
  check_status "uv python install 3.12" uv python find 3.12
  check_status "python3.12 --version" python3.12 --version
else
  status skip "uv not found; skipping Python 3.12 reminder"
fi

repo_sync_helper="$(bootstrap_root)/local-bin/.local/bin/sync-agent-skills"

sync_agent_skills_cmd() {
  if command -v sync-agent-skills >/dev/null 2>&1; then
    printf '%s\n' sync-agent-skills
    return 0
  fi

  if [ -x "$repo_sync_helper" ]; then
    printf '%s\n' "$repo_sync_helper"
    return 0
  fi

  return 1
}

if [ -f "$HOME/.agents/.skill-lock.json" ]; then
  if sync_cmd="$(sync_agent_skills_cmd)"; then
    if is_dry_run; then
      status plan "$sync_cmd"
    else
      run "$sync_cmd"
    fi
  else
    status todo "sync-agent-skills after ~/.agents/.skill-lock.json is available and node tooling is installed"
  fi
else
  status todo "sync-agent-skills after ~/.agents/.skill-lock.json is available and node tooling is installed"
fi

status todo "ssh-add ~/.ssh/nick_muoh.trimble-github.ed25519"
status todo "source ~/.bashrc"
