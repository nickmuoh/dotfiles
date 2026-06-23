#!/usr/bin/env bash
set -euo pipefail

bootstrap_root() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "${script_dir}/.."
  pwd
}

is_dry_run() {
  [[ "${DRY_RUN:-0}" == "1" ]]
}

log() {
  printf '==> %s\n' "$*"
}

die() {
  printf 'bootstrap: %s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

run() {
  if is_dry_run; then
    printf '+ '
    printf '%q ' "$@"
    printf '\n'
  else
    "$@"
  fi
}

run_sh() {
  if is_dry_run; then
    printf '+ %s\n' "$*"
  else
    bash -lc "$*"
  fi
}

clone_if_missing() {
  local dest=$1
  shift
  if [ -e "$dest" ]; then
    log "skip existing $dest"
  else
    run git clone "$@" "$dest"
  fi
}

