# Interfaces

This directory documents the interface layer that sits in front of the local and remote models.

## What Lives Here

| Surface                | Primary file                                                  | Purpose                                                                                                                       |
| ---------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Compose entrypoint     | `interfaces/docker-compose.interface.yml`                     | Defines the LiteLLM proxy and the recipe-pinned 27B / 35B vLLM backends.                                                      |
| LiteLLM model catalog  | `interfaces/config/litellm/litellm-config.yaml`               | Root include file for the proxy-visible models, routing, and provider fragments under `interfaces/config/litellm/providers/`. |
| Developer client note  | `interfaces/docs/developer-clients.md`                        | Operator note for VS Code, Codex-style clients, OpenClaw, Hermes Agent, and Claude Code against this proxy.                   |
| llama.cpp helper       | `interfaces/llama-mtp.sh`                                     | Runs the 27B llama.cpp backend directly from the host, sourcing `.env` first.                                                 |
| llama.cpp build recipe | `interfaces/llama-cpp/Dockerfile`                             | Builds the CUDA-enabled llama.cpp image used by the compose profile.                                                          |
| vLLM launch script     | `interfaces/vllm/qwen3.6-27b-fp8-mtp.sh`                      | Replays the `spark-vllm-docker` FP8 MTP recipe inside the compose service.                                                    |
| vLLM launch script     | `interfaces/vllm/qwen3.6-35b-a3b-fp8-mtp.sh`                  | Replays the 35B A3B FP8 recipe with MTP enabled inside the compose service.                                                   |
| Shared mods            | `mods/fix-qwen3-coder-next`, `mods/fix-qwen3.6-chat-template` | Pre-launch mods mounted into `/workspace/mods` and applied before `vllm serve`.                                               |
| Tool-call sanitizer    | `interfaces/scripts/litellm/litellm_qwen36_sanitizer.py`      | Repairs tagged tool-call XML so LiteLLM receives cleaner Qwen 3.6 outputs.                                                    |

## Profiles

| Compose profile         | Service name            | Default endpoint           | Purpose                                        | Notes                                                                  |
| ----------------------- | ----------------------- | -------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------- |
| `interface`             | `litellm`               | `http://localhost:4000`    | OpenAI-compatible proxy for tools and clients. | Expects one active 27B backend on host port `8000`.                    |
| `llama-qwen-3-6-27b`    | `llama-qwen-3-6-27b`    | `http://localhost:8000/v1` | 27B local backend powered by llama.cpp.        | Mutually exclusive with `vllm-qwen-3-6-27b`.                           |
| `vllm-qwen-3-6-27b`     | `vllm-qwen-3-6-27b`     | `http://localhost:8000/v1` | 27B local backend powered by vLLM.             | Mutually exclusive with `llama-qwen-3-6-27b`.                          |
| `vllm-qwen-3-6-35b-a3b` | `vllm-qwen-3-6-35b-a3b` | `http://localhost:8001/v1` | 35B A3B direct vLLM backend.                   | MTP enabled; auto-falls back to `tp=1` when pinned to one visible GPU. |

## Startup Rules

1. Always run Compose from the repository root with the top-level `docker-compose.yml`.
2. Set the full active stack shape in root `.env` through `COMPOSE_PROFILES`.
3. Include `data` whenever LiteLLM or Grafana needs Postgres.
4. Include `interface` only after choosing one 27B backend profile.
5. Do not include `llama-qwen-3-6-27b` and `vllm-qwen-3-6-27b` together. Both are designed around host port `8000` so LiteLLM can keep a stable upstream URL.
6. Use `vllm-qwen-3-6-35b-a3b` only for direct access unless you extend the provider fragments included by `litellm-config.yaml`.

## Recommended Profile Sets

Set one of these values in root `.env`, then run `docker compose up -d` from the repository root:

```bash
COMPOSE_PROFILES=data,obs,interface,llama-qwen-3-6-27b
COMPOSE_PROFILES=data,interface,vllm-qwen-3-6-27b
COMPOSE_PROFILES=data,vllm-qwen-3-6-35b-a3b
```

Once `COMPOSE_PROFILES` is set, the routine commands are:

```bash
docker compose up -d
docker compose ps
docker compose down
```

## Developer Clients

The proxy now publishes one consistent provider-backed naming scheme:

- `openai/<Provider>/...`
- `anthropic/<Provider>/...`

It also publishes the latest direct Claude compatibility aliases for clients that send hardcoded Claude model IDs:

- `claude-opus-4-7`
- `claude-sonnet-4-6`
- `claude-haiku-4-5-20251001`
- `claude-haiku-4-5`

OpenAI-compatible clients should use `http://localhost:4000/v1`. Claude Code should use `http://localhost:4000` and enable gateway discovery. See `interfaces/docs/developer-clients.md` for exact examples and the header-forwarding caveat for Claude Max passthrough.

## Documentation Map

- `file-index.md`: purpose and parameters for every interface file.
- `env-reference.md`: grouped root `.env` variables that drive the interface stack.
- `developer-clients.md`: operator setup for developer tools and agent clients.

## Standalone Notes

- The old standalone vLLM compose file was removed on purpose. `interfaces/docker-compose.interface.yml` is now the single source of truth for all interface runtimes.
- The supported operator workflow is the top-level root compose entrypoint with `COMPOSE_PROFILES` defined in `.env`; do not run Compose from `interfaces/`.
- `interfaces/interface.md` is now a short quick-reference. The deeper operational details live in this docs directory.
