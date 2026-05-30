# .init Stack

**Modular Docker Compose platform for local AI inference and observability on NVIDIA hardware.**

`.init` is a composable, profile-driven platform that brings together data storage, full-stack observability, and OpenAI-compatible AI inference — all running locally on NVIDIA GPU hardware. Whether you're prototyping with Qwen 3.6 models or building production-grade agent infrastructure, `.init` provides the building blocks to go from zero to running in minutes.

## Three-Layer Architecture

The platform is organized into three independent layers, each defined in its own Docker Compose file and included by the root `docker-compose.yml`:

| Layer             | Directory          | Services                                                                                         |
|-------------------|--------------------|--------------------------------------------------------------------------------------------------|
| **Data**          | `data/`            | PostgreSQL — shared persistence for LiteLLM, Grafana, and any downstream integrations.           |
| **Observability** | `observability/`   | Alloy, Grafana, Mimir (metrics), Loki (logs), and GPU telemetry via DCGM.                        |
| **Interfaces**    | `interfaces/`      | LiteLLM proxy with multi-provider routing, llama.cpp inference backend.                          |

Each layer is activated independently through Docker Compose profiles, so you can run just the data + observability stack for monitoring, or add one or more inference backends on top without touching other services.

## Key Features

- **Profile-driven Compose** — Mix and match services with a single `COMPOSE_PROFILES` environment variable; no need to juggle multiple compose files.
- **OpenAI-compatible API** — LiteLLM proxy on port `4000` with multi-provider routing, authentication, and Claude compatibility aliases for agent clients.
- **Full observability stack** — Metrics (Mimir), logs (Loki), distributed tracing, and GPU telemetry via DCGM, all visualized in Grafana.
- **GPU telemetry** — Real-time monitoring of NVIDIA GPU utilization, memory, and power through `nvidia-dcgm-exporter` wired into the Alloy collector.
- **llama.cpp backend** — CUDA-accelerated inference for GGUF-quantized models, wired to the proxy endpoint on port `8000`.
- **Qwen 3.6 model support** — Pre-configured recipes for Standard (Qwen 3.6 27B) and Lite variants, optimized for NVIDIA Blackwell/Ada GPUs with MTP (Multi-Token Prediction).

## Quick Start

```bash
# Clone and enter the repository
git clone https://github.com/nilayparikh/init-stack.git
cd init-stack

# Initialize submodules (llama.cpp backend + model weights)
git submodule update --init --recursive

# Configure environment and secrets
cp .env.example .env
# Edit .env — set LITELLM_MASTER_KEY, model paths, and COMPOSE_PROFILES

# Start the stack
docker compose up -d
```

## What Happens Next

The default profile set (`data,obs,interface,llama-qwen-3-6-27b`) will start:

1. **PostgreSQL** — database for LiteLLM and Grafana.
2. **Observability stack** — Alloy, Mimir, Loki, Grafana, and GPU telemetry.
3. **LiteLLM proxy** — OpenAI-compatible API on `http://localhost:4000`.
4. **llama.cpp 27B backend** — Qwen 3.6 inference on `http://localhost:8000/v1`.

Verify with `docker compose ps` and check the health endpoints listed in the [Quick Start guide](getting-started/quickstart.md).

## Documentation

- **[Quick Start](getting-started/quickstart.md)** — 5-minute guide to get a full stack running.
- **[Prerequisites](getting-started/prerequisites.md)** — Docker, NVIDIA driver, and toolkit requirements.
- **Architecture** — Deep dives into the inference stack, observability stack, and networking.
- **Configuration** — Docker Compose profiles, environment variables, and custom configs.
- **Guides** — Adding models, GPU configuration, observability setup, and troubleshooting.

## Project Structure

```
.init/
├── docker-compose.yml              # Root entrypoint (includes all layers)
├── .env.example                    # Environment template with profile defaults
│
├── data/                           # Data layer
│   ├── docker-compose.data.yml     # PostgreSQL service definition
│   └── config/postgres-init/       # Database bootstrap scripts
│
├── observability/                  # Observability layer
│   ├── docker-compose.obs.yml      # Alloy, Grafana, Mimir, Loki, DCGM
│   └── config/                     # Collector and dashboard configs
│
├── interfaces/                     # Interfaces layer
│   ├── docker-compose.interface.yml  # LiteLLM, llama.cpp services
│   ├── config/litellm/             # Proxy model catalog and routing
│   ├── config/qwen3.6/             # Chat templates for Qwen 3.6
│   └── dockerfiles/                # Custom Docker images (llama.cpp CUDA build)
│
├── models/                         # Model weight submodules (GGUF files)
├── third-party/                    # Vendored dependencies (llama.cpp, etc.)
└── docs/                           # This documentation site
```

## License

Apache 2.0 — see [LICENSE](https://github.com/nilayparikh/init-stack/blob/main/LICENSE).
