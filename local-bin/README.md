# local-bin package

## Contents

- `~/.local/bin/difft` (wrapper for `difftastic`)
- `~/.local/bin/gh-browser` (browser opener used by `gh auth login`)
- `~/.local/bin/mwt` (monorepo worktree helper for detached-head backends with sparse checkout)

## Notes

- This package carries small user-owned helper binaries.
- `mwt` is installed by stowing `local-bin`: `stow -v local-bin`
- `mwt` reads `wt.yaml` from the backend repo root and depends on `git` plus the Python `yq` wrapper available on `PATH`
