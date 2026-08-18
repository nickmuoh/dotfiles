#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap
parse_dry_run_args scripts/setup-wsl.sh "$@"

log "WSL"
if ! grep -qi microsoft /proc/version 2>/dev/null && [ -z "${WSL_DISTRO_NAME:-}" ]; then
  status skip "not running under WSL"
  exit 0
fi

sublog "pre-flight"
read -r -d '' wsl_conf <<'EOF' || true
[boot]
systemd=true
# Fix PMTUD blackhole to anansi.am.trimblecorp.net: the path MTU is ~1278 bytes but the router
# silently drops larger packets without sending ICMP "fragmentation needed", causing SSH to hang
# indefinitely during key exchange. This clamps the route MTU to match the path limit.
command = ip route add 10.7.56.198/32 via 172.17.48.1 dev eth0 mtu 1278

[user]
default=nmuoh

[automount]
options = "metadata"
EOF

if is_dry_run; then
  status plan "sudo tee /etc/wsl.conf >/dev/null <<'EOF'
$wsl_conf
EOF"
  status todo "wsl --shutdown from Windows"
else
  status run "sudo tee /etc/wsl.conf >/dev/null"
  printf '%s\n' "$wsl_conf" | sudo tee /etc/wsl.conf >/dev/null
  status todo "wsl --shutdown from Windows after this completes"
fi
