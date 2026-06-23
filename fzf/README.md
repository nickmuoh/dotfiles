# fzf setup

## Important configuration paths

- `~/.bashrc`
- `~/.fzf.bash`
- `~/.fzf/`

## Installed state

- Installed version: `0.72.0`
- `setup-tools.sh` installs the `fzf` apt package.
- `setup-tools.sh` skips the `~/.fzf` clone when `fzf` is already on `PATH`.
- `setup-tools.sh --reinstall-tools` pulls or creates the `~/.fzf` clone and runs `~/.fzf/install --all --no-update-rc`.
- Bash loads fzf with `[ -f ~/.fzf.bash ] && source ~/.fzf.bash`

## History-backed setup notes

- `git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf`
- `~/.fzf/install`
- repeated `source ~/.bashrc` after setup

## Integration points

- micro is configured to use fzf through the `fzfinder` plugin
- micro `settings.json` contains:
  - `fzfopen = "newtab"`
  - `fzfarg = "--preview 'batcat -f -p {}'"`
  - `fzfpath = "relative"`
- micro binds `F9` to `command:fzfinder`

## Caveats

- The shell integration depends on `~/.fzf.bash` existing.
- The preview integration in micro expects `batcat` to be installed.
