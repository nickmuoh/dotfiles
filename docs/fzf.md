# fzf

The `fzf` package stows `~/.fzf.bash`. `scripts/setup-tools.sh` installs the
`fzf` command and owns the generated `~/.fzf/` repository; tool reinstallation
refreshes that repository and runs its installer.

Interactive Bash loads fzf with `[ -f ~/.fzf.bash ] && source ~/.fzf.bash`.

Micro's `fzfinder` integration is documented in [`micro.md`](micro.md). Its preview command uses `batcat`.
