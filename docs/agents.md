# Agents

The `agents` package stows `~/.agents/`.

## Managed files

- `~/.agents/.skill-lock.json` pins skills used by `npx skills`.
- `~/.agents/.skillx-managed.json` is the versioned ownership ledger written by an explicitly confirmed `skillx adopt --from-lock` operation.
- `~/.agents/skills/in-ste/SKILL.md` is a local technical-writing skill.

The lockfile is desired state for `skillx`. `skillx sync` validates every declared source and skill before installing or updating anything, and post-install setup invokes that command after the lockfile and Node tooling are available. Indeterminate remote state blocks sync without changing installed skills or desired state.

The ownership ledger is custody rather than discovery. Only `skillx adopt --from-lock --yes` creates management records for pre-existing installations. `skillx prune --yes` can remove an installation only when its ledger record and installed inventory agree on one exact path, skill name, and source. Unmanaged, local, manual, duplicate, and ambiguous installations remain untouched.
