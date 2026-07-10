# .agents

Stow package for `~/.agents/`.

## Contents

- `.skill-lock.json` — pinned skill versions used by `npx skills` (Cortex Code skill runner)

`sync-agent-skills` reads this lockfile after bootstrap and reinstalls the global skills listed under `.skills`. Pass `--agent <names...>` to also sync those skills to specific agents.

## Stow

```sh
stow -nv .agents   # dry-run
stow -v  .agents   # apply
```
