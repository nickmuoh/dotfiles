#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/lib.sh"

# ── apt packages ─────────────────────────────────────────────────────────────
# Add or remove package names here. apt handles install and future upgrades.
APT_PACKAGES=(
  bash-completion curl git fzf bat jq yq tmux starship gh stow
  lazygit universal-ctags
)

# ── github release versions ──────────────────────────────────────────────────
# Update the version variable here when upgrading a tool.
# nvim uses the /latest/ GitHub redirect and does not need a pinned version.
RG_VERSION="14.1.1"
PANDOC_VERSION="3.10"
KEYCHAIN_VERSION="3.0.0_beta1"

# ── github release installs ──────────────────────────────────────────────────
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

# ── install ───────────────────────────────────────────────────────────────────

log "apt packages"
run sudo apt-get update
run sudo apt-get install -y "${APT_PACKAGES[@]}"

log "github release installs"
run mkdir -p "$HOME/.local/bin" "$HOME/.local/opt"

for entry in "${GITHUB_INSTALLS[@]}"; do
  IFS='|' read -r cmd method url extra <<< "$entry"
  file="$(basename "$url")"

  case "$method" in
    deb)
      if ! command -v "$cmd" >/dev/null 2>&1; then
        log "$cmd"
        if is_dry_run; then
          printf '+ curl -LO %s\n' "$url"
          printf '+ sudo dpkg -i %s\n' "$file"
        else
          (cd /tmp && curl -LO "$url" && sudo dpkg -i "$file" && rm "$file")
        fi
      fi
      ;;

    tarball)
      if [ ! -e "$HOME/.local/opt/$extra" ]; then
        log "$cmd"
        if is_dry_run; then
          printf '+ curl -LO %s\n' "$url"
          printf '+ tar -C ~/.local/opt -xzf %s\n' "$file"
          printf '+ ln -sf ~/.local/opt/%s/bin/%s ~/.local/bin/%s\n' "$extra" "$cmd" "$cmd"
        else
          (cd /tmp && curl -LO "$url" && tar -C "$HOME/.local/opt" -xzf "$file" && rm "$file")
          ln -sf "$HOME/.local/opt/$extra/bin/$cmd" "$HOME/.local/bin/$cmd"
        fi
      fi
      ;;

    bin)
      if [ ! -f "$HOME/.local/bin/$cmd" ]; then
        log "$cmd"
        depth="$(echo "$extra" | tr -cd '/' | wc -c)"
        if is_dry_run; then
          printf '+ curl -LO %s\n' "$url"
          printf '+ tar -C ~/.local/bin --strip-components=%s -xzf %s %s\n' "$depth" "$file" "$extra"
        else
          (
            cd /tmp
            curl -LO "$url"
            tar -C "$HOME/.local/bin" --strip-components="$depth" -xzf "$file" "$extra"
            chmod +x "$HOME/.local/bin/$cmd"
            rm "$file"
          )
        fi
      fi
      ;;

    direct)
      if ! command -v "$cmd" >/dev/null 2>&1; then
        log "$cmd"
        if is_dry_run; then
          printf '+ curl -LO %s\n' "$url"
          printf '+ mv /tmp/%s ~/.local/bin/%s && chmod +x ~/.local/bin/%s\n' "$file" "$cmd" "$cmd"
        else
          (cd /tmp && curl -LO "$url" && mv "$file" "$HOME/.local/bin/$cmd" && chmod +x "$HOME/.local/bin/$cmd")
        fi
      fi
      ;;
  esac
done

# ── snap packages ─────────────────────────────────────────────────────────────
# Add package names here. snap handles install and updates.
# Skipped when: snap list <pkg> already succeeds.
SNAP_PACKAGES=(
  difftastic
)

log "snap packages"
for pkg in "${SNAP_PACKAGES[@]}"; do
  if ! snap list "$pkg" >/dev/null 2>&1; then
    log "$pkg"
    if is_dry_run; then
      printf '+ sudo snap install %s\n' "$pkg"
    else
      sudo snap install "$pkg"
    fi
  fi
done

# ── installer scripts ─────────────────────────────────────────────────────────
# Tools installed via their own installer scripts.
#
#   "cmd|url"       — installer runs itself to completion and adds cmd to PATH
#   "cmd|url|dest"  — installer drops the binary in CWD; it is then moved to dest
#                     (used when the installer doesn't self-install, e.g. getmic.ro)
#
# Skipped when: command -v <cmd> succeeds.
INSTALLER_TOOLS=(
  "zoxide|https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh"
  "uv|https://astral.sh/uv/install.sh"
  "micro|https://getmic.ro|/usr/bin/micro"
  "gh-copilot|https://gh.io/copilot-install"
)

log "installer scripts"
for entry in "${INSTALLER_TOOLS[@]}"; do
  IFS='|' read -r cmd url dest <<< "$entry"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    log "$cmd"
    if [ -n "${dest:-}" ]; then
      if is_dry_run; then
        printf '+ (cd /tmp && curl %s | bash && sudo mv %s %s)\n' "$url" "$cmd" "$dest"
      else
        (cd /tmp && curl "$url" | bash && sudo mv "$cmd" "$dest")
      fi
    else
      run_sh "curl -sSfL $url | sh"
    fi
  fi
done

# ── fzf ───────────────────────────────────────────────────────────────────────
# Installed via git clone + bundled install script (not a pipe-to-sh installer).
clone_if_missing "$HOME/.fzf" --depth 1 https://github.com/junegunn/fzf.git
if [ ! -f "$HOME/.fzf.bash" ]; then
  run_sh "$HOME/.fzf/install --all --no-update-rc"
fi
