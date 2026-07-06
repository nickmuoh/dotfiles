#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap

log "micro plugins"
if ! is_dry_run; then
  need_cmd git
  need_cmd micro
fi

install_micro_plugin() {
  local plugin=$1
  if is_dry_run; then
    status plan "micro -plugin install $plugin"
  else
    status plug "$plugin"
    micro -plugin install "$plugin"
  fi
}

for plugin in gitStatus preview fzfinder jump wc; do
  install_micro_plugin "$plugin"
done

clone_if_missing "$HOME/.config/micro/plug/palettero" https://github.com/terokarvinen/palettero
clone_if_missing "$HOME/.config/micro/plug/iconic_tabs" https://github.com/dalekirkwood/Micro_Editor_Iconic_Tabs
