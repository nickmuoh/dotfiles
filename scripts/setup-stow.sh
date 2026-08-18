#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib.sh"

enable_error_trap

usage() {
  cat <<'EOF'
Usage: scripts/setup-stow.sh [options]

Options:
  -n, --dry-run    Print planned commands without changing files
      --adopt      Pass --adopt to GNU Stow
      --overwrite  Remove existing package-file targets before stowing
  -h, --help       Show this help message
EOF
}

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
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown setup-stow argument: $arg"
      ;;
  esac
done
export DRY_RUN

log "stow packages"
# package selection is exported by bootstrap.sh before this subprocess starts.
repo_root="$(bootstrap_root)"
mapfile -t stow_records < <(registry_stow_packages)
packages=()
for record in "${stow_records[@]}"; do
  IFS='|' read -r _stow_package _stow_args <<< "$record"
  packages+=("$_stow_package")
done

if [[ "${ADOPT:-0}" == "1" && "${OVERWRITE:-0}" == "1" ]]; then
  die "--adopt and --overwrite cannot be used together"
fi

resolve_path() {
  local path=$1
  local link
  local dir
  local base

  if [ -L "$path" ]; then
    link="$(readlink "$path")"
    if [[ "$link" == /* ]]; then
      path="$link"
    else
      path="$(dirname "$path")/$link"
    fi
  fi

  dir="$(dirname "$path")"
  base="$(basename "$path")"
  if cd "$dir" 2>/dev/null; then
    printf '%s/%s\n' "$(pwd -P)" "$base"
  else
    printf '%s/%s\n' "$dir" "$base"
  fi
}

remove_overwrite_conflicts() {
  local package
  local source
  local package_rel
  local target
  local source_resolved
  local target_resolved

  for package in "${packages[@]}"; do
    while IFS= read -r -d '' source; do
      package_rel=${source#"$repo_root/$package/"}
      target="$HOME/$package_rel"

      if [ ! -e "$target" ] && [ ! -L "$target" ]; then
        continue
      fi

      source_resolved="$(resolve_path "$source")"
      target_resolved="$(resolve_path "$target")"
      if [[ "$target_resolved" == "$source_resolved" ]]; then
        continue
      fi

      if [ -d "$target" ] && [ ! -L "$target" ]; then
        die "refusing to overwrite directory target: $target"
      fi

      run rm -f "$target"
    done < <(find "$repo_root/$package" \( -type f -o -type l \) -print0)
  done
}

remove_matching_treemux_target() {
  local source="$repo_root/treemux/.tmux/plugins/treemux/configs/treemux_init.lua"
  local target="$HOME/.tmux/plugins/treemux/configs/treemux_init.lua"

  if [ ! -f "$target" ] || [ -L "$target" ]; then
    return
  fi

  if cmp -s "$source" "$target"; then
    run rm -f "$target"
  fi
}

stow_args=(-v)

if is_dry_run; then
  stow_args=(-nv)
fi

if [[ "${ADOPT:-0}" == "1" ]]; then
  stow_args+=(--adopt)
fi

if [[ "${OVERWRITE:-0}" == "1" ]]; then
  remove_overwrite_conflicts
fi

if ((${#packages[@]} == 0)); then
  status skip "no Stow packages selected"
  exit 0
fi
if ! is_dry_run; then
  need_cmd stow
fi

local_bin_dir="$repo_root/local-bin/.local/bin"
if bootstrap_package_selected local-bin && [[ -d "$local_bin_dir" ]]; then
  for helper in "$local_bin_dir"/*; do
    [[ -f "$helper" ]] || continue
    ensure_executable "$helper"
  done
fi

if bootstrap_package_selected treemux; then
  remove_matching_treemux_target
fi

for record in "${stow_records[@]}"; do
  IFS='|' read -r package package_args <<< "$record"
  package_stow_args=("${stow_args[@]}")
  if [[ -n "$package_args" ]]; then
    read -r -a extra_args <<< "$package_args"
    package_stow_args+=("${extra_args[@]}")
  fi
  if is_dry_run; then
    status plan "cd $(printf '%q' "$repo_root") && $(command_string stow "${package_stow_args[@]}" "$package")"
  else
    status run "cd $(printf '%q' "$repo_root") && $(command_string stow "${package_stow_args[@]}" "$package")"
    (cd "$repo_root" && stow "${package_stow_args[@]}" "$package")
  fi
done
