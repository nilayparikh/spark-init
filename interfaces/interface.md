# Interface Quick Reference

The interface stack now uses one compose entrypoint: `interfaces/docker-compose.interface.yml`.

Always run Compose from the repository root with `COMPOSE_PROFILES` set in the
root `.env` file and the top-level `docker-compose.yml`. Do not run Compose
from `interfaces/`.

Current default:

```text
COMPOSE_PROFILES=data,obs,interface,llama-qwen-3-6-27b
```

Routine commands:

```bash
docker compose up -d
docker compose ps
docker compose down
```

Alternative profile sets:

```text
COMPOSE_PROFILES=data,obs,interface,llama-qwen-3-6-35b-a3b
COMPOSE_PROFILES=data,obs,interface,llama-qwen-3-6-27b,llama-qwen-3-6-35b-a3b
```

Profiles:

- `interface`: LiteLLM proxy on `http://localhost:4000`
- `llama-qwen-3-6-27b`: llama.cpp-backed 27B runtime on host port `8000`
- `llama-qwen-3-6-35b-a3b`: llama.cpp-backed 35B A3B runtime on host port `8001`

Important behavior:

- `llama-qwen-3-6-27b` and `llama-qwen-3-6-35b-a3b` use separate host ports (8000 and 8001) and can run simultaneously.
- LiteLLM is configured to proxy the active backends through `INTERFACE_QWEN_3_6_27B_BASE_URL` and `INTERFACE_QWEN_3_6_35B_A3B_BASE_URL`.
- LiteLLM now loads the root catalog at `interfaces/config/litellm/config.yaml` plus provider fragments under `interfaces/config/litellm/providers/`.
- The top-level root compose file is the supported operator entrypoint for this stack.
- All documentation lives under `docs/` in the repository root.

Client defaults:

- OpenAI-compatible clients: `http://localhost:4000/v1`
- Claude Code: `ANTHROPIC_BASE_URL=http://localhost:4000`
- LiteLLM auth key: `LITELLM_MASTER_KEY` (local fallback default: `sk-interface-ui-local`)
- Local backend key: `INTERFACE_QWEN_3_6_27B_API_KEY` (local fallback default: `sk-dummy`)
- Default local coding model: `openai/DGX/Qwen3.6 27B/SWE`

See `docs/interfaces/developer-clients.md` for exact VS Code, Codex-style client, OpenClaw, Hermes Agent, and Claude Code examples.
