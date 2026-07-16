# 1password package

## Contents

- `~/.1password/agent-bridge.sh` (shell helper that forwards WSL SSH agent requests to the 1Password SSH agent on Windows)

## Notes

- This package is installed by stowing `1password`: `stow -v 1password`
- `bash/.bashrc` sources `~/.1password/agent-bridge.sh` for interactive shells
- `~/.1password/agent-bridge.sh` uses strict mode internally and restores the caller's shell options before returning so interactive Bash state is unchanged
- `scripts/setup-tools.sh` installs `socat` in WSL and `npiperelay.exe` from `https://github.com/jstarks/npiperelay`
- 1Password for Windows is required and must be installed with Developer > `Use the SSH agent` enabled; setup details are documented at `https://developer.1password.com/docs/ssh/agent/`
- The Windows `OpenSSH Authentication Agent` service must be stopped and disabled so 1Password can own `\\.\pipe\openssh-ssh-agent`
- If `%LOCALAPPDATA%/1Password/config/ssh/agent.toml` exists, it overrides the default Personal/Private/Employee vault scope and only exposes the keys matched by that file
- This bridge flow does not use `keychain`; any `keychain` block in `~/.bashrc` is separate local-key setup
