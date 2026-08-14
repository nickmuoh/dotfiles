# Tool installation

Register every new tool in `scripts/setup-tools.sh` so new machines receive it:

- apt packages use `APT_PACKAGES`.
- GitHub release artifacts use `GITHUB_INSTALLS`.
- snap packages use `SNAP_PACKAGES`.
- Installer scripts use `INSTALLER_TOOLS`.
- Git clones and generated plugin content belong in `bootstrap.sh`.

Install single binaries and `.pyz` files in `~/.local/bin/`. Extract tarballs to `~/.local/opt/<name>/` and link their binary from `~/.local/bin/`.

After changing the tool setup, run `./bootstrap.sh --dry-run`.
