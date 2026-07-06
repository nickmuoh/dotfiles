# micro setup

## Important configuration paths

- `~/.config/micro/settings.json`
- `~/.config/micro/bindings.json`
- `~/.config/micro/palettero.cfg`
- `~/.config/micro/colorschemes/nord-16.micro`
- `~/.config/micro/colorschemes/nord-16-light.micro`
- `~/.config/micro/colorschemes/nord-tc.micro`
- `~/.config/micro/colorschemes/nord-tc-light.micro`
- `~/.config/micro/plug/`

## Local runtime state

- `~/.config/micro/buffers/`
- `~/.config/micro/buffers/history` is local buffer history runtime state and is not tracked in Git or deployed by Stow

## Installed plugins observed on disk

- `fzfinder`
- `gitStatus`
- `iconic_tabs`
- `jump`
- `palettero`
- `preview`
- `wc`

## Plugin metadata observed in repo manifests

- `fzfinder`: `0.2.0`
- `gitStatus`: manifest includes `0.1.5` as latest listed version
- `iconic_tabs`: `0.1.0`
- `jump`: `0.0.4`
- `palettero`: `0.0.5`
- `preview`: `1.0.1`
- `wc`: `1.1.0`

## Current state

- Active colorscheme in `settings.json`: `nord-16`
- `iconic_tabs.enabled` is `true`
- `pluginrepos` includes custom repos for:
  - `preview`
  - `gitStatus`
  - `fzfinder`
- `statusformatr` uses `$(gitStatus.info)`
- fzf integration is configured with:
  - `fzfopen = "newtab"`
  - `fzfarg = "--preview 'batcat -f -p {}'"`
  - `fzfpath = "relative"`
- Micro plugin customization:
  - `gitStatus` is enabled via `pluginrepos` and shown in the status bar
  - `fzfinder` is installed from the custom repo and exposed as `F9`
  - `preview` is installed from the custom repo and exposed as `F8`
  - `jump` is installed through Micro's plugin manager
  - `wc` is installed through Micro's plugin manager
  - `palettero.cfg` includes `fzfinder` and `preview` as palette commands
- Custom key bindings:
  - `F9` -> `command:fzfinder`
  - `F12` -> `command:jumptag`
  - `F8` -> `command:preview`
- Palettero custom menu entries in `palettero.cfg`:
  - `fzfinder`
  - `preview`

## Setup flow

- `micro -plugin install gitStatus`
- `micro -plugin install preview`
- `micro -plugin install fzfinder`
- `micro -plugin install jump`
- `micro -plugin install wc`
- `git clone https://github.com/terokarvinen/palettero ~/.config/micro/plug/palettero`
- `git clone https://github.com/dalekirkwood/Micro_Editor_Iconic_Tabs ~/.config/micro/plug/iconic_tabs`

## History-backed setup notes

- `curl https://getmic.ro | bash && sudo mv micro /usr/bin`
- `micro ~/.bashrc`
- `micro ~/.tmux.conf`
- `micro .config/starship.toml`
- `micro config`
- `micro -plugin install gitStatus`
- `micro -plugin install preview`
- `micro ~/.config/micro/settings.json`

## Caveats

- `jump` and `wc` use Micro's default plugin index, so they do not need custom `pluginrepos` entries.
- `palettero` still uses a manual clone because its README documents development install only.
- `iconic_tabs` still uses a manual clone or copy into `~/.config/micro/plug/iconic_tabs`.
- `fzfinder` and some other plugins assume `fzf` is installed and reachable in `PATH`.
- `fzfinder` preview is wired to `batcat`, so the preview experience depends on the `bat`/`batcat` package being installed.
- `preview` depends on `pandoc` being installed and available in `PATH`.
- `iconic_tabs` and parts of the visual experience assume a Nerd Font-capable terminal.
- The exact installed plugin version is not centrally locked by micro; the repo manifests show available versions, but the live plugin directory is the real source of truth.
