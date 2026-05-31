# Reference

Quick-lookup tables. Technical depth lives in code comments — these are cheat sheets.

## Docker Images

| Image                               | Tag                      | Pulled from                              |
| ----------------------------------- | ------------------------ | ---------------------------------------- |
| `nilayparikh/llama-cpp-dgx`         | `cuda13.1.2-b9222`       | GitHub Container Registry (custom build) |
| `docker.litellm.ai/berriai/litellm` | `latest`                 | LiteLLM registry                         |
| `grafana/grafana-oss`               | `latest`                 | Docker Hub                               |
| `grafana/mimir`                     | `latest`                 | Docker Hub                               |
| `grafana/loki`                      | `latest`                 | Docker Hub                               |
| `grafana/alloy`                     | `latest`                 | Docker Hub                               |
| `gcr.io/cadvisor/cadvisor`          | `v0.52.1`                | Google Container Registry                |
| `nvcr.io/nvidia/k8s/dcgm-exporter`  | `4.5.3-4.8.2-distroless` | NVIDIA NGC                               |
| `postgres`                          | `latest`                 | Docker Hub                               |

The only custom image is `llama-cpp-dgx`, built from `docker/llama-cpp-dgx/Dockerfile`.

## Model Catalog

| Model ID                             | Provider                | Type          | Requires                    |
| ------------------------------------ | ----------------------- | ------------- | --------------------------- |
| `DGX/Qwen3.6-27B`                    | Local (llama.cpp :8000) | Chat          | Model file in `.env`        |
| `DGX/Qwen3.6-35B-A3B`                | Local (llama.cpp :8001) | Chat + Vision | Model + mmproj files        |
| `Azure/Kimi-K2.6`                    | Azure Foundry           | Chat          | `MICROSOFT_FOUNDRY_API_KEY` |
| `Azure/DeepSeek V4 Flash`            | Azure Foundry           | Chat          | Same                        |
| `DeepSeek/DeepSeek-V4-Flash`         | DeepSeek native         | Chat          | `DEEPSEEK_API_KEY`          |
| `DeepSeek/DeepSeek-V4-Pro`           | DeepSeek native         | Chat          | Same                        |
| `NVIDIA/DeepSeek-V4-Flash`           | NVIDIA AI Endpoints     | Chat          | `NVIDIA_API_KEY`            |
| `NVIDIA/MiniMax-M2.7`                | NVIDIA AI Endpoints     | Chat          | Same                        |
| `NVIDIA/Kimi-K2.6`                   | NVIDIA AI Endpoints     | Chat          | Same                        |
| `OpenCodeZen/MIMO-V2.5-FREE`         | OpenCode Zen            | Chat          | `OPENCODE_ZEN_API_KEY`      |
| `OpenCodeZen/NEMOTRON-3-SUPER-FREE`  | OpenCode Zen            | Chat          | Same                        |
| `OpenCodeZen/DEEPSEEK-V4-FLASH-FREE` | OpenCode Zen            | Chat          | Same                        |
| `OpenCodeZen/BIG-PICKLE`             | OpenCode Zen            | Chat          | Same                        |

## Ports

### User-facing

| Port | Service           | Stack Profile | Unique Profile           |
| ---- | ----------------- | ------------- | ------------------------ |
| 3000 | Grafana           | `obs`         | `grafana`                |
| 4000 | LiteLLM proxy     | `interface`   | `litellm`                |
| 5432 | PostgreSQL        | `data`        | `postgres`               |
| 8000 | llama.cpp 27B     | `interface`   | `llama-qwen-3-6-27b`     |
| 8001 | llama.cpp 35B A3B | `interface`   | `llama-qwen-3-6-35b-a3b` |

### Internal (for debugging / tunnel routing)

| Port  | Service       | Stack Profile | Purpose           |
| ----- | ------------- | ------------- | ----------------- |
| 9009  | Mimir HTTP    | `obs`         | Metrics endpoint  |
| 3100  | Loki HTTP     | `obs`         | Log ingestion     |
| 9400  | DCGM exporter | `obs`         | GPU metrics       |
| 8080  | cAdvisor      | `obs`         | Container metrics |
| 12345 | Alloy admin   | `obs`         | Health/HTTP admin |
| 9096  | Loki gRPC     | `obs`         | gRPC ingestion    |

## Scripts

The `scripts/` directory is reserved for project utility scripts. Historically included GPU smoke tests, system info, and GPU persistence scripts, which have been removed. If you need these, refer to old commits or the original source patterns in `docker/llama-cpp-dgx/Dockerfile` and `docker/claude-code/Dockerfile` for reference implementations.

The root-level `claude-code.sh` is the primary launcher for Claude Code — it reads `.env` for auth tokens and model aliases, then launches an isolated container routed through LiteLLM.

## Model Aliases (Claude Code)

These `.INIT/` aliases are defined in `LITELLM_MODEL_ALIAS_*` env vars and discovered via LiteLLM's `/v1/models`:

| Alias          | Default Model                     | Env Variable                |
| -------------- | --------------------------------- | --------------------------- |
| `.INIT/Ultra`  | `OpenCodeZen/BIG-PICKLE`          | `LITELLM_MODEL_ALIAS_ULTRA` |
| `.INIT/Pro`    | `DGX/Qwen3.6-27B`                 | `LITELLM_MODEL_ALIAS_PRO`   |
| `.INIT/Flash`  | `DGX/Qwen3.6-35B-A3B`             | `LITELLM_MODEL_ALIAS_FLASH` |
| `.INIT/AIR`    | `DGX/Qwen3.6-35B-A3B`             | `LITELLM_MODEL_ALIAS_AIR`   |

## CI/CD (GitHub Actions)

| Workflow                         | Trigger           | What it does                         |
| -------------------------------- | ----------------- | ------------------------------------ |
| `lint.yml`                       | Push/PR to main   | YAML lint, ShellCheck, Python syntax |
| `trivy.yml`                      | Push/PR/daily     | Full repo secret + misconfig scan    |
| `docker-build-llama-cpp-dgx.yml` | Push to main/tags | Build & push `llama-cpp-dgx` to GHCR |
| `docker-build-claude-code.yml`   | Push to main/tags | Build & push `claude-code` to GHCR   |
| `deploy-docs.yml`                | Push to main      | Deploy MkDocs site to GitHub Pages   |
