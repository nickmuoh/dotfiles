# GitHub CLI setup

## Important configuration paths

- `~/.bashrc`
- `~/.bash_aliases`
- `~/.config/gh/` if you later authenticate or add CLI config

## Installed state

- `scripts/setup-tools.sh` installs `gh`, which is available on `PATH`.
- Browser opening support comes from `gh-browser` in `~/.local/bin`

## Current state

- There is no `gh`-specific shell init in `~/.bashrc` or `~/.bash_aliases`
- `~/.config/gh/` holds user-level GitHub CLI configuration after authentication
- `gh auth login` relies on the shell's `BROWSER` setting, which is exported from `~/.bashrc` when `gh-browser` is available

## Caveats

- Authentication state and CLI preferences appear after commands such as `gh auth login`.
- Shell completions or aliases for `gh` are not currently configured in the documented Bash setup; browser launching is handled by `gh-browser`
