#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

log "system packages"
run sudo apt-get update
run sudo apt-get install -y \
  bash-completion curl git ctags fzf bat jq yq tmux pandoc \
  starship gh neovim stow

if ! command -v uv >/dev/null 2>&1; then
  log "installing uv"
  if is_dry_run; then
    printf '+ curl -LsSf https://astral.sh/uv/install.sh -o /dev/null | sh\n'
  else
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi
fi
