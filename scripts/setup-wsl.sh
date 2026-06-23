#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

log "WSL"
if ! grep -qi microsoft /proc/version 2>/dev/null && [ -z "${WSL_DISTRO_NAME:-}" ]; then
  status skip "not running under WSL"
  exit 0
fi

sublog "pre-flight"
if is_dry_run; then
  status plan "sudo tee /etc/wsl.conf >/dev/null <<'EOF'"
  cat <<'EOF'
[boot]
systemd=true

[user]
default=nmuoh

[automount]
options = "metadata"
EOF
  status todo "wsl --shutdown from Windows"
else
  status run "sudo tee /etc/wsl.conf >/dev/null"
  sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[user]
default=nmuoh

[automount]
options = "metadata"
EOF
  status todo "wsl --shutdown from Windows after this completes"
fi
