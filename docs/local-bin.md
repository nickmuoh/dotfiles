# Local binaries

The `local-bin` package stows user-owned helpers under `~/.local/bin/`.

- `difft` wraps difftastic with inline display.
- `gh-browser` opens browser URLs for `gh auth login`.
- `mwt` manages sparse worktrees from a backend repository's `wt.yaml`; it requires `git` and `yq`.
- `sync-agent-skills` reads `~/.agents/.skill-lock.json`, requires `jq` and `npx`, and reinstalls listed skills. `--agent <names...>` also syncs named agents; `*` targets all supported agents.
