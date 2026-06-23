# fnm

Fast Node Manager. Installs and switches Node.js versions.

## Install

Installed by `scripts/setup-tools.sh` with the official installer:

- Source: `Schniz/fnm` GitHub repository
- Installer: `https://fnm.vercel.app/install`
- Command: `curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell`
- Dependencies: `curl`, `unzip`
- Shell mutation: disabled with `--skip-shell`; Bash initialization is stow-tracked

## Important configuration paths

- `~/.bashrc` — shell startup eval block
- `~/.local/share/fnm/` — default fnm install and Node version storage

## Current state

Bash initializes fnm when it is on `PATH`:

```sh
eval "$(fnm env --use-on-cd --shell bash)"
```

## Postinstall commands

`scripts/setup-postinstall.sh` prints these follow-up commands when `fnm` is
available:

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
