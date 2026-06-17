#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

log "shell tools"

if ! command -v zoxide >/dev/null 2>&1; then
  run_sh 'curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh'
fi

clone_if_missing "$HOME/.fzf" --depth 1 https://github.com/junegunn/fzf.git
if [ ! -f "$HOME/.fzf.bash" ]; then
  run_sh "$HOME/.fzf/install --all --no-update-rc"
fi

if ! command -v micro >/dev/null 2>&1; then
  if is_dry_run; then
    printf '+ curl https://getmic.ro | bash && sudo mv micro /usr/bin/micro\n'
  else
    curl https://getmic.ro | bash
    sudo mv micro /usr/bin/micro
  fi
fi

if ! is_dry_run; then
  mkdir -p "$HOME/.local/bin" "$HOME/.local/share/bash-completion/completions"
fi

if [ ! -f "$HOME/.local/bin/keychain" ]; then
  run_sh 'curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/keychain.sh -o ~/.local/bin/keychain'
  run chmod +x "$HOME/.local/bin/keychain"
fi
if [ ! -f "$HOME/.local/share/bash-completion/completions/keychain" ]; then
  run_sh 'curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/completions/keychain.bash -o ~/.local/share/bash-completion/completions/keychain'
fi
