# Documentation rules

`README.md` is human orientation only: project purpose, bootstrap quick start, layout, and links to `docs/` and `AGENTS.md`. It does not contain a package inventory.

Each Stow package has one canonical `docs/<package>.md` file. Package directories contain configuration, not human-readable package documentation. The exception is a standalone subproject README, such as `pi/pi-model-filter/README.md`, and runtime Markdown inputs consumed by tools.

Write factual current state only. Use inline code for paths, commands, and key names. Installation commands and installer details belong in `scripts/setup-tools.sh` or `bootstrap.sh`; documentation identifies the owning script instead of reproducing shell-history notes.
