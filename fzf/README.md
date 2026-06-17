# fzf setup

## Important configuration paths

- `~/.bashrc`
- `~/.fzf.bash`
- `~/.fzf/`

## Installed state

- Installed version: `0.72.0`
- Installed from a Git clone under `~/.fzf`
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

- fzf was installed from a clone, not a package manager, so updates are likely manual unless another tool manages that directory.
- The shell integration depends on `~/.fzf.bash` existing.
- The preview integration in micro expects `batcat` to be installed.
