#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/scripts/lib.sh"

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
  setup-pi.sh
  setup-postinstall.sh

Options:
  -n, --dry-run          Print planned commands without changing files
  -p, --package NAME     Install only selected package-scoped items
      --adopt            Pass --adopt to GNU Stow when stowing packages
      --overwrite        Remove existing package-file targets before stowing
      --reinstall-tools  Reinstall or refresh tools even when already installed
  -h, --help             Show this help message

Optional environment:
  NO_COLOR=1        Disable colored bootstrap output

Examples:
  ./bootstrap.sh --dry-run
  ./bootstrap.sh
  ./bootstrap.sh --adopt
  ./bootstrap.sh --overwrite
  ./bootstrap.sh --reinstall-tools
  ./bootstrap.sh --package claude
EOF
}

DRY_RUN=0
ADOPT=0
OVERWRITE=0
REINSTALL_TOOLS=0
declare -a BOOTSTRAP_PACKAGES=()

while (($#)); do
  case "$1" in
    -n|--dry-run)
      DRY_RUN=1
      shift
      ;;
    -p|--package)
      if [ "$#" -lt 2 ]; then
        printf 'bootstrap: missing value for %s\n' "$1" >&2
        usage >&2
        exit 1
      fi
      BOOTSTRAP_PACKAGES+=("$2")
      shift 2
      ;;
    --package=*)
      BOOTSTRAP_PACKAGES+=("${1#*=}")
      shift
      ;;
    --adopt)
      ADOPT=1
      shift
      ;;
    --overwrite)
      OVERWRITE=1
      shift
      ;;
    --reinstall-tools)
      REINSTALL_TOOLS=1
      shift
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
export BOOTSTRAP_PACKAGES="${BOOTSTRAP_PACKAGES[*]}"

if bootstrap_package_mode; then
  scripts=(
    setup-tools.sh
    setup-stow.sh
    setup-pi.sh
  )
else
  scripts=(
    setup-wsl.sh
    setup-tools.sh
    setup-stow.sh
    setup-micro.sh
    setup-tmux.sh
    setup-treemux.sh
    setup-nvim.sh
    setup-pi.sh
    setup-postinstall.sh
  )
fi

for script in "${scripts[@]}"; do
  ensure_executable "${script_dir}/scripts/${script}"
  "${script_dir}/scripts/${script}"
done

log "Bootstrap complete"
