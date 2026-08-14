# shell_setup agent guide

This repository manages Linux/WSL shell, editor, and AI-agent configuration with GNU Stow and bootstrap scripts.

## Scope

The root instructions apply unless a closer `AGENTS.md` exists. Package directories are the source of truth for deployed configuration; do not edit their `$HOME` targets directly.

## Documentation

After a change, update the canonical `docs/<package>.md` for the affected Stow package. Update a related `docs/<tool>.md` when shell-level behavior changes. Do not add package-level READMEs or a package inventory to `README.md`.

Use [documentation rules](docs/agents/documentation.md) for documentation changes.

## Operational guides

- [Stow packages](docs/agents/stow.md)
- [Tool installation](docs/agents/tool-installation.md)
- [Bootstrap scripts](docs/agents/bootstrap.md)
- [tmux safety](docs/agents/tmux.md)

## Completion checklist

- Update the relevant canonical documentation.
- Run the task-appropriate validation from the focused guide.
- Do not overwrite a real file in `$HOME` without inspection and user confirmation.
- Do not create planning or scratch-pad files in this repository.
