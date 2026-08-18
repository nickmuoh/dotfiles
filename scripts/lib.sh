#!/usr/bin/env bash
set -euo pipefail

__BOOTSTRAP_TEMP_DIRS=()
__BOOTSTRAP_TRAPS_ENABLED=0

# The registry is intentionally Bash-only so it works before bootstrap installs tools.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/package-registry.sh"

# Print the repository root based on this library's location.
# Args: none.
# Outputs: absolute repo path on stdout.
bootstrap_root() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "${script_dir}/.."
  pwd
}

# Return success when the bootstrap is running in preview mode.
# Args: none. Reads DRY_RUN from environment.
# Returns: 0 when DRY_RUN=1, otherwise 1.
is_dry_run() {
  [[ "${DRY_RUN:-0}" == "1" ]]
}

# Return success when bootstrap package mode is active.
# Args: none. Reads BOOTSTRAP_PACKAGES from environment.
bootstrap_package_mode() {
  [[ -n "${BOOTSTRAP_PACKAGES:-}" ]]
}

# Return success when any selected bootstrap package matches one of the names.
# Args: $@ package names to match against the selected package list.
# Returns: 0 when package mode is off or any name matches.
bootstrap_package_selected() {
  local candidate
  for candidate in "$@"; do
    registry_package_selected "$candidate" && return 0
  done
  return 1
}

# Return success when colored output should be emitted.
# Args: none. Reads NO_COLOR and TERM from environment.
# Returns: 0 when stdout is interactive and color is allowed.
use_color() {
  [[ -t 1 && -z "${NO_COLOR:-}" && "${TERM:-}" != "dumb" ]]
}

# Print text with an ANSI color code when color is enabled.
# Args: $1 ANSI color code, $@ text to print after shifting code.
# Outputs: colored or plain text on stdout, without adding a newline.
color() {
  local code=$1
  shift
  if use_color; then
    printf '\033[%sm%s\033[0m' "$code" "$*"
  else
    printf '%s' "$*"
  fi
}

# Print a top-level bootstrap section heading.
# Args: $@ heading text.
# Outputs: "==> <heading>" line on stdout.
log() {
  color '1;34' '==>'
  printf ' '
  color '1' "$*"
  printf '\n'
}

# Print a nested section heading under the current bootstrap section.
# Args: $@ nested heading text.
# Outputs: blank line plus indented heading on stdout.
sublog() {
  printf '\n  '
  color '1' "$*"
  printf '\n'
}

# Print an indented structured status line with a colored label.
# Args: $1 status label, $@ message text after shifting label.
# Outputs: indented, aligned status line on stdout.
status() {
  local label=$1
  shift
  local label_color=36
  case "$label" in
    done) label_color=32 ;;
    skip) label_color=33 ;;
    todo) label_color=35 ;;
    error) label_color=31 ;;
    plan) label_color=36 ;;
  esac
  printf '    '
  color "$label_color" "$(printf '%-7s' "$label")"
  printf '  %s\n' "$*"
}

# Print a shell-escaped command string from an argv-style command.
# Args: $@ command argv tokens.
# Outputs: one shell-escaped command string on stdout.
command_string() {
  local arg
  local quoted=()
  for arg in "$@"; do
    printf -v arg '%q' "$arg"
    quoted+=("$arg")
  done
  local IFS=' '
  printf '%s' "${quoted[*]}"
}

# Print a fatal bootstrap message and exit with code 1.
# Args: $@ fatal message text.
# Outputs: "bootstrap: <message>" on stderr.
die() {
  printf 'bootstrap: %s\n' "$*" >&2
  exit 1
}

# Require a command to exist on PATH before continuing.
# Args: $1 command name to find on PATH.
# Exits: code 1 via die when command is missing.
need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

# Require a named value to be non-empty.
# Args: $1 human-readable value name, $2 value to validate.
# Exits: code 1 via die when value is empty or unset.
require_nonempty_arg() {
  local name=$1
  local value=${2:-}
  [[ -n "$value" ]] || die "missing required value: $name"
}

# Require a path to exist as a regular file.
# Args: $1 path to validate.
# Exits: code 1 via die when path is not a regular file.
require_file() {
  local path=$1
  [[ -f "$path" ]] || die "missing required file: $path"
}

# Require a path to exist as a directory.
# Args: $1 path to validate.
# Exits: code 1 via die when path is not a directory.
require_dir() {
  local path=$1
  [[ -d "$path" ]] || die "missing required directory: $path"
}

# Ensure a file is executable.
# Args: $1 path to validate and chmod when needed.
# Effects: prints a dry-run plan or runs chmod +x when the bit is missing.
ensure_executable() {
  local path=$1

  if [[ -x "$path" ]]; then
    return 0
  fi

  if is_dry_run; then
    status plan "chmod +x $path"
  else
    run chmod +x "$path"
  fi
}

# Remove temp directories registered by make_temp_dir.
# Args: none. Reads __BOOTSTRAP_TEMP_DIRS.
# Effects: removes registered directories that still exist.
cleanup_temp_dirs() {
  local dir
  local cleanup_status

  # Bash with nounset errors on empty arrays, so disable it only for this loop.
  set +u
  for dir in "${__BOOTSTRAP_TEMP_DIRS[@]}"; do
    if [[ -n "$dir" && -d "$dir" ]]; then
      rm -rf -- "$dir"
    fi
  done
  cleanup_status=$?
  set -u
  return "$cleanup_status"
}

# EXIT trap handler that preserves the script's original exit code.
# Args: none. Reads current exit status from $?
# Effects: runs cleanup_temp_dirs before exiting with original status.
on_exit() {
  local exit_code=$?
  cleanup_temp_dirs || true
  exit "$exit_code"
}

# ERR trap handler that reports the failing command and preserves its exit code.
# Args: $1 exit code, $2 line number, $3 failing command string.
# Effects: prints structured error, disables ERR trap, exits with $1.
on_error() {
  local exit_code=$1
  local line=$2
  local command=$3
  local source=${BASH_SOURCE[1]:-$0}

  trap - ERR
  report_error "$exit_code" "$source" "$line" "$command"
  exit "$exit_code"
}

# Print a structured bootstrap error line.
# Args: $1 exit code, $2 source path, $3 line number, $4 command string.
# Outputs: structured error status line on stderr.
report_error() {
  local exit_code=$1
  local source=$2
  local line=$3
  local command=$4

  status error "failed at ${source}:${line}: ${command} (exit ${exit_code})" >&2
}

# Enable shared ERR and EXIT traps once for the current script.
# Args: none.
# Effects: installs ERR/EXIT traps and enables errtrace for functions.
enable_error_trap() {
  if [[ "$__BOOTSTRAP_TRAPS_ENABLED" == "1" ]]; then
    return
  fi

  trap 'on_error "$?" "$LINENO" "$BASH_COMMAND"' ERR
  trap on_exit EXIT
  set -E
  __BOOTSTRAP_TRAPS_ENABLED=1
  ensure_tmpdir
}

# Ensure TMPDIR points at an existing writable directory before installers run.
# Args: none. Reads and exports TMPDIR.
# Effects: creates TMPDIR when needed during real runs.
ensure_tmpdir() {
  local tmp_base=${TMPDIR:-/tmp}

  if is_dry_run; then
    return 0
  fi

  mkdir -p "$tmp_base"
  require_dir "$tmp_base"
  [[ -w "$tmp_base" ]] || die "temp directory is not writable: $tmp_base"

  tmp_base="$(cd "$tmp_base" && pwd)"
  export TMPDIR="$tmp_base"
}

# Create a temp directory, register it for cleanup, and assign it to var_name.
# Args: $1 mktemp prefix, $2 caller variable name to receive path.
# Effects: appends directory to __BOOTSTRAP_TEMP_DIRS.
make_temp_dir() {
  local prefix=$1
  local var_name=${2:-}
  local created_dir

  require_nonempty_arg "temp directory prefix" "$prefix"
  require_nonempty_arg "temp directory variable" "$var_name"
  created_dir="$(mktemp -d "${TMPDIR:-/tmp}/${prefix}.XXXXXX")"
  __BOOTSTRAP_TEMP_DIRS+=("$created_dir")
  printf -v "$var_name" '%s' "$created_dir"
}

# Run a command with structured dry-run output and failure reporting.
# Args: $@ command argv tokens.
# Effects: in dry-run, prints plan only; otherwise runs command.
# Exits: failed command exit code after structured error reporting.
run() {
  if is_dry_run; then
    status plan "$(command_string "$@")"
  else
    local caller
    local caller_line
    local caller_source
    local exit_code

    status run "$(command_string "$@")"
    if "$@"; then
      return 0
    else
      exit_code=$?
    fi
    caller="$(caller 0)"
    caller_line=${caller%% *}
    caller_source=${caller##* }
    report_error "$exit_code" "$caller_source" "$caller_line" "$(command_string "$@")"
    exit "$exit_code"
  fi
}

# Run a shell command string with structured dry-run output and failure reporting.
# Args: $@ shell command string tokens, joined as one string.
# Effects: in dry-run, prints plan only; otherwise runs via bash -lc.
# Exits: failed shell exit code after structured error reporting.
run_sh() {
  if is_dry_run; then
    status plan "$*"
  else
    local caller
    local caller_line
    local caller_source
    local exit_code

    status run "$*"
    if bash -lc "$*"; then
      return 0
    else
      exit_code=$?
    fi
    caller="$(caller 0)"
    caller_line=${caller%% *}
    caller_source=${caller##* }
    report_error "$exit_code" "$caller_source" "$caller_line" "$*"
    exit "$exit_code"
  fi
}

# Clone a repository into dest unless that path already exists.
# Args: $1 destination path, $@ git clone arguments after shifting dest.
# Effects: prints skip when dest exists; otherwise runs git clone.
clone_if_missing() {
  local dest=$1
  shift
  if [ -e "$dest" ]; then
    status skip "$dest already exists"
  else
    run git clone "$@" "$dest"
  fi
}
