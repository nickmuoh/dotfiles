#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap
parse_dry_run_args scripts/setup-postinstall.sh "$@"

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

repo_skillx="$(bootstrap_root)/local-bin/.local/bin/skillx"

skillx_cmd() {
  if command -v skillx >/dev/null 2>&1; then
    printf '%s\n' skillx
    return 0
  fi

  if [ -x "$repo_skillx" ]; then
    printf '%s\n' "$repo_skillx"
    return 0
  fi

  return 1
}

# Collect existing identity files selected by the effective GitHub SSH config.
# Do not fall back to arbitrary ~/.ssh keys: multiple keys must not be guessed.
discover_github_ssh_keys() {
  local keyword candidate existing
  local duplicate
  SSH_KEY_CANDIDATES=()

  command -v ssh >/dev/null 2>&1 || return 0
  while read -r keyword candidate; do
    [[ "$keyword" == "identityfile" && -n "$candidate" ]] || continue
    if [[ "$candidate" == "~/"* ]]; then
      candidate="$HOME/${candidate#"~/"}"
    elif [[ "$candidate" != /* ]]; then
      continue
    fi
    [[ "$candidate" != *%* && -f "$candidate" ]] || continue

    duplicate=0
    for existing in "${SSH_KEY_CANDIDATES[@]}"; do
      if [[ "$existing" == "$candidate" ]]; then
        duplicate=1
        break
      fi
    done
    [[ "$duplicate" == "1" ]] || SSH_KEY_CANDIDATES+=("$candidate")
  done < <(ssh -G github.com 2>/dev/null)
}

show_ssh_key_todo() {
  discover_github_ssh_keys
  case "${#SSH_KEY_CANDIDATES[@]}" in
    0)
      status todo 'ssh-add ~/.ssh/<your-github-key> (no configured GitHub key found)'
      ;;
    1)
      status todo "$(command_string ssh-add "${SSH_KEY_CANDIDATES[0]}")"
      ;;
    *)
      status todo 'ssh-add ~/.ssh/<your-github-key> (multiple configured keys found; choose the GitHub key)'
      ;;
  esac
}

if [ -f "$HOME/.agents/.skill-lock.json" ]; then
  if sync_cmd="$(skillx_cmd)"; then
    if is_dry_run; then
      status plan "$sync_cmd sync"
    else
      run "$sync_cmd" sync
    fi
  else
    status todo "skillx sync after ~/.agents/.skill-lock.json is available and node tooling is installed"
  fi
else
  status todo "skillx sync after ~/.agents/.skill-lock.json is available and node tooling is installed"
fi

show_ssh_key_todo
status todo "source ~/.bashrc"
