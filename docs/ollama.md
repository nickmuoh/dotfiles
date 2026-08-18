# Ollama

Ollama has canonical bootstrap ID `ollama`. `./bootstrap.sh --package ollama` runs the Ollama installer and deploys the tracked `ollama/` Stow package with `stow --no-folding ollama`; the installer metadata and Stow ownership live together in `scripts/package-registry.sh`. `ollama` is also included in a full bootstrap. `--package ollama` does not install unrelated tools.

The Ollama package deploys configuration and custom model definitions from `ollama/`.

## Custom model sync

`ollama/.ollama/custom_models/ollama-sync.py` reconciles enabled entries in `ollama-compose.yml` with local Ollama tags. It renders Modelfiles, creates changed custom tags, and can prune undeclared or disabled custom tags with `--prune`.

During a create, the sync prints `SYNCING <tag>` and leaves Ollama's native pull output attached to the terminal. This keeps layer percentage, transferred size, download rate, and ETA visible during first-time base-model pulls. A separator and `RESULTS` summary appear after reconciliation.

Generated model files and sync state under `ollama/.ollama/custom_models/` are ignored by Git and Stow. When deploying this package manually, use `stow --no-folding ollama` so only `ollama-compose.yml` and `ollama-sync.py` are deployed from that directory.

