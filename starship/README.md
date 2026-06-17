# Starship setup

## Important configuration paths

- `~/.bashrc`
- `~/.config/starship.toml`

## Installed state

- Installed version: `1.22.1`
- Bash initializes Starship with `eval "$(starship init bash)"`

## Current state

- `command_timeout = 1500`
- directory truncation is set to `2`
- many language/tool symbols are customized in `~/.config/starship.toml`
- hostname SSH symbol is customized
- package symbol is customized
- OS symbols are extensively customized

## History-backed setup notes

- `apt install starship`
- `sudo apt install starship`
- `starship timings`
- `micro .config/starship.toml`

## Caveats

- This config uses many Nerd Font glyphs. Without a Nerd Font-capable terminal, prompt symbols may render incorrectly.
- Starship is only initialized from Bash right now; other shells are not documented here.
