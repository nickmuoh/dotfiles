# local-bin package

## Contents

- `~/.local/bin/difft` (wrapper for `difftastic`)
- `~/.local/bin/gh-browser` (browser opener used by `gh auth login`)
- `~/.local/bin/mwt` (monorepo worktree helper for detached-head backends with sparse checkout)
- `~/.local/bin/sync-agent-skills` (reinstalls global agent skills from `~/.agents/.skill-lock.json`)

## Notes

- This package carries small user-owned helper binaries.
- `mwt` is installed by stowing `local-bin`: `stow -v local-bin`
- `mwt` reads `wt.yaml` from the backend repo root and depends on `git` plus the Python `yq` wrapper available on `PATH`
- `sync-agent-skills` depends on `jq` and `npx`; it reads the stowed lockfile and runs `npx skills add <skill> -g -y` for each entry
- `sync-agent-skills --agent <names...>` also syncs each skill to the named agents; pass `*` to target all supported agents
