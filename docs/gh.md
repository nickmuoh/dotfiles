# GitHub CLI setup

## Important configuration paths

- `~/.bash_history`
- `~/.bashrc`
- `~/.bash_aliases`
- `~/.config/gh/` if you later authenticate or add CLI config

## Installed state

- Installed version: `2.92.0`
- Executable path: `/usr/bin/gh`
- Package state shows `gh` is installed and available on `PATH`
- Browser opening support comes from `gh-browser` in `~/.local/bin`

## Current state

- There is no `gh`-specific shell init in `~/.bashrc` or `~/.bash_aliases`
- There is no `~/.config/gh/` directory yet, so no user-level GitHub CLI config is currently documented here
- `gh auth login` relies on the shell's `BROWSER` setting, which is exported from `~/.bashrc` when `gh-browser` is available

## Caveats

- `gh` is installed and ready to use, but auth state and CLI preferences will only appear after you run commands like `gh auth login`
- Shell completions or aliases for `gh` are not currently configured in the documented Bash setup; browser launching is handled by `gh-browser`
