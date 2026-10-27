# Lazygit

The `lazygit` package stows `~/.config/lazygit/config.yml` and the runtime prompt input `~/.config/lazygit/git-commit-msg.prompt.md`.

`scripts/setup-tools.sh` installs the current Lazygit GitHub release into `~/.local/bin/lazygit`, selecting the host architecture automatically.

## Diff rendering

`git.diffRenderers` defines two renderers, cycled with `|` in the diff view: `difftastic` (structural diff, default) and `unified` (git's plain unified diff, needed for line-by-line staging).

## AI commit messages

`<c-g>` in the files context runs a custom command that pipes the staged diff through `pi -p` (no tools, no session, no `AGENTS.md`/skills/extensions context) using the `ollama` provider and the `gpt-oss:20b-cloud` model, with `git-commit-msg.prompt.md` passed via `--system-prompt`. Passing the prompt as `--system-prompt` rather than as the user message, and stripping pi's own agent context, keeps the small local model focused on the diff — otherwise pi's default tool-use identity and repo context bleed into the prompt and the model replies empty. The generated message is opened in `git commit -e` for review/edit before committing; the command runs as `subprocess: true` since the commit editor needs a real terminal (without it, lazygit's spinner hangs forever with no output). Requires `ollama` configured with a `gpt-oss` model pulled (`ollama list` to check) and `pi` on `PATH`.
