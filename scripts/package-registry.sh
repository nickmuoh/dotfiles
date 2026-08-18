#!/usr/bin/env bash
# Authoritative bootstrap unit registry.
#
# This file deliberately uses only Bash. It is sourced before bootstrap can assume
# jq, yq, Python, or any other optional parser is installed.
#
# REGISTRY_UNIT_IDS is the only enumeration list. Each ID has one self-contained
# case stanza in registry_load_unit. The loader resets every field first, so a
# stanza only assigns fields that apply to that unit.
#
# Field semantics:
#   REGISTRY_ID                  canonical --package ID
#   REGISTRY_ALIASES             accepted alternate --package IDs
#   REGISTRY_INSTALL_METHOD      apt, github, snap, installer, or empty
#   REGISTRY_INSTALL_NAMES       apt distribution package names
#   REGISTRY_COMMAND             installed command used for idempotence
#   REGISTRY_DOWNLOAD_METHOD     setup-tools GitHub method
#   REGISTRY_URL                 release API, artifact, or installer URL
#   REGISTRY_DOWNLOAD_DETAIL     archive member/root or latest asset prefix
#   REGISTRY_INSTALL_DESTINATION installer-specific destination path
#   REGISTRY_INSTALL_SHELL       shell used by an installer
#   REGISTRY_INSTALL_ARGS        installer or Snap arguments
#   REGISTRY_STOW_PACKAGE        repository directory owned by GNU Stow
#   REGISTRY_STOW_ARGS           package-specific GNU Stow arguments
#   REGISTRY_SETUP_HOOK          setup phase selected by registry_hook_selected

REGISTRY_UNIT_IDS=(
  __core__
  bash
  bash-completion
  git
  curl
  bat
  jq
  yq
  fzf
  fd
  tmux
  starship
  gh
  stow
  universal-ctags
  unzip
  socat
  psmisc
  libpq-dev
  libsqlite3-dev
  python3-dev
  gcc
  gnome-keyring
  libsecret-1-0
  xdg-utils
  rg
  nvim
  pandoc
  npiperelay
  keychain
  lazygit
  difftastic
  aws-cli
  zoxide
  uv
  fnm
  micro
  copilot
  claude
  snowflake
  ollama
  1password
  treemux
  tmux-cpu-mem-monitor
  local-bin
  pi
)

registry_reset_unit() {
  REGISTRY_ID=
  REGISTRY_ALIASES=()
  REGISTRY_INSTALL_METHOD=
  REGISTRY_INSTALL_NAMES=()
  REGISTRY_COMMAND=
  REGISTRY_DOWNLOAD_METHOD=
  REGISTRY_URL=
  REGISTRY_DOWNLOAD_DETAIL=
  REGISTRY_INSTALL_DESTINATION=
  REGISTRY_INSTALL_SHELL=
  REGISTRY_INSTALL_ARGS=()
  REGISTRY_STOW_PACKAGE=
  REGISTRY_STOW_ARGS=()
  REGISTRY_SETUP_HOOK=
}

registry_load_unit() {
  local canonical_id=${1:-}
  registry_reset_unit

  case "$canonical_id" in
    __core__)
      REGISTRY_ID=__core__
      REGISTRY_ALIASES=(core)
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(
        bash-completion curl git fd-find fzf bat jq yq tmux starship gh stow
        universal-ctags unzip socat psmisc libpq-dev libsqlite3-dev python3-dev
        gcc gnome-keyring libsecret-1-0 xdg-utils
      )
      ;;

    # Stow-only unit: no installer metadata is needed.
    bash)
      REGISTRY_ID=bash
      REGISTRY_ALIASES=(shell)
      REGISTRY_STOW_PACKAGE=bash
      ;;

    bash-completion)
      REGISTRY_ID=bash-completion
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(bash-completion)
      REGISTRY_STOW_PACKAGE=bash-completions
      ;;

    git)
      REGISTRY_ID=git
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(git)
      REGISTRY_STOW_PACKAGE=git
      ;;

    curl)
      REGISTRY_ID=curl
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(curl)
      ;;

    bat)
      REGISTRY_ID=bat
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(bat)
      ;;

    # Apt-only unit: canonical ID, distribution package, and no Stow ownership.
    jq)
      REGISTRY_ID=jq
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(jq)
      ;;

    yq)
      REGISTRY_ID=yq
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(yq)
      ;;

    fzf)
      REGISTRY_ID=fzf
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(fzf)
      REGISTRY_STOW_PACKAGE=fzf
      REGISTRY_SETUP_HOOK=setup-tools:fzf
      ;;

    fd)
      REGISTRY_ID=fd
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(fd-find)
      REGISTRY_SETUP_HOOK=setup-tools:fd
      ;;

    tmux)
      REGISTRY_ID=tmux
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(tmux)
      REGISTRY_STOW_PACKAGE=tmux
      ;;

    starship)
      REGISTRY_ID=starship
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(starship)
      REGISTRY_STOW_PACKAGE=starship
      ;;

    gh)
      REGISTRY_ID=gh
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(gh)
      ;;

    stow)
      REGISTRY_ID=stow
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(stow)
      ;;

    universal-ctags)
      REGISTRY_ID=universal-ctags
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(universal-ctags)
      ;;

    unzip)
      REGISTRY_ID=unzip
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(unzip)
      ;;

    socat)
      REGISTRY_ID=socat
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(socat)
      ;;

    psmisc)
      REGISTRY_ID=psmisc
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(psmisc)
      ;;

    libpq-dev)
      REGISTRY_ID=libpq-dev
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(libpq-dev)
      ;;

    libsqlite3-dev)
      REGISTRY_ID=libsqlite3-dev
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(libsqlite3-dev)
      ;;

    python3-dev)
      REGISTRY_ID=python3-dev
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(python3-dev)
      ;;

    gcc)
      REGISTRY_ID=gcc
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(gcc)
      ;;

    gnome-keyring)
      REGISTRY_ID=gnome-keyring
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(gnome-keyring)
      ;;

    libsecret-1-0)
      REGISTRY_ID=libsecret-1-0
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(libsecret-1-0)
      ;;

    xdg-utils)
      REGISTRY_ID=xdg-utils
      REGISTRY_INSTALL_METHOD=apt
      REGISTRY_INSTALL_NAMES=(xdg-utils)
      ;;

    rg)
      REGISTRY_ID=rg
      REGISTRY_ALIASES=(ripgrep)
      REGISTRY_INSTALL_METHOD=github
      REGISTRY_COMMAND=rg
      REGISTRY_DOWNLOAD_METHOD=deb
      REGISTRY_URL=https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/ripgrep_14.1.1-1_amd64.deb
      ;;

    nvim)
      REGISTRY_ID=nvim
      REGISTRY_ALIASES=(neovim)
      REGISTRY_INSTALL_METHOD=github
      REGISTRY_COMMAND=nvim
      REGISTRY_DOWNLOAD_METHOD=tarball
      REGISTRY_URL=https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz
      REGISTRY_DOWNLOAD_DETAIL=nvim-linux-x86_64
      REGISTRY_STOW_PACKAGE=nvim
      ;;

    pandoc)
      REGISTRY_ID=pandoc
      REGISTRY_INSTALL_METHOD=github
      REGISTRY_COMMAND=pandoc
      REGISTRY_DOWNLOAD_METHOD=bin
      REGISTRY_URL=https://github.com/jgm/pandoc/releases/download/3.10/pandoc-3.10-linux-amd64.tar.gz
      REGISTRY_DOWNLOAD_DETAIL=pandoc-3.10/bin/pandoc
      ;;

    # Canonical ID differs from the Windows executable/distribution artifact.
    npiperelay)
      REGISTRY_ID=npiperelay
      REGISTRY_ALIASES=(npiperelay.exe)
      REGISTRY_INSTALL_METHOD=github
      REGISTRY_COMMAND=npiperelay.exe
      REGISTRY_DOWNLOAD_METHOD=zipbin
      REGISTRY_URL=https://github.com/jstarks/npiperelay/releases/download/v0.1.0/npiperelay_windows_amd64.zip
      REGISTRY_DOWNLOAD_DETAIL=npiperelay.exe
      ;;

    keychain)
      REGISTRY_ID=keychain
      REGISTRY_INSTALL_METHOD=github
      REGISTRY_COMMAND=keychain
      REGISTRY_DOWNLOAD_METHOD=direct
      REGISTRY_URL=https://github.com/danielrobbins/keychain/releases/download/3.0.0_beta1/keychain-3.0.0_beta1.pyz
      ;;

    lazygit)
      REGISTRY_ID=lazygit
      REGISTRY_INSTALL_METHOD=github
      REGISTRY_COMMAND=lazygit
      REGISTRY_DOWNLOAD_METHOD=latest-bin
      REGISTRY_URL=https://api.github.com/repos/jesseduffield/lazygit/releases/latest
      REGISTRY_DOWNLOAD_DETAIL=lazygit
      REGISTRY_STOW_PACKAGE=lazygit
      ;;

    difftastic)
      REGISTRY_ID=difftastic
      REGISTRY_INSTALL_METHOD=snap
      REGISTRY_INSTALL_NAMES=(difftastic)
      ;;

    aws-cli)
      REGISTRY_ID=aws-cli
      REGISTRY_ALIASES=(aws)
      REGISTRY_INSTALL_METHOD=snap
      REGISTRY_INSTALL_NAMES=(aws-cli)
      REGISTRY_INSTALL_ARGS=(--classic)
      ;;

    zoxide)
      REGISTRY_ID=zoxide
      REGISTRY_INSTALL_METHOD=installer
      REGISTRY_COMMAND=zoxide
      REGISTRY_URL=https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh
      ;;

    uv)
      REGISTRY_ID=uv
      REGISTRY_INSTALL_METHOD=installer
      REGISTRY_COMMAND=uv
      REGISTRY_URL=https://astral.sh/uv/install.sh
      ;;

    fnm)
      REGISTRY_ID=fnm
      REGISTRY_INSTALL_METHOD=installer
      REGISTRY_COMMAND=fnm
      REGISTRY_URL=https://fnm.vercel.app/install
      REGISTRY_INSTALL_SHELL=bash
      REGISTRY_INSTALL_ARGS=(-s -- --skip-shell --install-dir "$HOME/.fnm")
      REGISTRY_STOW_PACKAGE=fnm
      ;;

    micro)
      REGISTRY_ID=micro
      REGISTRY_INSTALL_METHOD=installer
      REGISTRY_COMMAND=micro
      REGISTRY_URL=https://getmic.ro
      REGISTRY_INSTALL_DESTINATION=/usr/bin/micro
      REGISTRY_INSTALL_SHELL=sh
      REGISTRY_STOW_PACKAGE=micro
      ;;

    copilot)
      REGISTRY_ID=copilot
      REGISTRY_INSTALL_METHOD=installer
      REGISTRY_COMMAND=copilot
      REGISTRY_URL=https://gh.io/copilot-install
      REGISTRY_INSTALL_SHELL=bash
      REGISTRY_STOW_PACKAGE=copilot
      ;;

    claude)
      REGISTRY_ID=claude
      REGISTRY_INSTALL_METHOD=installer
      REGISTRY_COMMAND=claude
      REGISTRY_URL=https://claude.ai/install.sh
      REGISTRY_INSTALL_SHELL=bash
      REGISTRY_STOW_PACKAGE=claude
      ;;

    snowflake)
      REGISTRY_ID=snowflake
      REGISTRY_ALIASES=(cortex)
      REGISTRY_INSTALL_METHOD=installer
      REGISTRY_COMMAND=cortex
      REGISTRY_URL=https://ai.snowflake.com/static/cc-scripts/install.sh
      REGISTRY_INSTALL_SHELL=sh
      REGISTRY_STOW_PACKAGE=snowflake
      ;;

    # Installer plus Stow ownership, with a package-specific Stow option.
    ollama)
      REGISTRY_ID=ollama
      REGISTRY_INSTALL_METHOD=installer
      REGISTRY_COMMAND=ollama
      REGISTRY_URL=https://ollama.com/install.sh
      REGISTRY_INSTALL_SHELL=sh
      REGISTRY_STOW_PACKAGE=ollama
      REGISTRY_STOW_ARGS=(--no-folding)
      ;;

    1password)
      REGISTRY_ID=1password
      REGISTRY_STOW_PACKAGE=1password
      ;;

    treemux)
      REGISTRY_ID=treemux
      REGISTRY_STOW_PACKAGE=treemux
      ;;

    tmux-cpu-mem-monitor)
      REGISTRY_ID=tmux-cpu-mem-monitor
      REGISTRY_STOW_PACKAGE=tmux-cpu-mem-monitor
      ;;

    local-bin)
      REGISTRY_ID=local-bin
      REGISTRY_STOW_PACKAGE=local-bin
      ;;

    pi)
      REGISTRY_ID=pi
      REGISTRY_STOW_PACKAGE=pi
      REGISTRY_SETUP_HOOK=setup-pi
      ;;

    *)
      printf 'unknown canonical registry unit: %s\n' "$canonical_id" >&2
      return 1
      ;;
  esac
}

registry_canonical_ids() {
  printf '%s\n' "${REGISTRY_UNIT_IDS[@]}"
}

registry_resolve() {
  local wanted=$1
  local canonical_id alias

  for canonical_id in "${REGISTRY_UNIT_IDS[@]}"; do
    registry_load_unit "$canonical_id" || return
    if [[ "$wanted" == "$REGISTRY_ID" ]]; then
      printf '%s\n' "$REGISTRY_ID"
      return 0
    fi
    for alias in "${REGISTRY_ALIASES[@]}"; do
      if [[ "$wanted" == "$alias" ]]; then
        printf '%s\n' "$REGISTRY_ID"
        return 0
      fi
    done
  done
  return 1
}

registry_validate() {
  local requested
  for requested in "$@"; do
    if ! registry_resolve "$requested" >/dev/null; then
      printf 'unknown bootstrap package: %s\n' "$requested" >&2
      return 1
    fi
  done
}

registry_selected_ids() {
  local requested
  if [[ -z "${BOOTSTRAP_PACKAGES:-}" ]]; then
    registry_canonical_ids
    return
  fi
  for requested in ${BOOTSTRAP_PACKAGES}; do
    registry_resolve "$requested"
  done
}

registry_package_selected() {
  local candidate resolved selected
  [[ -z "${BOOTSTRAP_PACKAGES:-}" ]] && return 0
  resolved=$(registry_resolve "$1") || return 1
  while read -r selected; do
    [[ "$resolved" == "$selected" ]] && return 0
  done < <(registry_selected_ids)
  return 1
}

# Output format is an internal setup-stow interface: stow-package|stow-args.
registry_stow_packages() {
  local canonical_id
  while read -r canonical_id; do
    registry_load_unit "$canonical_id" || return
    [[ -n "$REGISTRY_STOW_PACKAGE" ]] || continue
    printf '%s|%s\n' "$REGISTRY_STOW_PACKAGE" "${REGISTRY_STOW_ARGS[*]}"
  done < <(registry_selected_ids)
}

# Output format is used by validation: canonical-id|stow-package|stow-args.
registry_all_stow_packages() {
  local canonical_id
  for canonical_id in "${REGISTRY_UNIT_IDS[@]}"; do
    registry_load_unit "$canonical_id" || return
    [[ -n "$REGISTRY_STOW_PACKAGE" ]] || continue
    printf '%s|%s|%s\n' "$REGISTRY_ID" "$REGISTRY_STOW_PACKAGE" "${REGISTRY_STOW_ARGS[*]}"
  done
}

registry_install_records() {
  local canonical_id
  while read -r canonical_id; do
    registry_load_unit "$canonical_id" || return
    [[ -n "$REGISTRY_INSTALL_METHOD" ]] || continue
    printf '%s|%s|%s\n' "$REGISTRY_ID" "$REGISTRY_INSTALL_METHOD" "${REGISTRY_INSTALL_NAMES[*]:-$REGISTRY_COMMAND}"
  done < <(registry_selected_ids)
}

registry_setup_hook() {
  local canonical_id
  canonical_id=$(registry_resolve "$1") || return 1
  registry_load_unit "$canonical_id" || return
  [[ -n "$REGISTRY_SETUP_HOOK" ]] && printf '%s\n' "$REGISTRY_SETUP_HOOK"
}

# Return success when the named setup hook belongs to a selected registry unit.
registry_hook_selected() {
  local wanted_hook=$1 canonical_id
  while read -r canonical_id; do
    registry_load_unit "$canonical_id" || return
    [[ "$REGISTRY_SETUP_HOOK" == "$wanted_hook" ]] && return 0
  done < <(registry_selected_ids)
  return 1
}

registry_stow_args() {
  local canonical_id
  canonical_id=$(registry_resolve "$1") || return 1
  registry_load_unit "$canonical_id" || return
  [[ -n "$REGISTRY_STOW_PACKAGE" ]] || return 1
  printf '%s\n' "${REGISTRY_STOW_ARGS[*]}"
}
