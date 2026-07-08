# snowflake

Stow package for Snowflake CLI and Cortex Code configuration. The `cortex`
binary is installed by `scripts/setup-tools.sh` from Snowflake's installer.

## Files

- `.snowflake/config.toml` — Snowflake CLI settings (logs, version warnings)
- `.snowflake/cortex/settings.json` — Cortex Code settings (theme, default connection, model)

## Stow

```sh
stow -v snowflake
```
