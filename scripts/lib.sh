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

use_color() {
  [[ -t 1 && -z "${NO_COLOR:-}" && "${TERM:-}" != "dumb" ]]
}

color() {
  local code=$1
  shift
  if use_color; then
    printf '\033[%sm%s\033[0m' "$code" "$*"
  else
    printf '%s' "$*"
  fi
}

log() {
  color '1;34' '==>'
  printf ' '
  color '1' "$*"
  printf '\n'
}

sublog() {
  printf '\n  '
  color '1' "$*"
  printf '\n'
}

status() {
  local label=$1
  shift
  local label_color=36
  case "$label" in
    done) label_color=32 ;;
    skip) label_color=33 ;;
    todo) label_color=35 ;;
    error) label_color=31 ;;
    plan) label_color=36 ;;
  esac
  printf '    '
  color "$label_color" "$(printf '%-7s' "$label")"
  printf '  %s\n' "$*"
}

command_string() {
  local arg
  local quoted=()
  for arg in "$@"; do
    printf -v arg '%q' "$arg"
    quoted+=("$arg")
  done
  local IFS=' '
  printf '%s' "${quoted[*]}"
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
    status plan "$(command_string "$@")"
  else
    status run "$(command_string "$@")"
    "$@"
  fi
}

run_sh() {
  if is_dry_run; then
    status plan "$*"
  else
    status run "$*"
    bash -lc "$*"
  fi
}

clone_if_missing() {
  local dest=$1
  shift
  if [ -e "$dest" ]; then
    status skip "$dest already exists"
  else
    run git clone "$@" "$dest"
  fi
}
