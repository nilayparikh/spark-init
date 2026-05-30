# File Index

Master file catalog for the `.init` project. This index covers all source files, configuration, and documentation — excluding third-party submodule internals (`third-party/llama.cpp/`), runtime data, and build artifacts.

## Root-Level Files

| File                 | Description                                               |
| -------------------- | --------------------------------------------------------- |
| `docker-compose.yml` | Root compose file — includes all sub-compose files        |
| `.env.example`       | Environment variable template (copy to `.env`)            |
| `claude-code.sh`     | Launch Claude Code container routed through LiteLLM proxy |
| `mkdocs.yml`         | MkDocs site configuration                                 |
| `CLAUDE.md`          | Instructions for Claude Code (AI assistant context)       |

## `.github/` — GitHub Configuration

| File                                 | Description                                 |
| ------------------------------------ | ------------------------------------------- |
| `.github/workflows/lint.yml`         | YAML lint, ShellCheck, Python syntax checks |
| `.github/workflows/docker-build.yml` | Build and push llama.cpp Docker image       |
| `.github/workflows/deploy-docs.yml`  | Deploy MkDocs site to GitHub Pages          |

## `data/` — Data Layer

| File                                                 | Description                                 |
| ---------------------------------------------------- | ------------------------------------------- |
| `data/docker-compose.data.yml`                       | PostgreSQL service definition               |
| `data/config/postgres-init/010-grafana.sh`           | Grafana database bootstrap script           |
| `data/config/postgres-init/020-litellm-interface.sh` | LiteLLM interface database bootstrap script |

## `docs/` — Documentation Site (Canonical Location)

All documentation lives here. Per-layer `docs/` subdirectories have been consolidated into this single location.

| File                                          | Description                                                |
| --------------------------------------------- | ---------------------------------------------------------- |
| `docs/index.md`                               | Site home — project overview and quick start               |
| `docs/getting-started/quickstart.md`          | 5-minute Docker Compose spin-up guide                      |
| `docs/getting-started/prerequisites.md`       | System requirements (GPU, Docker, drivers)                 |
| `docs/architecture/overview.md`               | High-level component diagram and data flow                 |
| `docs/architecture/inference-stack.md`        | llama.cpp layer architecture                               |
| `docs/architecture/observability-stack.md`    | Grafana, Loki, Mimir, Alloy architecture                   |
| `docs/architecture/networking.md`             | Docker networks and service discovery                      |
| `docs/configuration/docker-compose.md`        | Compose file reference — profiles, services, ports         |
| `docs/configuration/environment-variables.md` | Full environment variable catalog                          |
| `docs/configuration/custom-configs.md`        | LiteLLM config and chat templates                          |
| `docs/guides/adding-models.md`                | How to add new GGUF models                                 |
| `docs/guides/observability-setup.md`          | Wiring metrics, logs, and traces                           |
| `docs/guides/gpu-configuration.md`            | GPU passthrough, persistent settings, DCGM                 |
| `docs/guides/troubleshooting.md`              | Common issues and fixes                                    |
| `docs/api/openai-compatible.md`               | Inference API reference                                    |
| `docs/interfaces/developer-clients.md`        | Developer client configuration (Claude Code, IDEs, agents) |
| `docs/observability/labeling.md`              | Label taxonomy and conventions                             |
| `docs/observability/log-coverage.md`          | Log source coverage matrix                                 |
| `docs/observability/dashboard-standards.md`   | Dashboard design standards                                 |
| `docs/observability/interface-telemetry.md`   | Telemetry labeling standards for interfaces                |
| `docs/observability/llamacpp-telemetry.md`    | llama.cpp telemetry specifics                              |
| `docs/reference/file-index.md`                | This file — master file catalog                            |
| `docs/reference/docker-images.md`             | Docker images and tags                                     |
| `docs/contributing/development.md`            | Local development setup                                    |
| `docs/contributing/docs-guide.md`             | How to contribute to documentation                         |

## `interfaces/` — Interface Layer

| File                                                     | Description                                          |
| -------------------------------------------------------- | ---------------------------------------------------- |
| `interfaces/docker-compose.interface.yml`                | LiteLLM proxy and llama.cpp service definitions      |
| `interfaces/interface.md`                                | Interface layer quick reference                      |
| `interfaces/config/litellm/config.yaml`                  | LiteLLM proxy configuration (routing, retries, auth) |
| `interfaces/config/litellm/providers/dgx.yaml`           | DGX provider routing config                          |
| `interfaces/config/litellm/providers/azure-foundry.yaml` | Azure Foundry provider routing config                |
| `interfaces/config/litellm/providers/nvidia.yaml`        | NVIDIA provider routing config                       |
| `interfaces/config/litellm/providers/deepseek.yaml`      | DeepSeek provider routing config                     |
| `interfaces/config/litellm/providers/opencode-zen.yaml`  | OpenCode Zen provider routing config                 |
| `interfaces/config/qwen3.6/chat_template.jinja`          | Chat template for Qwen 3.6 model                     |
| `interfaces/dockerfiles/Dockerfile`                      | llama.cpp Docker image build definition              |

## `network/` — Network Configuration

| File                          | Description                                     |
| ----------------------------- | ----------------------------------------------- |
| `network/docker-compose.yaml` | Shared external Docker network (`init_default`) |

## `observability/` — Observability Layer

| File                                         | Description                                          |
| -------------------------------------------- | ---------------------------------------------------- |
| `observability/docker-compose.obs.yml`       | Grafana, Mimir, Loki, Alloy, cAdvisor, DCGM services |
| `observability/config/config.alloy`          | Grafana Alloy collector configuration                |
| `observability/config/loki-config.yaml`      | Loki log storage configuration                       |
| `observability/config/mimir-config.yaml`     | Mimir metrics storage configuration                  |
| `observability/config/grafana/provisioning/` | Grafana dashboard and datasource provisioning        |

## `scripts/` — Utility Scripts

| File                                        | Description                                      |
| ------------------------------------------- | ------------------------------------------------ |
| `scripts/gpu-persistent-setting.sh`         | Apply persistent GPU mode and clock limits       |
| `scripts/litellm-claude-smoke-test.sh`      | Smoke test for Claude Code discovery + routing   |
| `scripts/nvidia_system_info.py`             | NVIDIA system information reporter               |
| `scripts/spark-gpu-smoke-test.py`           | GPU smoke test (driver, CUDA, container toolkit) |
| `scripts/spark-gpu-throttle-test.py`        | GPU throttle behavior test                       |
| `scripts/spark-a3b-long-context-harness.py` | Long context inference test harness              |

## `third-party/` — Third-Party Dependencies

| File                     | Description                                              |
| ------------------------ | -------------------------------------------------------- |
| `third-party/README.md`  | Third-party dependency overview                          |
| `third-party/llama.cpp/` | Git submodule — llama.cpp inference engine (MIT license) |
