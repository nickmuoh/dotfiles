# fd setup

A simple, fast alternative to `find` for searching files and directories.

## Repository

https://github.com/sharkdp/fd

## Install command

```sh
sudo apt install fd-find
```

## Binary names

The package installs two binary names:
- `fd` — the primary command
- `fdfind` — also available if needed

## Usage

`fd` replaces `find` for most common use cases with a more user-friendly interface:

- Find files by name: `fd pattern`
- Find directories: `fd -t d pattern`
- Find files of type: `fd -e txt` (extension)
- Exclude patterns: `fd -E '*.tmp'`
- Case-insensitive search: `fd -i pattern`

## Integration

Works well with other tools via pipes:
- With `fzf`: `fd | fzf`
- With `xargs`: `fd pattern | xargs -I {} command {}`
- In scripts and aliases for file discovery
