# Origo Agent

The agent core of Origo/元启. It exposes a local-first, cloud-capable assistant that plans tasks, calls skills (MCP-style tools), keeps memory, and asks before doing anything risky.

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
origo-agent
```

## Backends

- **Local (default)**: Ollama (`http://localhost:11434`) or any OpenAI-compatible local server.
- **Cloud (optional)**: any OpenAI-compatible endpoint, configured by the user.

## Environment / config

- `ORIGO_MODEL` (default: a local model tag, e.g. `qwen3:1.7b`)
- `ORIGO_LOCAL_BASE_URL` (default `http://localhost:11434/v1`)
- `ORIGO_CLOUD_BASE_URL`, `ORIGO_CLOUD_API_KEY`, `ORIGO_CLOUD_MODEL`
- `ORIGO_ALLOW_CLOUD` (`0`/`1`, default `0`)

## License

Apache-2.0.
