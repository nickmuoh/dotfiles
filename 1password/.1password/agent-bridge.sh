#!/usr/bin/env bash

_agent_bridge_restore_errexit=0
_agent_bridge_restore_nounset=0
_agent_bridge_restore_pipefail=0

case $- in
  *e*) _agent_bridge_restore_errexit=1 ;;
esac

case $- in
  *u*) _agent_bridge_restore_nounset=1 ;;
esac

if shopt -qo pipefail; then
  _agent_bridge_restore_pipefail=1
fi

_agent_bridge_restore_shell_options() {
  if [ "$_agent_bridge_restore_errexit" -eq 1 ]; then
    set -e
  else
    set +e
  fi

  if [ "$_agent_bridge_restore_nounset" -eq 1 ]; then
    set -u
  else
    set +u
  fi

  if [ "$_agent_bridge_restore_pipefail" -eq 1 ]; then
    set -o pipefail
  else
    set +o pipefail
  fi
}

set -euo pipefail

SSH_AUTH_SOCK="${SSH_AUTH_SOCK:-$HOME/.1password/agent.sock}"
export SSH_AUTH_SOCK

PATH="$HOME/.local/bin:$PATH"

if ! command -v socat >/dev/null 2>&1; then
  echo "[1Password WSL] Warning: 'socat' not found in WSL. Install it with: sudo apt update && sudo apt install -y socat"
  _agent_bridge_restore_shell_options
  return 0 2>/dev/null || exit 0
fi

if ! command -v npiperelay.exe >/dev/null 2>&1; then
  echo "[1Password WSL] Warning: 'npiperelay.exe' not found on PATH. Bootstrap should install it into ~/.local/bin."
  _agent_bridge_restore_shell_options
  return 0 2>/dev/null || exit 0
fi

mkdir -p "$HOME/.1password"

if pgrep -f "npiperelay.exe -ei -s //./pipe/openssh-ssh-agent" >/dev/null 2>&1; then
  _agent_bridge_restore_shell_options
  return 0 2>/dev/null || exit 0
fi

if [ -S "$SSH_AUTH_SOCK" ]; then
  rm -f "$SSH_AUTH_SOCK"
fi

echo "[1Password WSL] Starting SSH-Agent relay..."
setsid socat UNIX-LISTEN:"$SSH_AUTH_SOCK",fork EXEC:"npiperelay.exe -ei -s //./pipe/openssh-ssh-agent",nofork >/dev/null 2>&1 &

_agent_bridge_restore_shell_options
unset -f _agent_bridge_restore_shell_options
unset _agent_bridge_restore_errexit _agent_bridge_restore_nounset _agent_bridge_restore_pipefail
