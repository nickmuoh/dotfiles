# 1Password WSL bridge

The `1password` package stows `~/.1password/agent-bridge.sh`. Interactive Bash sources it to forward WSL SSH-agent requests to the 1Password SSH Agent on Windows.

## Requirements

- `scripts/setup-tools.sh` installs `socat` and `npiperelay.exe`.
- 1Password for Windows has Developer > `Use the SSH agent` enabled.
- The Windows `OpenSSH Authentication Agent` service is stopped and disabled so 1Password owns `\\.\pipe\openssh-ssh-agent`.
- If `%LOCALAPPDATA%/1Password/config/ssh/agent.toml` exists, it limits the SSH keys exposed to WSL.

The bridge restores the caller's shell options before returning. It is separate from optional `keychain` setup.

## Verify

```sh
ssh-add -L | ssh-keygen -lf -
ssh -T git@github.com
```

If no expected key is exposed, verify the Windows service state and `agent.toml` rules.
