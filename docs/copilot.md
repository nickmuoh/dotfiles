# GitHub Copilot CLI

AI coding assistant for the terminal, installed as a gh extension wrapper.

## Install

```sh
curl -fsSL https://gh.io/copilot-install | bash
```

## Config directory

`~/.copilot/` — not stow-tracked, not in this dotfiles repo.

## mcp-config.json

Three HTTP MCP servers configured, all with `"tools": ["*"]`:

| Name | URL |
|------|-----|
| `e-tools` | `https://mcp.trimble.tools/mcp` |
| `amplitude` | `https://mcp.amplitude.com/mcp` |
| `monte-carlo-mcp` | `https://mcp.getmontecarlo.com/mcp` |

Authentication for each server is handled at runtime (OAuth or token flows managed by the server, not stored in this file).

## settings.json

```json
{ "model": "auto" }
```

`"model": "auto"` lets Copilot select the model based on context.
