# fnm

Fast Node Manager. Installs and switches Node.js versions.

`scripts/setup-stow.sh` creates `~/.fnm/`; `scripts/setup-tools.sh` installs the
fnm binary there with its official installer. Bash initialization is stow-tracked.

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
