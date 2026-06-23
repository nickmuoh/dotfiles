#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

log "micro plugins"
if ! is_dry_run; then
  need_cmd micro
fi

for plugin in gitStatus preview fzfinder; do
  if is_dry_run; then
    printf '+ micro -plugin install %s\n' "$plugin"
  else
    micro -plugin install "$plugin"
  fi
done

clone_if_missing "$HOME/.config/micro/plug/palettero" https://github.com/terokarvinen/palettero
clone_if_missing "$HOME/.config/micro/plug/jump" https://github.com/terokarvinen/micro-jump
clone_if_missing "$HOME/.config/micro/plug/iconic_tabs" https://github.com/dalekirkwood/Micro_Editor_Iconic_Tabs
clone_if_missing "$HOME/.config/micro/plug/wc" https://github.com/adamnpeace/micro-wc-plugin
