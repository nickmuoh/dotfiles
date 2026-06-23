#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./bootstrap.sh [--dry-run] [--adopt]

Runs the shell setup bootstrap scripts in order.
EOF
}

DRY_RUN=0
ADOPT=0
for arg in "$@"; do
  case "$arg" in
    -n|--dry-run)
      DRY_RUN=1
      ;;
    --adopt)
      ADOPT=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'bootstrap: unknown argument: %s\n' "$arg" >&2
      usage >&2
      exit 1
      ;;
  esac
done

export DRY_RUN
export ADOPT

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
scripts=(
  setup-wsl.sh
  setup-tools.sh
  setup-stow.sh
  setup-micro.sh
  setup-tmux.sh
  setup-treemux.sh
  setup-nvim.sh
  setup-postinstall.sh
)

for script in "${scripts[@]}"; do
  "${script_dir}/scripts/${script}"
done

printf '%s\n' "bootstrap complete"
