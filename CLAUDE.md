# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`.init` is a modular Docker Compose platform for local AI inference and observability on NVIDIA DGX/Spark hardware. It brings together data storage (PostgreSQL), full-stack observability (Grafana/Mimir/Loki/Alloy/DCGM), and OpenAI-compatible AI inference (LiteLLM + llama.cpp) — all composable via Docker Compose profiles.

## Big-Picture Architecture

Three layers, each independently composable through `COMPOSE_PROFILES`:

| Layer             | Directory        | Services                                    | Profile(s)                        |
| ----------------- | ---------------- | ------------------------------------------- | --------------------------------- |
| **Data**          | `data/`          | PostgreSQL                                  | `data`                            |
| **Observability** | `observability/` | Mimir, Loki, Alloy, Grafana, DCGM, cAdvisor | `obs`                             |
| **Interfaces**    | `interfaces/`    | LiteLLM proxy, llama.cpp backend            | `interface`, `llama-qwen-3-6-27b` |

Data flow: clients → LiteLLM proxy (`:4000`) → llama.cpp (`:8000`) → GPU. Alloy scrapes all services and streams to Mimir/Loki for Grafana visualization. All services share the `init_default` Docker network.

### Compose Structure

- Root `docker-compose.yml` includes all sub-compose files via `include:`
- Each layer has its own compose file: `data/docker-compose.data.yml`, `observability/docker-compose.obs.yml`, `interfaces/docker-compose.interface.yml`
- `network/docker-compose.yaml` defines the shared external network
- `.env` is the switchboard — `COMPOSE_PROFILES` controls which services start

### Key Dependencies

- `interface` requires `data` (Postgres for LiteLLM)
- `obs` requires `data` (Postgres for Grafana)
- `llama-qwen-3-6-27b` is independent of `obs`
- `third-party/llama.cpp/` is a git submodule providing the inference backend

## Working with the Stack

### Start/Stop

```bash
# Full stack (data + obs + interface + llama.cpp)
docker compose up -d

# Check status
docker compose ps

# Stop everything
docker compose down
```

### Profile Selection

Edit `COMPOSE_PROFILES` in `.env`, then run `docker compose up -d`. Common shapes:

```
# Full stack
COMPOSE_PROFILES=data,obs,interface,llama-qwen-3-6-27b

# Data + observability only
COMPOSE_PROFILES=data,obs

# Interface only (with data)
COMPOSE_PROFILES=data,interface,llama-qwen-3-6-27b
```

### Endpoints

| Service       | URL                        | Auth                                          |
| ------------- | -------------------------- | --------------------------------------------- |
| LiteLLM proxy | `http://localhost:4000`    | `LITELLM_MASTER_KEY`                          |
| llama.cpp     | `http://localhost:8000/v1` | None                                          |
| Grafana       | `http://<host>:3000`       | `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD` |

### Environment

Copy `.env.example` to `.env` and update secrets and paths. Before first use, also initialize submodules:

```bash
cp .env.example .env
git submodule update --init --recursive
```

Critical settings:

- `LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH` — must point to a valid GGUF model file on disk
- `LITELLM_MASTER_KEY` — auth key for the proxy

## Linting & CI

No test suite — this is an infrastructure repository. CI runs three lint jobs:

```bash
# YAML lint (docker-compose files + configs)
pip install yamllint
yamllint -d "{extends: default, rules: {line-length: disable, truthy: disable}}" \
  $(find . -name 'docker-compose*.yml' -o -name '*.yaml' -path '*/config/*')

# Shell lint
shellcheck scripts/*.sh data/config/postgres-init/*.sh

# Python syntax check
find scripts/ -name '*.py' -print0 | xargs -0 -I{} python3 -m py_compile {}
```

GitHub Actions (`.github/workflows/`):

- `lint.yml` — YAML, ShellCheck, Python syntax on push/PR to main
- `docker-build.yml` — Build and push `llama-cpp-dgx` image to GHCR on push to main/tags
- `deploy-docs.yml` — Deploy MkDocs site

## Building the llama.cpp Docker Image

```bash
# Build locally (arm64)
docker build -t nilayparikh/llama-cpp-dgx:cuda13.1.2-b9222 \
  -f interfaces/dockerfiles/Dockerfile interfaces/dockerfiles/
```

The image is also built by CI when `interfaces/dockerfiles/` changes.

## `claude-code.sh`

Launches an isolated Claude Code container (NVIDIA PyTorch base) routed through the local LiteLLM proxy. It:

1. Parses `.env` for model routing and auth tokens
2. Builds the container image from `docker/claude-code/Dockerfile` if not cached
3. Runs Claude Code with `ANTHROPIC_BASE_URL` pointing to the LiteLLM proxy at `http://barsana.local:4000`

The image uses `.INIT/Pro`, `.INIT/Flash`, `.INIT/Ultra` model aliases mapped to the LiteLLM backends (see `claude-code.sh` for the full routing table).

## Key Files to Know

| File                                            | Purpose                                                |
| ----------------------------------------------- | ------------------------------------------------------ |
| `.env.example`                                  | Template for local `.env` — all configurable variables |
| `docker-compose.yml`                            | Root compose — includes all sub-compose files          |
| `interfaces/config/litellm/config.yaml`         | LiteLLM provider routing config                        |
| `interfaces/config/qwen3.6/chat_template.jinja` | Chat template for Qwen 3.6                             |
| `observability/config/config.alloy`             | Alloy collector configuration                          |
| `observability/config/grafana/provisioning/`    | Grafana dashboards & data sources                      |
| `data/config/postgres-init/`                    | Database bootstrap scripts                             |
| `scripts/`                                      | GPU smoke tests, harness scripts                       |
| `docs/`                                         | MkDocs documentation site                              |

## Documentation

The docs site is built with MkDocs (`mkdocs.yml`). Source lives in `docs/`. Deploy via `deploy-docs.yml` workflow.

## Submodules

- `third-party/llama.cpp/` — inference backend (ggml-org/llama.cpp)
- `models/qwen3.6-27b-text-nvfp4-mtp/` — Qwen 3.6 27B GGUF model weights
- `models/qwen3.6-35b-a3b-nvfp4-mtp/` — Qwen 3.6 35B A3B GGUF model weights

All initialized via `git submodule update --init --recursive`.
