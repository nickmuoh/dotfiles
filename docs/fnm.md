# fnm

Fast Node Manager. Installs and switches Node.js versions.

## Install

- Directory structure: created by the `fnm` stow package (`scripts/setup-stow.sh`)
- Binary: installed by `scripts/setup-tools.sh` with the official installer:
  - Source: `Schniz/fnm` GitHub repository
  - Installer: `https://fnm.vercel.app/install`
  - Command: `curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell --install-dir "$HOME/.fnm"`
  - Dependencies: `curl`, `unzip`
  - Shell mutation: disabled with `--skip-shell`; Bash initialization is stow-tracked

## Important configuration paths

- `~/.bashrc` — shell startup eval block
- `~/.fnm/` — fnm binary and Node version storage (created by stow, populated by installer)

## Current state

Bash adds `~/.fnm` to `PATH` before initialization.

When `fnm` is available, Bash initializes it with:

```sh
eval "$(fnm env --use-on-cd --shell bash)"
```

## Postinstall commands

`scripts/setup-postinstall.sh` prints these follow-up commands when `fnm` is
available, and marks them `done` when they are already satisfied:

```sh
fnm install --lts
fnm default lts-latest
node --version
npm --version
```

## Key commands

```sh
fnm install --lts        # install the latest Node.js LTS release
fnm default lts-latest   # set the latest LTS alias as the default version
fnm list                 # list installed Node.js versions
fnm current              # show the active Node.js version
```
