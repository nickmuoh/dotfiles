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

## Bootstrap logging

Bootstrap scripts source `scripts/lib.sh` and use Homebrew-inspired structured logs.

- Use `log "section"` for top-level `==>` sections.
- Use `sublog "name"` for nested tool/plugin names under a section.
- Use `status <label> "message"` for indented status lines. Existing labels include `plan`, `run`, `skip`, `get`, `unpack`, `link`, `install`, `plug`, `todo`, `done`, and `error`.
- Use `run <cmd> ...` for ordinary commands so dry runs print `plan` and real runs print `run`.
- Use `run_sh "command string"` only for shell pipelines or compound shell snippets.
- Use `clone_if_missing <dest> ...` for idempotent git clones.
- Do not print bootstrap actions with ad hoc `printf '+ ...'` or plain `echo`; route new output through `log`, `sublog`, `status`, `run`, or `run_sh`.
- Keep color behavior centralized in `scripts/lib.sh`. Colors are enabled only for interactive terminals and can be disabled with `NO_COLOR=1`.

## Bootstrap error handling

Bootstrap and setup scripts use `set -euo pipefail` plus shared traps from `scripts/lib.sh`.

- After sourcing `scripts/lib.sh`, call `enable_error_trap` in setup scripts so failures print a structured `error` line and managed temp directories are cleaned up.
- Use `make_temp_dir <prefix> <var_name>` for temporary download or build directories instead of ad hoc `/tmp` work. The shared `EXIT` trap removes registered temp directories.
- If a script needs a local trap, preserve the shared cleanup and error-reporting behavior instead of replacing it silently.
- Keep expected failures inside explicit conditionals such as `if ! command -v tool ...; then`; use `|| true` only when failure is intentionally acceptable.

## Tmux safety

- Never run `tmux kill-server` from inside a running session — it interrupts the current shell context.
- To apply config changes: `tmux source-file ~/.tmux.conf`
- To check if you are inside a session: `echo $TMUX` — non-empty means yes.

## Doc style

- Write factual, current state only — no theory, no plans, no opinions.
- One doc per tool.
- Use inline code for all paths, commands, and key names.
- Do not create planning or scratch-pad files in this repo.
