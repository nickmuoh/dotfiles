# shell_setup agent guide

## Doc sync

After any change, update the corresponding docs before completing the task:

- Change a tool's config or plugins → update `<package>/README.md` for that tool
- Change a tool's shell-level behavior → update `docs/<tool>.md` if that file exists
- Add or remove a stow package → update the package index in `README.md`
- Add a new tool or plugin → document it in the relevant `<package>/README.md` with repo URL, install command, and any extra dependencies

## Installing tools

When asked to install a tool:

1. Install it using the appropriate method.
2. Register it in `scripts/setup-tools.sh` so it installs on new machines:
   - apt package → `APT_PACKAGES`
   - GitHub release artifact → `GITHUB_INSTALLS` (format: `"cmd|method|url"` or `"cmd|method|url|extra"`; methods: `deb`, `tarball`, `bin`, `direct`)
   - snap package → `SNAP_PACKAGES`
   - tool with its own installer script → `INSTALLER_TOOLS` (format: `"cmd|url"` or `"cmd|url|dest"`)
   - git clone or plugin content → add to `bootstrap.sh` instead
3. Install location conventions:
   - Single binaries and `.pyz` files → `~/.local/bin/`
   - Tarballs → extract to `~/.local/opt/<name>/`, symlink binary at `~/.local/bin/<name>`

## Stow packages

Config files are managed as GNU Stow packages. Each package directory in the repo root mirrors its target path under `$HOME`.

- To add a config file: place it in the correct package subdirectory, then stow the package.
- Dry-run first: `stow -nv <package>`
- Deploy: `stow -v <package>`

## Bootstrap

`bootstrap.sh` manages generated and plugin content that cannot be stowed: TPM and tmux plugins, the fzf git clone, Micro plugin repos, and the Treemux Python venv.

- Add git-cloned or generated content to `bootstrap.sh`, not to a stow package.
- Preview before applying: `./bootstrap.sh --dry-run`

## Tmux safety

- Never run `tmux kill-server` from inside a running session — it interrupts the current shell context.
- To apply config changes: `tmux source-file ~/.tmux.conf`
- To check if you are inside a session: `echo $TMUX` — non-empty means yes.

## Doc style

- Write factual, current state only — no theory, no plans, no opinions.
- One doc per tool.
- Use inline code for all paths, commands, and key names.
- Do not create planning or scratch-pad files in this repo.
