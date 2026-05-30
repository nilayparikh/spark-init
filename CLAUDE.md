# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`.init` is a modular Docker Compose platform for local AI inference and observability on NVIDIA DGX/Spark hardware. It brings together data storage (PostgreSQL), full-stack observability (Grafana/Mimir/Loki/Alloy/DCGM), and OpenAI-compatible AI inference (LiteLLM + llama.cpp) — all composable via Docker Compose profiles.

## Big-Picture Architecture

Three layers, each independently composable through `COMPOSE_PROFILES`. Every service
also has its own unique profile for fine-grained control:

| Layer             | Directory        | Services                                    | Stack Profiles                 | Unique Profiles |
| ----------------- | ---------------- | ------------------------------------------- | ------------------------------ | --------------- |
| **Data**          | `data/`          | PostgreSQL                                  | `data`                         | `postgres`      |
| **Observability** | `observability/` | Mimir, Loki, Alloy, Grafana, DCGM, cAdvisor | `obs`                          | `mimir`, `loki`, `alloy`, `grafana`, `gpu-telemetry`, `cadvisor` |
| **Interfaces**    | `interfaces/`    | LiteLLM proxy, llama.cpp backend            | `interface`                    | `litellm`, `llama-qwen-3-6-27b`, `llama-qwen-3-6-35b-a3b` |
| **Network**       | `network/`       | Cloudflare Tunnel                           | —                              | `cloudflared`  |

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
# Full stack (all layers + both llama.cpp backends)
docker compose up -d

# Check status
docker compose ps

# Stop everything
docker compose down
```

### Profile Selection

Each service has a unique profile. Stack profiles (`data`, `obs`, `interface`) activate
all services in a layer. Use `all` to start everything.

Edit `COMPOSE_PROFILES` in `.env`, then run `docker compose up -d`. Common shapes:

```
# Full stack (all layers + both llama.cpp backends)
COMPOSE_PROFILES=data,obs,interface

# Everything (shorthand)
COMPOSE_PROFILES=all

# Data + observability only
COMPOSE_PROFILES=data,obs

# LiteLLM + 27B only (no observability)
COMPOSE_PROFILES=data,litellm,llama-qwen-3-6-27b

# API proxy only (cloud models, no local llama.cpp)
COMPOSE_PROFILES=data,litellm

# Just a single service (e.g., PostgreSQL only)
COMPOSE_PROFILES=postgres
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

### Secret Protection

A single Trivy-based hook replaces the old multi-hook system:

| Component | What it does |
|-----------|-------------|
| **PostToolUse hook** | `.claude/hooks/trivy-scan.sh` — scans every written file for secrets and misconfigurations using Trivy (scanners: `secret`, `misconfig`; severity: CRITICAL, HIGH, MEDIUM) |
| **CI workflow** | `.github/workflows/trivy.yml` — full repo scan on push/PR + daily scheduled scan |
| **Custom rules** | `trivy-secret.yaml` — project-specific patterns (OpenAI keys, DB connection strings) |
| **Sync check** | `.claude/hooks/compare-env.sh` — run `! .claude/hooks/compare-env.sh` at session end to compare `.env` vs `.env.example` key names |

**Working with secrets:**

- **Always** use `.env.example` for template changes (never `.env` directly)
- **Never** hardcode a secret in source code — reference it via an environment variable
- **At session end**, run `! .claude/hooks/compare-env.sh` to check if `.env` needs updating
- **Secret values in .env** can only be checked by the user directly (`grep VAR .env`)
- **False positives** → add allow-rules to `trivy-secret.yaml`

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
- `trivy.yml` — Full repo secret + misconfig scan on push/PR + daily schedule
- `docker-build-llama-cpp-dgx.yml` — Build and push `llama-cpp-dgx` image to GHCR on push to main/tags
- `docker-build-claude-code.yml` — Build and push `claude-code` image to GHCR on push to main/tags
- `deploy-docs.yml` — Deploy MkDocs site

## Building Docker Images

```bash
# llama-cpp-dgx
docker build -t ghcr.io/nilayparikh/llama-cpp-dgx:cuda13.1.2-b9222 \
  -f docker/llama-cpp-dgx/Dockerfile .

# claude-code
docker build -t ghcr.io/nilayparikh/claude-code:v0.0.1 \
  -f docker/claude-code/Dockerfile docker/claude-code/
```

Each image is also built by CI when its `docker/<image>/` directory changes.

## `claude-code.sh`

Launches an isolated Claude Code container (NVIDIA PyTorch base) routed through the local LiteLLM proxy. It:

1. Parses `.env` for model routing and auth tokens
2. Builds the container image from `docker/claude-code/Dockerfile` if not cached
3. Runs Claude Code with `ANTHROPIC_BASE_URL` pointing to the LiteLLM proxy at `http://barsana.local:4000`

The image uses `.INIT/Pro`, `.INIT/Flash`, `.INIT/Ultra` model aliases mapped to the LiteLLM backends (see `claude-code.sh` for the full routing table).

## File Map (for AI Agents)

This indexed catalog covers all source files, configuration, and documentation. Use it to locate any file without searching.

### Root-Level

| File | Purpose |
| -------------------- | --------------------------------------------------------- |
| `docker-compose.yml` | Root compose — includes all sub-compose files via `include:` |
| `.env.example` | All configurable variables with defaults and descriptions |
| `claude-code.sh` | Launch Claude Code container routed through LiteLLM proxy |
| `mkdocs.yml` | MkDocs site configuration (Material theme) |
| `CLAUDE.md` | This file — guidance for AI agents |
| `.claude/hooks/` | Trivy-based security scanning hooks |
| `trivy.yaml` | Trivy scan strategy reference |
| `trivy-secret.yaml` | Custom Trivy secret rules (OpenAI keys, DB strings) |

### Data Layer (`data/`)

| File | Purpose |
| ---------------------------------------------------- | --------------------------------------------------------- |
| `data/docker-compose.data.yml` | PostgreSQL service definition with health check |
| `data/config/postgres-init/010-grafana.sh` | Creates Grafana database + user on first start |
| `data/config/postgres-init/020-litellm-interface.sh` | Creates LiteLLM database + user on first start |

### Interfaces Layer (`interfaces/`)

| File | Purpose |
| -------------------------------------------------------- | --------------------------------------------------------- |
| `interfaces/docker-compose.interface.yml` | LiteLLM proxy + llama.cpp service definitions (all flags documented inline) |
| `interfaces/config/litellm/config.yaml` | LiteLLM routing: provider includes, model_group_alias, retry policy |
| `interfaces/config/litellm/providers/dgx-spark.yaml` | Local DGX model routing (27B + 35B A3B) |
| `interfaces/config/litellm/providers/azure-foundry.yaml` | Azure Foundry cloud models |
| `interfaces/config/litellm/providers/deepseek.yaml` | DeepSeek native API |
| `interfaces/config/litellm/providers/nvidia.yaml` | NVIDIA AI Endpoints |
| `interfaces/config/litellm/providers/opencode-zen.yaml` | OpenCode Zen models |
| `interfaces/config/qwen3.6/chat_template.jinja` | Jinja2 chat template for Qwen 3.6 (reasoning format) |

### Docker Layer (`docker/`)

| File | Purpose |
| ---------------------------------------------------- | --------------------------------------------------------- |
| `docker/llama-cpp-dgx/Dockerfile` | llama.cpp CUDA Docker image (aarch64, CUDA 13.1.2) |
| `docker/claude-code/Dockerfile` | Claude Code dev container (NVIDIA PyTorch, aarch64) |
| `docker/README.md` | Build instructions and OCI label reference |

### Observability Layer (`observability/`)

| File | Purpose |
| -------------------------------------------- | --------------------------------------------------------- |
| `observability/docker-compose.obs.yml` | Mimir, Loki, Alloy, cAdvisor, DCGM, Grafana service definitions |
| `observability/config/config.alloy` | Grafana Alloy pipeline — scrape configs + label conventions (all inline) |
| `observability/config/loki-config.yaml` | Loki single-binary storage config |
| `observability/config/mimir-config.yaml` | Mimir single-binary storage config |
| `observability/config/grafana/provisioning/datasources/` | Mimir + Loki data source definitions |
| `observability/config/grafana/provisioning/dashboards/machine/` | JSON dashboard definitions (7 dashboards) |
| `observability/config/grafana/provisioning/alerting/machine-alerts.yaml` | Alert rules (GPU thermal, filesystem, host saturation) |

### Network (`network/`)

| File | Purpose |
| ----------------------------- | --------------------------------------------------------- |
| `network/docker-compose.yaml` | Cloudflare Tunnel service for external access |

### Scripts (`scripts/`)

| File | Purpose |
| ------------------------------------------- | --------------------------------------------------------- |
| `scripts/gpu-persistent-setting.sh` | Apply persistent GPU mode + lock clock speeds |
| `scripts/litellm-claude-smoke-test.sh` | Validate Claude Code model discovery + routing |
| `scripts/spark-gpu-smoke-test.py` | Verify GPU, CUDA, and container toolkit |
| `scripts/spark-gpu-throttle-test.py` | GPU throttle behavior testing |
| `scripts/spark-a3b-long-context-harness.py` | Long-context inference benchmark |
| `scripts/nvidia_system_info.py` | System information reporter |

### Documentation (`docs/`)

| File | Purpose (Human-First) |
| --------------------------------------------------------- | --------------------------------------------------------- |
| `docs/index.md` | Project overview and quick start |
| `docs/quickstart.md` | 5-minute getting-started guide |
| `docs/capabilities.md` | Feature-driven capability reference |
| `docs/architecture.md` | High-level architecture (one diagram, three layers) |
| `docs/configuration.md` | How-to configure (profiles, .env) |
| `docs/guides.md` | Task-oriented recipes (add model, GPU tuning, troubleshooting) |
| `docs/reference.md` | Quick-lookup tables (models, ports, scripts) |

### GitHub CI (`.github/workflows/`)

| File | Purpose |
| --------------------------------------------------------- | --------------------------------------------------------- |
| `.github/workflows/lint.yml` | YAML lint, ShellCheck, Python syntax on push/PR |
| `.github/workflows/trivy.yml` | Full repo secret + misconfig scan on push/PR + daily |
| `.github/workflows/docker-build-llama-cpp-dgx.yml` | Build `llama-cpp-dgx` image and push to GHCR |
| `.github/workflows/docker-build-claude-code.yml` | Build `claude-code` image and push to GHCR |
| `.github/workflows/deploy-docs.yml` | Deploy MkDocs site to GitHub Pages |

## Submodules

- `third-party/llama.cpp/` — inference backend (ggml-org/llama.cpp)
- `models/qwen3.6-27b-text-nvfp4-mtp/` — Qwen 3.6 27B GGUF model weights
- `models/qwen3.6-35b-a3b-nvfp4-mtp/` — Qwen 3.6 35B A3B GGUF model weights

All initialized via `git submodule update --init --recursive`.
