#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

log "stow packages"
if ! is_dry_run; then
  need_cmd stow
fi

repo_root="$(bootstrap_root)"
packages=(bash micro tmux nvim starship fzf local-bin bash-completions)

stow_args=(-v)
if is_dry_run; then
  stow_args=(-nv)
fi
if [[ "${ADOPT:-0}" == "1" ]]; then
  stow_args+=(--adopt)
fi

if is_dry_run; then
  printf '+ cd %q && ' "$repo_root"
  printf '%q ' stow "${stow_args[@]}" "${packages[@]}"
  printf '\n'
else
  (cd "$repo_root" && stow "${stow_args[@]}" "${packages[@]}")
fi
