#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./bootstrap.sh [options]

Runs the shell setup bootstrap scripts in order:
  setup-wsl.sh
  setup-tools.sh
  setup-stow.sh
  setup-micro.sh
  setup-tmux.sh
  setup-treemux.sh
  setup-nvim.sh
  setup-postinstall.sh

Options:
  -n, --dry-run          Print planned commands without changing files
      --adopt            Pass --adopt to GNU Stow when stowing packages
      --overwrite        Remove existing package-file targets before stowing
      --reinstall-tools  Reinstall or refresh tools even when already installed
  -h, --help             Show this help message

Optional environment:
  ENABLE_TREEMUX=1  Create the Treemux Python venv and install neovim
  NO_COLOR=1        Disable colored bootstrap output

Examples:
  ./bootstrap.sh --dry-run
  ./bootstrap.sh
  ./bootstrap.sh --adopt
  ./bootstrap.sh --overwrite
  ./bootstrap.sh --reinstall-tools
  ENABLE_TREEMUX=1 ./bootstrap.sh
EOF
}

DRY_RUN=0
ADOPT=0
OVERWRITE=0
REINSTALL_TOOLS=0
for arg in "$@"; do
  case "$arg" in
    -n|--dry-run)
      DRY_RUN=1
      ;;
    --adopt)
      ADOPT=1
      ;;
    --overwrite)
      OVERWRITE=1
      ;;
    --reinstall-tools)
      REINSTALL_TOOLS=1
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

if [[ "$ADOPT" == "1" && "$OVERWRITE" == "1" ]]; then
  printf 'bootstrap: --adopt and --overwrite cannot be used together\n' >&2
  exit 1
fi

export DRY_RUN
export ADOPT
export OVERWRITE
export REINSTALL_TOOLS

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

. "${script_dir}/scripts/lib.sh"
log "Bootstrap complete"
