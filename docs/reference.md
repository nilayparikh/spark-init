# Reference

Quick-lookup tables. Technical depth lives in code comments — these are cheat sheets.

## Docker Images

| Image | Tag | Pulled from |
|---|---|---|
| `nilayparikh/llama-cpp-dgx` | `cuda13.1.2-b9222` | Docker Hub (custom build) |
| `docker.litellm.ai/berriai/litellm` | `latest` | LiteLLM registry |
| `grafana/grafana-oss` | `latest` | Docker Hub |
| `grafana/mimir` | `latest` | Docker Hub |
| `grafana/loki` | `latest` | Docker Hub |
| `grafana/alloy` | `latest` | Docker Hub |
| `gcr.io/cadvisor/cadvisor` | `v0.52.1` | Google Container Registry |
| `nvcr.io/nvidia/k8s/dcgm-exporter` | `4.5.3-4.8.2-distroless` | NVIDIA NGC |
| `postgres` | `latest` | Docker Hub |

The only custom image is `llama-cpp-dgx`, built from `interfaces/dockerfiles/Dockerfile`.

## Model Catalog

| Model ID | Provider | Type | Requires |
|---|---|---|---|
| `DGX/Qwen3.6-27B` | Local (llama.cpp :8000) | Chat | Model file in `.env` |
| `DGX/Qwen3.6-35B-A3B` | Local (llama.cpp :8001) | Chat + Vision | Model + mmproj files |
| `Azure/Kimi-K2.6` | Azure Foundry | Chat | `MICROSOFT_FOUNDRY_API_KEY` |
| `Azure/DeepSeek V4 Flash` | Azure Foundry | Chat | Same |
| `DeepSeek/DeepSeek-V4-Flash` | DeepSeek native | Chat | `DEEPSEEK_API_KEY` |
| `DeepSeek/DeepSeek-V4-Pro` | DeepSeek native | Chat | Same |
| `NVIDIA/DeepSeek-V4-Flash` | NVIDIA AI Endpoints | Chat | `NVIDIA_API_KEY` |
| `NVIDIA/MiniMax-M2.7` | NVIDIA AI Endpoints | Chat | Same |
| `NVIDIA/Kimi-K2.6` | NVIDIA AI Endpoints | Chat | Same |
| `OpenCodeZen/MIMO-V2.5-FREE` | OpenCode Zen | Chat | `OPENCODE_ZEN_API_KEY` |
| `OpenCodeZen/NEMOTRON-3-SUPER-FREE` | OpenCode Zen | Chat | Same |
| `OpenCodeZen/DEEPSEEK-V4-FLASH-FREE` | OpenCode Zen | Chat | Same |
| `OpenCodeZen/BIG-PICKLE` | OpenCode Zen | Chat | Same |

## Ports

| Port | Service | Profile |
|---|---|---|
| 3000 | Grafana | `obs` |
| 4000 | LiteLLM proxy | `interface` |
| 5432 | PostgreSQL | `data` |
| 8000 | llama.cpp 27B | `llama-qwen-3-6-27b` |
| 8001 | llama.cpp 35B A3B | `llama-qwen-3-6-35b-a3b` |

## Scripts

| Script | What it does |
|---|---|
| `scripts/spark-gpu-smoke-test.py` | Verify GPU, CUDA, and container toolkit |
| `scripts/spark-gpu-throttle-test.py` | Test GPU throttle behavior under load |
| `scripts/spark-a3b-long-context-harness.py` | Long-context inference test |
| `scripts/gpu-persistent-setting.sh` | Apply persistent GPU mode + clock locks |
| `scripts/litellm-claude-smoke-test.sh` | Validate Claude Code discovery + routing |
| `scripts/nvidia_system_info.py` | Report GPU system information |

## CI/CD (GitHub Actions)

| Workflow | Trigger | What it does |
|---|---|---|
| `lint.yml` | Push/PR to main | YAML lint, ShellCheck, Python syntax |
| `docker-build.yml` | Push to main/tags | Build & push `llama-cpp-dgx` to GHCR |
| `deploy-docs.yml` | Push to main | Deploy MkDocs site to GitHub Pages |
