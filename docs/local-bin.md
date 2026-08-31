# Local binaries

The `local-bin` package stows user-owned helpers under `~/.local/bin/`.

- `difft` wraps difftastic with inline display.
- `gh-browser` opens browser URLs for `gh auth login`.
- `mwt` manages sparse worktrees from a backend repository's `wt.yaml`; it requires `git` and `yq`.
- `skillx` safely reconciles globally installed agent skills with `~/.agents/.skill-lock.json`. It requires Python 3.12 or newer and `npx`; it has no third-party Python runtime dependencies and does not require `jq`.

The Stow-facing `skillx` executable loads its implementation from the ignored `skillx-cli` project in this package. The command defaults to `~/.agents/.skill-lock.json`; `--lockfile` or `LOCKFILE` can override it. Ownership used for pruning is recorded separately in `~/.agents/.skillx-managed.json`.

Commands:

- `skillx check` validates every declared source and skill without mutation.
- `skillx sync` validates all desired entries before installing or updating any of them. Before live mutation, it preflights the complete install batch in disposable homes and snapshots canonical skills plus the upstream lock for rollback. `--dry-run` performs the full validation pass without invoking a mutating `npx` command. `--agent <names...>` targets named agents in addition to global installation.
- `skillx repair` previews confirmed-invalid lock entries. `--yes` backs up the lockfile and atomically removes only those entries; indeterminate failures are preserved.
- `skillx adopt --from-lock` previews explicit custody transfer for installed desired skills. `--yes` writes exact skill, source, and installed-path records to the ownership ledger. Ordinary sync never adopts existing installations.
- `skillx prune` previews ledger-backed installations absent from desired state. `--yes` removes them only when each candidate has one unambiguous exact-path inventory match. The removal batch retains rollback state until the ownership-ledger update commits. Any duplicate name, path mismatch, source conflict, or malformed prerequisite blocks the complete prune.

Destructive commands support `--dry-run`. Every expected outcome, including a safely blocked reconciliation, is reported as a schema-versioned document with `--json` or as text otherwise. `--json` always writes exactly one document to stdout. Operational failures also produce a failed report; stderr stays quiet by default, `-v`/`--verbose` writes the contextual error and captured `npx` diagnostics, and `-vv` adds a traceback. Exit `0` means success, exit `1` means drift or a safely blocked reconciliation, and exit `2` means reliable execution was prevented by usage, configuration, dependency, or runtime failure.

Remote enumeration runs in a disposable home and cache. Timeouts, transport failures, rate limits, authentication failures, SSO failures, and ambiguous not-found responses are indeterminate and can block sync but cannot trigger repair or prune. Local, manual, unadopted, and ambiguously attributed skills are never pruned.
