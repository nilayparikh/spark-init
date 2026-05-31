# .init

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Docker Compose](https://img.shields.io/badge/docker%20compose-2.24+-brightgreen.svg)](docker-compose.yml)
[![Platform](https://img.shields.io/badge/platform-dgx--spark--arm64-lightgrey.svg)](README.md)
[![CI](https://github.com/nilayparikh/spark-init/actions/workflows/lint.yml/badge.svg)](https://github.com/nilayparikh/spark-init/actions/workflows/lint.yml)

**AI-augmented software engineering, on your NVIDIA DGX Spark.**

`.init` is a single Docker Compose stack that turns your **DGX Spark** (GB10, SM120/SM121) into a private AI inference server. It gives you local Qwen 3.6 LLMs (NVFP4, MTP speculative decoding) behind an OpenAI-compatible API, full GPU observability, and optional cloud model routing — all from one `.env` file.

## Why DGX Spark?

This stack is purpose-built for DGX Spark's specific hardware boundary:

| Constraint                | How .init Handles It                                            |
| ------------------------- | --------------------------------------------------------------- |
| **SM120/SM121 compute**   | llama.cpp only — no vLLM (NVFP4 kernels need server-class TMEM) |
| **128 GB unified memory** | Models sized to fit with 50%+ overhead for OS + tools           |
| **No server-class TMEM**  | GGUF loads weights directly — no layout transformations needed  |
| **ARM64 (Grace CPU)**     | All containers built for `linux/arm64`                          |
| **Driver 580.x**          | Compatible without forced upgrades                              |

We use **NVFP4 quantization** (NVIDIA ModelOpt) with **MTP speculative decoding** for the best speed-to-quality ratio on DGX Spark hardware: ~40 tok/s for the 27B, ~30 tok/s for the 35B A3B.

## Three Layers

| Layer             | Directory        | Services                                    | Stack Profile |
| ----------------- | ---------------- | ------------------------------------------- | ------------- |
| **Data**          | `data/`          | PostgreSQL                                  | `data`        |
| **Observability** | `observability/` | Alloy, Mimir, Loki, Grafana, DCGM, cAdvisor | `obs`         |
| **Interfaces**    | `interfaces/`    | LiteLLM proxy, llama.cpp (27B + 35B A3B)    | `interface`   |
| **Network**       | `network/`       | Cloudflare Tunnel                           | `cloudflared` |

All layers share the `init_default` external network. Each layer has its own `README.md` for details.

## Quick Start

```bash
git clone https://github.com/nilayparikh/spark-init.git
cd spark-init
git submodule update --init --recursive

# Copy the secrets template and fill in your values
cp .env.secrets.example .env.secrets
# edit .env.secrets: add your LITELLM_MASTER_KEY and other secrets

docker compose --env-file .env --env-file .env.secrets up -d
```

### Environment Files

Two files — `.env` (tracked, safe defaults) and `.env.secrets` (gitignored, secrets only):

| File                   | Purpose                             | Committed?    |
| ---------------------- | ----------------------------------- | ------------- |
| `.env`                 | All safe defaults and configuration | ✅ Git        |
| `.env.secrets.example` | Template for secrets                | ✅ Git        |
| `.env.secrets`         | Your actual secrets                 | ❌ Gitignored |

**Interpolation order** (later overrides earlier): `.env` → `.env.secrets`

To change your stack shape, edit `COMPOSE_PROFILES` in `.env`. Common profiles:

```bash
# Full stack
COMPOSE_PROFILES=data,obs,interface

# 27B only, no observability
COMPOSE_PROFILES=data,litellm,llama-qwen-3-6-27b

# Cloud providers only, no local models
COMPOSE_PROFILES=data,litellm
```

To add a new variable: add it to `.env` (with a safe default). If it's a secret, also add it to `.env.secrets.example`.

## Profile Sets

The top-level `COMPOSE_PROFILES` controls which services start. Each service also
has a unique profile for fine-grained control.

| Profile Set                       | What You Get                                    |
| --------------------------------- | ----------------------------------------------- |
| `all`                             | Everything — full stack                         |
| `data,obs,interface`              | Full stack w/ both llama.cpp backends (default) |
| `data,obs`                        | Telemetry only (no inference)                   |
| `data,litellm,llama-qwen-3-6-27b` | LiteLLM + 27B only                              |
| `data,litellm`                    | API proxy only (cloud models)                   |
| `data`                            | Just PostgreSQL                                 |

**Per-service profiles** — use alongside stack profiles for fine-grained control:

| Service              | Profile                  |
| -------------------- | ------------------------ |
| PostgreSQL           | `postgres`               |
| Mimir                | `mimir`                  |
| Loki                 | `loki`                   |
| Alloy                | `alloy`                  |
| GPU Telemetry (DCGM) | `gpu-telemetry`          |
| cAdvisor             | `cadvisor`               |
| Grafana              | `grafana`                |
| LiteLLM              | `litellm`                |
| llama.cpp 27B        | `llama-qwen-3-6-27b`     |
| llama.cpp 35B A3B    | `llama-qwen-3-6-35b-a3b` |
| Cloudflare Tunnel    | `cloudflared`            |

## Endpoints

| Service       | URL                        | Auth                       |
| ------------- | -------------------------- | -------------------------- |
| LiteLLM proxy | `http://localhost:4000`    | `LITELLM_MASTER_KEY`       |
| llama.cpp 27B | `http://localhost:8000/v1` | None                       |
| llama.cpp 35B | `http://localhost:8001/v1` | None                       |
| Grafana       | `http://localhost:3000`    | Admin password from `.env` |

## Learn More

- [Quick Start](docs/quickstart.md) — 5-minute setup
- [Capabilities](docs/capabilities.md) — what you can do
- [Architecture](docs/architecture.md) — how it fits together
- [Configuration](docs/configuration.md) — .env and profiles
- [Guides](docs/guides.md) — adding models, GPU tuning, troubleshooting
- [Reference](docs/reference.md) — cheat-sheet tables

## Directory READMEs

| Directory                                   | Content                             |
| ------------------------------------------- | ----------------------------------- |
| [`data/`](data/README.md)                   | PostgreSQL persistence layer        |
| [`docker/`](docker/README.md)               | Claude Code dev container           |
| [`interfaces/`](interfaces/README.md)       | LiteLLM proxy + llama.cpp inference |
| [`models/`](models/README.md)               | NVFP4 GGUF model weights            |
| [`network/`](network/README.md)             | Docker network + Cloudflare Tunnel  |
| [`observability/`](observability/README.md) | Metrics, logs, and dashboards       |
| [`third-party/`](third-party/README.md)     | llama.cpp submodule                 |

## License

Apache 2.0 — see [LICENSE](LICENSE). Copyright 2025 .init contributors.
