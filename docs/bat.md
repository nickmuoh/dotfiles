# bat setup

## Important configuration paths

- `~/.bash_aliases`
- `~/.bashrc`

## Current state

- The shell alias is `bat='batcat'`
- A helper alias is also defined:
  - `bathelp='bat --plain --language=help'`
- The shell `help()` function uses `bathelp` to pretty-print command help output
- Other shell/docs depend on this alias existing:
  - micro `fzfinder` preview uses `batcat`

## Caveats

- On this system the executable is `batcat`, not `bat`, so the alias is what makes `bat` work in your shell.
- Anything that expects `bat` in a non-interactive context may need either the alias loaded or a direct `batcat` command.
