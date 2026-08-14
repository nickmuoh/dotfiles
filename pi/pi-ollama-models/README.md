# pi-ollama-models

Pi extension that discovers models from an Ollama-compatible `/models` endpoint and keeps the `ollama` provider in Pi's `models.json` current.

This local package is deployed by GNU Stow. The wrapper at `pi/.pi/agent/extensions/pi-ollama-models.ts` re-exports `pi/pi-ollama-models/src/extension.ts`; it is not installed from an external repository.

## Configuration

Configure the endpoint and overrides in `~/.pi/agent/models.json`:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "modelOverrides": {
        "qwen3-coder:latest": {
          "contextWindow": 65536,
          "reasoning": true
        }
      },
      "models": []
    }
  }
}
```

The extension reads `providers.ollama` from `getAgentDir()/models.json`, requests `${baseUrl}/models`, and writes OpenAI-compatible `data[].id` values (or Ollama `models[].name` values) in stable sorted order with duplicates removed. Entries are merged with exact matching `modelOverrides` and always retain the discovered ID; unrelated configuration is preserved. Configured request headers are sent, with `Authorization: Bearer <apiKey>` added only for a literal non-empty key when `authHeader` is true. Updates use an atomic same-directory replacement of the resolved Stow target, preserve its mode, retain symlinks, and byte-identical files are not rewritten.

Network, HTTP, response JSON, or write errors fail open: the persisted provider configuration is registered for the current Pi process when possible. Registration strips discovery-writer-only fields such as `modelOverrides`, `prefix`, `version`, and `filter`. The extension uses a bounded request timeout and catches startup failures so Ollama availability never prevents Pi from starting. `startPiOllamaModels` accepts injected startup dependencies for direct testing.

## Development

```sh
cd pi/pi-ollama-models
npm install
npm test
npm run typecheck
npm run build
```
