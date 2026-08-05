# .agents

Stow package for `~/.agents/`.

## Contents

- `.skill-lock.json` — pinned skill versions used by `npx skills` (Cortex Code skill runner)
- `skills/technical-english/SKILL.md` — local `/technical-english` skill for ASD-STE100-style technical writing

`sync-agent-skills` reads this lockfile after bootstrap and reinstalls the global skills listed under `.skills`. Pass `--agent <names...>` to also sync those skills to specific agents.

Install the local skill globally with:

```sh
npx skills add ~/.dotfiles/agents/skills -g -y --skill technical-english
```

## Stow

```sh
stow -nv .agents   # dry-run
stow -v  .agents   # apply
```
