# fd setup

A simple, fast alternative to `find` for searching files and directories.

## Repository

https://github.com/sharkdp/fd

`scripts/setup-tools.sh` installs `fd-find`.

## Binary name

On Debian/Ubuntu, `fd-find` provides the `fdfind` command. This repository does
not configure an `fd` alias or shim.

## Integration

Works well with other tools via pipes:
- With `fzf`: `fdfind | fzf`
- With `xargs`: `fdfind pattern | xargs -I {} command {}`
- In scripts and aliases for file discovery
