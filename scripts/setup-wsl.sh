#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

if ! grep -qi microsoft /proc/version 2>/dev/null && [ -z "${WSL_DISTRO_NAME:-}" ]; then
  log "not running under WSL; skipping"
  exit 0
fi

log "WSL pre-flight"
if is_dry_run; then
  cat <<'EOF'
+ sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[user]
default=nmuoh

[automount]
options = "metadata"
EOF
  printf '%s\n' "++ wsl --shutdown (from Windows)"
else
  sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[user]
default=nmuoh

[automount]
options = "metadata"
EOF
  printf '%s\n' "wsl --shutdown (from Windows) after this completes"
fi

