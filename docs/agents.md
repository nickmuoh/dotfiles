# Agents

The `agents` package stows `~/.agents/`.

## Managed files

- `~/.agents/.skill-lock.json` pins skills used by `npx skills`.
- `~/.agents/skills/in-ste/SKILL.md` is a local technical-writing skill.

`sync-agent-skills` reads the lockfile after bootstrap and reinstalls the listed global skills. `sync-agent-skills --agent <names...>` also targets named agents.
