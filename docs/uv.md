# uv

Python package and runtime manager.

## Install

Installed by `scripts/setup-tools.sh` with the official installer:

- Source: `astral-sh/uv` installer
- Installer: `https://astral.sh/uv/install.sh`
- Command: `curl -sSfL https://astral.sh/uv/install.sh | sh`
- Binary: `~/.local/bin/uv`

## Important configuration paths

- `~/.local/bin/uv` — uv binary installed by bootstrap
- `~/.local/share/uv/python/` — uv-managed Python installations

## Managed Python

`scripts/setup-postinstall.sh` prints this follow-up command when `uv` is
available, and marks it `done` when the Python is already installed:

```sh
uv python install 3.12
python3.12 --version
```

The `3.12` request lets uv install the latest available Python 3.12 patch for
the current uv release metadata instead of pinning a patch version in this repo.

## Key commands

```sh
uv python list          # list available and installed Python versions
uv python install 3.12  # install the latest available Python 3.12 patch
uv python dir           # show uv's managed Python install directory
uv python find 3.12     # show the resolved Python 3.12 executable
```
