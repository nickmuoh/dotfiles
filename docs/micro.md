# Micro

The `micro` package manages `settings.json`, `bindings.json`, `palettero.cfg`,
and Nord color schemes under `~/.config/micro/`. Buffer history under
`~/.config/micro/buffers/` is runtime state and is not tracked.

## Current configuration

- The active colorscheme is `nord-16`; `iconic_tabs` is enabled.
- `gitStatus`, `fzfinder`, and `preview` use configured plugin repositories. `jump` and `wc` use Micro's default plugin index.
- `F8`, `F9`, and `F12` run `preview`, `fzfinder`, and `jumptag` respectively.
- `fzfinder` opens results in a new tab and previews with `batcat`.
- `preview` requires `pandoc`; fzfinder requires `fzf`; visual plugins require a Nerd Font-capable terminal.

`scripts/setup-micro.sh` installs or updates generated plugin content. The live plugin directory is the source of truth for installed plugin versions.

Use `micro -plugin install <plugin>` for plugins available from Micro's default
index. The generated `palettero` and `iconic_tabs` repositories are managed by
the bootstrap script.
