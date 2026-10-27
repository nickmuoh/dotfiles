# pi-minimal-statusline

Minimal Pi footer replacement. The only real change from Pi's stock footer is
the working-directory line: it keeps the leaf and its immediate parent full
and abbreviates every earlier segment to its first character (two characters
if that first character isn't a letter/digit, e.g. `_SketchUp` -> `_S`), then
hard-caps the line at 80 characters.

```text
~/Developer/_SketchUp/sbd-legionrepo-wt/snowflake_cdp_dcm/projects/snowflake_cdp_dcm
->
~/D/_S/s/s/projects/snowflake_cdp_dcm
```

## How it works

Pi has no partial footer-override hook, so `ctx.ui.setFooter` replaces the
whole footer. This extension rebuilds the second line (token stats, cache-hit
%, cost, context `%/total`, provider, model, thinking effort) from the public
`ExtensionContext` surface so it matches Pi's stock format, since Pi's own
formatting helpers for that line aren't exported by the package.

## Known gaps

- No responsive width truncation/wrapping (`truncateToWidth`) like the stock
  footer — very narrow terminals may overflow a line instead of wrapping.
- The `(sub)` subscription-cost flag needs `session.modelRuntime`, which
  isn't exposed to extensions; only approximated for the `kimi-coding`
  provider.

## Installation

The package is registered in `pi/.pi/agent/settings.json` as a local path and
deployed through the `pi` Stow package:

```sh
stow -nv pi    # preview
stow pi
```

## Development

```sh
npm install
npm run typecheck
npm test
npm run build
```
