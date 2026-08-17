# Bash

The `bash` package manages `~/.bashrc` and `~/.bash_aliases`.

## Current configuration

- Interactive Bash uses `LANG=C.UTF-8`, enables completion when system files are present, and prepends `~/.local/bin` to `PATH`.
- `MICRO_TRUECOLOR=1` is exported.
- `~/.bash_aliases` defines `bat`, `bathelp`, and a `help()` function that formats command help with `batcat`.
- `claude-usage` runs the current Claude usage tracker; tracker options such as `--today`, `--month current`, and `--budget` are passed through to the script.
- Starship, fzf, zoxide, and fnm initialize only when their commands or startup files are available.
- `gh-browser` supplies the `BROWSER` command used by `gh auth login`.
- The keychain startup block is disabled; SSH authentication uses the 1Password WSL bridge.

See [`starship.md`](starship.md), [`fzf.md`](fzf.md), [`fnm.md`](fnm.md), [`zoxide.md`](zoxide.md), [`gh.md`](gh.md), [`bat.md`](bat.md), and [`1password.md`](1password.md) for tool-specific details.
