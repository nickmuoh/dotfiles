#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"
enable_error_trap

usage() {
  cat <<'EOF'
Usage: scripts/setup-tools.sh [options]

Options:
  -n, --dry-run          Print planned commands without changing files
      --reinstall-tools Reinstall or refresh tools even when already installed
  -h, --help             Show this help message
EOF
}

REINSTALL_TOOLS="${REINSTALL_TOOLS:-0}"
for arg in "$@"; do
  case "$arg" in
    -n|--dry-run)
      DRY_RUN=1
      ;;
    --reinstall-tools)
      REINSTALL_TOOLS=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'setup-tools: unknown argument: %s\n' "$arg" >&2
      usage >&2
      exit 1
      ;;
  esac
done
export DRY_RUN
export REINSTALL_TOOLS

should_reinstall_tools() {
  [[ "${REINSTALL_TOOLS:-0}" == "1" ]]
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

apt_package_installed() {
  dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q 'install ok installed'
}

## [apt packages]
# Add or remove package names here. apt handles install and future upgrades.
APT_PACKAGES=(
  bash-completion curl git fzf bat jq yq tmux starship gh stow
  lazygit universal-ctags unzip libpq-dev libsqlite3-dev python3-dev gcc
)

## [github release versions]
# Update the version variable here when upgrading a tool.
# nvim uses the /latest/ GitHub redirect and does not need a pinned version.
RG_VERSION="14.1.1"
PANDOC_VERSION="3.10"
KEYCHAIN_VERSION="3.0.0_beta1"

## [github release installs]
# Each entry is a pipe-delimited string:  "cmd|method|url"  or  "cmd|method|url|extra"
#
#   cmd    — the binary name (used for the idempotency check and symlink target)
#   method — one of: deb | tarball | bin
#   url    — direct download URL for the release artifact
#   extra  — method-specific detail (see below)
#
# Methods:
#   deb     Installs a .deb via sudo dpkg -i.
#           Skipped when: command -v <cmd> succeeds.
#           extra: not used.
#
#   tarball Extracts a .tar.gz to ~/.local/opt/<extra>/ then symlinks
#           ~/.local/bin/<cmd> → ~/.local/opt/<extra>/bin/<cmd>.
#           Skipped when: ~/.local/opt/<extra> already exists.
#           extra: the top-level directory name inside the tarball
#                  (e.g. nvim-linux-x86_64).
#
#   bin     Extracts a single binary from a .tar.gz directly into
#           ~/.local/bin/<cmd> and marks it executable.
#           Skipped when: ~/.local/bin/<cmd> already exists.
#           extra: path to the binary inside the tarball
#                  (e.g. pandoc-3.10/bin/pandoc).
#
#   direct  Downloads a single file directly to ~/.local/bin/<cmd> and marks it
#           executable. Use for single-file releases (.pyz, prebuilt scripts, etc).
#           Skipped when: command -v <cmd> succeeds.
#           extra: not used.
#
GITHUB_INSTALLS=(
  "nvim|tarball|https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz|nvim-linux-x86_64"
  "rg|deb|https://github.com/BurntSushi/ripgrep/releases/download/${RG_VERSION}/ripgrep_${RG_VERSION}-1_amd64.deb"
  "pandoc|bin|https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz|pandoc-${PANDOC_VERSION}/bin/pandoc"
  "keychain|direct|https://github.com/danielrobbins/keychain/releases/download/${KEYCHAIN_VERSION}/keychain-${KEYCHAIN_VERSION}.pyz"
)

## [install]

log "apt packages"
apt_targets=()
for pkg in "${APT_PACKAGES[@]}"; do
  if should_reinstall_tools || ! apt_package_installed "$pkg"; then
    apt_targets+=("$pkg")
  else
    status skip "$pkg already installed"
  fi
done

if [ "${#apt_targets[@]}" -gt 0 ]; then
  run sudo apt-get update
  if should_reinstall_tools; then
    run sudo apt-get install -y --reinstall "${apt_targets[@]}"
  else
    run sudo apt-get install -y "${apt_targets[@]}"
  fi
fi

log "github release installs"
run mkdir -p "$HOME/.local/bin" "$HOME/.local/opt"

for entry in "${GITHUB_INSTALLS[@]}"; do
  IFS='|' read -r cmd method url extra <<< "$entry"
  file="$(basename "$url")"

  case "$method" in
    deb)
      if should_reinstall_tools || ! command_exists "$cmd"; then
        sublog "$cmd"
        if is_dry_run; then
          status get "$url"
          status plan "sudo dpkg -i $file"
        else
          make_temp_dir "setup-tools-${cmd}" tmp_dir
          status get "$url"
          curl -L -o "$tmp_dir/$file" "$url"
          sudo dpkg -i "$tmp_dir/$file"
        fi
      else
        status skip "$cmd already installed"
      fi
      ;;

    tarball)
      if should_reinstall_tools || ! command_exists "$cmd"; then
        sublog "$cmd"
        if is_dry_run; then
          status get "$url"
          status unpack "~/.local/opt/$extra"
          status link "~/.local/bin/$cmd -> ~/.local/opt/$extra/bin/$cmd"
        else
          make_temp_dir "setup-tools-${cmd}" tmp_dir
          status get "$url"
          curl -L -o "$tmp_dir/$file" "$url"
          if should_reinstall_tools && [ -e "$HOME/.local/opt/$extra" ]; then
            run rm -rf "$HOME/.local/opt/$extra"
          fi
          tar -C "$HOME/.local/opt" -xzf "$tmp_dir/$file"
          status link "$HOME/.local/bin/$cmd -> $HOME/.local/opt/$extra/bin/$cmd"
          ln -sf "$HOME/.local/opt/$extra/bin/$cmd" "$HOME/.local/bin/$cmd"
        fi
      else
        status skip "$cmd already installed"
      fi
      ;;

    bin)
      if should_reinstall_tools || ! command_exists "$cmd"; then
        sublog "$cmd"
        depth="$(echo "$extra" | tr -cd '/' | wc -c)"
        if is_dry_run; then
          status get "$url"
          status unpack "~/.local/bin/$cmd"
        else
          make_temp_dir "setup-tools-${cmd}" tmp_dir
          status get "$url"
          curl -L -o "$tmp_dir/$file" "$url"
          tar -C "$HOME/.local/bin" --strip-components="$depth" -xzf "$tmp_dir/$file" "$extra"
          chmod +x "$HOME/.local/bin/$cmd"
        fi
      else
        status skip "$cmd already installed"
      fi
      ;;

    direct)
      if should_reinstall_tools || ! command_exists "$cmd"; then
        sublog "$cmd"
        if is_dry_run; then
          status get "$url"
          status install "~/.local/bin/$cmd"
        else
          make_temp_dir "setup-tools-${cmd}" tmp_dir
          status get "$url"
          curl -L -o "$tmp_dir/$file" "$url"
          mv "$tmp_dir/$file" "$HOME/.local/bin/$cmd"
          chmod +x "$HOME/.local/bin/$cmd"
        fi
      else
        status skip "$cmd already installed"
      fi
      ;;
  esac
done

## [snap packages]
# Add package entries here. snap handles install and updates.
# Format: "pkg" or "pkg|flags"
# Skipped when: snap list <pkg> already succeeds.
SNAP_PACKAGES=(
  difftastic
  "aws-cli|--classic"
)

log "snap packages"
for entry in "${SNAP_PACKAGES[@]}"; do
  IFS='|' read -r pkg flags <<< "$entry"
  if should_reinstall_tools || ! snap list "$pkg" >/dev/null 2>&1; then
    sublog "$pkg"
    snap_args=("$pkg")
    if [ -n "${flags:-}" ]; then
      read -r -a snap_flags <<< "$flags"
      snap_args+=("${snap_flags[@]}")
    fi
    if should_reinstall_tools && snap list "$pkg" >/dev/null 2>&1; then
      install_cmd="$(command_string sudo snap refresh "$pkg")"
      snap_command=(sudo snap refresh "$pkg")
    else
      install_cmd="$(command_string sudo snap install "${snap_args[@]}")"
      snap_command=(sudo snap install "${snap_args[@]}")
    fi
    if is_dry_run; then
      status plan "$install_cmd"
    else
      status run "$install_cmd"
      "${snap_command[@]}"
    fi
  else
    status skip "$pkg already installed"
  fi
done

## [installer scripts]
# Tools installed via their own installer scripts.
#
#   "cmd|url"                    — installer runs with sh and adds cmd to PATH
#   "cmd|url|dest"               — installer runs with bash, drops the binary in CWD,
#                                  and moves it to dest (e.g. getmic.ro)
#   "cmd|url||shell"             — installer runs with the named shell and adds cmd
#                                  to PATH
#   "cmd|url||shell|shell_args"  — installer runs with the named shell and args
#
# Skipped when: command -v <cmd> succeeds.
INSTALLER_TOOLS=(
  "zoxide|https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh"
  "uv|https://astral.sh/uv/install.sh"
  "fnm|https://fnm.vercel.app/install||bash|-s -- --skip-shell --install-dir \"$HOME/.fnm\""
  "micro|https://getmic.ro|/usr/bin/micro"
  "copilot|https://gh.io/copilot-install||bash"
)

log "installer scripts"
for entry in "${INSTALLER_TOOLS[@]}"; do
  IFS='|' read -r cmd url dest shell shell_args <<< "$entry"
  shell="${shell:-sh}"
  if should_reinstall_tools || ! command_exists "$cmd"; then
    sublog "$cmd"
    if [ -n "${dest:-}" ]; then
      if is_dry_run; then
        status plan "(cd \"\$(mktemp -d)\" && curl $url | bash && sudo mv $cmd $dest)"
      else
        make_temp_dir "setup-tools-${cmd}" tmp_dir
        status run "(cd $(printf '%q' "$tmp_dir") && curl $url | bash && sudo mv $cmd $dest)"
        (cd "$tmp_dir" && curl "$url" | bash && sudo mv "$cmd" "$dest")
      fi
    else
      if [ -n "${shell_args:-}" ]; then
        run_sh "curl -fsSL $url | $shell $shell_args"
      else
        run_sh "curl -sSfL $url | $shell"
      fi
    fi
  else
    status skip "$cmd already installed"
  fi
done

## [fzf]
# Installed via git clone + bundled install script (not a pipe-to-sh installer).
if should_reinstall_tools; then
  if [ -d "$HOME/.fzf/.git" ]; then
    run git -C "$HOME/.fzf" pull --ff-only
  else
    clone_if_missing "$HOME/.fzf" --depth 1 https://github.com/junegunn/fzf.git
  fi
  run_sh "$HOME/.fzf/install --all --no-update-rc"
elif command_exists fzf; then
  status skip "fzf already installed"
else
  clone_if_missing "$HOME/.fzf" --depth 1 https://github.com/junegunn/fzf.git
  if [ ! -f "$HOME/.fzf.bash" ]; then
    run_sh "$HOME/.fzf/install --all --no-update-rc"
  fi
fi
