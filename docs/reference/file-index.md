# File Index

Master file catalog for the `.init` project. This index covers all source files, configuration, and documentation — excluding third-party submodule internals (`third-party/llama.cpp/`), runtime data, and build artifacts.

## Root-Level Files

| File | Description |
|------|-------------|
| `README.md` | Project overview, architecture diagram, quick start |
| `LICENSE` | Apache 2.0 license |
| `NOTICE` | Third-party dependency attributions |
| `CONTRIBUTING.md` | Contribution guidelines and development workflow |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 |
| `SECURITY.md` | Vulnerability disclosure policy |
| `CHANGELOG.md` | Release notes |
| `CLAUDE.md` | Instructions for Claude Code (AI assistant context) |
| `docker-compose.yml` | Root compose file — includes all sub-compose files |
| `docker_best_practice.md` | Docker best practices reference |
| `.env.example` | Environment variable template (copy to `.env`) |
| `.gitignore` | Git exclusions (secrets, caches, models, build outputs) |
| `.gitmodules` | Git submodule definitions |
| `.editorconfig` | Editor configuration for consistent formatting |
| `.mcp.json` | Model Context Protocol configuration |
| `mkdocs.yml` | MkDocs site configuration |
| `claude-code.sh` | Launch Claude Code container routed through LiteLLM proxy |
| `skills-lock.json` | Claude Code skills lockfile |

## `.github/` — GitHub Configuration

| File | Description |
|------|-------------|
| `.github/CODEOWNERS` | Directory ownership and review requirements |
| `.github/dependabot.yml` | Automated dependency updates |
| `.github/PULL_REQUEST_TEMPLATE.md` | Pull request template |
| `.github/ISSUE_TEMPLATE/bug-report.yml` | Structured bug report form |
| `.github/ISSUE_TEMPLATE/feature-request.yml` | Structured feature request form |
| `.github/workflows/lint.yml` | YAML lint, ShellCheck, Python syntax checks |
| `.github/workflows/docker-build.yml` | Build and push llama.cpp Docker image |
| `.github/workflows/deploy-docs.yml` | Deploy MkDocs site to GitHub Pages |

## `.devcontainer/` — Dev Container

| File | Description |
|------|-------------|
| `.devcontainer/devcontainer.json` | VS Code Dev Container configuration |
| `.devcontainer/Dockerfile` | Dev container image definition |

## `data/` — Data Layer

| File | Description |
|------|-------------|
| `data/docker-compose.data.yml` | PostgreSQL service definition |
| `data/config/postgres-init/010-grafana.sh` | Grafana database bootstrap script |
| `data/config/postgres-init/020-litellm-interface.sh` | LiteLLM interface database bootstrap script |
| `data/docs/README.md` | Data layer documentation |
| `data/docs/env-reference.md` | Data layer environment variables |
| `data/docs/file-index.md` | Data layer file index (legacy) |

## `docs/` — Documentation Site

| File | Description |
|------|-------------|
| `docs/index.md` | Site home — project overview and quick start |
| `docs/go-live.md` | Open-source release checklist |
| `docs/getting-started/quickstart.md` | 5-minute Docker Compose spin-up guide |
| `docs/getting-started/prerequisites.md` | System requirements (GPU, Docker, drivers) |
| `docs/architecture/overview.md` | High-level component diagram and data flow |
| `docs/architecture/inference-stack.md` | llama.cpp / vLLM layer architecture |
| `docs/architecture/observability-stack.md` | Grafana, Loki, Mimir, Alloy architecture |
| `docs/architecture/networking.md` | Docker networks and service discovery |
| `docs/configuration/docker-compose.md` | Compose file reference — profiles, services, ports |
| `docs/configuration/environment-variables.md` | Full environment variable catalog |
| `docs/configuration/custom-configs.md` | LiteLLM config and chat templates |
| `docs/guides/adding-models.md` | How to add new GGUF models |
| `docs/guides/observability-setup.md` | Wiring metrics, logs, and traces |
| `docs/guides/gpu-configuration.md` | GPU passthrough, persistent settings, DCGM |
| `docs/guides/troubleshooting.md` | Common issues and fixes |
| `docs/api/openai-compatible.md` | Inference API reference |
| `docs/reference/file-index.md` | This file — master file catalog |
| `docs/reference/docker-images.md` | Docker images and tags |
| `docs/contributing/development.md` | Local development setup |
| `docs/contributing/docs-guide.md` | How to contribute to documentation |

## `interfaces/` — Interface Layer

| File | Description |
|------|-------------|
| `interfaces/docker-compose.interface.yml` | LiteLLM proxy and llama.cpp service definitions |
| `interfaces/interface.md` | Interface layer overview |
| `interfaces/config/litellm/litellm-config.yaml` | LiteLLM proxy configuration (routing, retries, auth) |
| `interfaces/config/litellm/providers/dgx.yaml` | DGX provider routing config |
| `interfaces/config/litellm/providers/azure-foundry.yaml` | Azure Foundry provider routing config |
| `interfaces/config/litellm/providers/nvidia.yaml` | NVIDIA provider routing config |
| `interfaces/config/litellm/providers/deepseek.yaml` | DeepSeek provider routing config |
| `interfaces/config/qwen3.6/chat_template.jinja` | Chat template for Qwen 3.6 model |
| `interfaces/dockerfiles/Dockerfile` | llama.cpp Docker image build definition |
| `interfaces/docs/README.md` | Interface layer documentation |
| `interfaces/docs/developer-clients.md` | Developer client documentation |
| `interfaces/docs/env-reference.md` | Interface layer environment variables |
| `interfaces/docs/file-index.md` | Interface layer file index (legacy) |

## `network/` — Network Configuration

| File | Description |
|------|-------------|
| `network/docker-compose.yaml` | Shared external Docker network (`init_default`) |

## `observability/` — Observability Layer

| File | Description |
|------|-------------|
| `observability/docker-compose.obs.yml` | Grafana, Mimir, Loki, Alloy, cAdvisor, DCGM services |
| `observability/config/config.alloy` | Grafana Alloy collector configuration |
| `observability/config/loki-config.yaml` | Loki log storage configuration |
| `observability/config/mimir-config.yaml` | Mimir metrics storage configuration |
| `observability/config/alertmanager-fallback.yaml` | Alertmanager fallback configuration |
| `observability/config/grafana/provisioning/datasources/datasources.yaml` | Grafana data source provisioning (Mimir, Loki) |
| `observability/config/grafana/provisioning/dashboards/dashboard-providers.yaml` | Dashboard provider definition |
| `observability/config/grafana/provisioning/dashboards/machine/spark-machine-observability.json` | Host + GPU metrics dashboard |
| `observability/config/grafana/provisioning/dashboards/machine/spark-machine-signals.json` | Combined metrics and log signals |
| `observability/config/grafana/provisioning/dashboards/machine/spark-container-logs.json` | Container log dashboard |
| `observability/config/grafana/provisioning/dashboards/machine/spark-docker-containers.json` | Container resource dashboard |
| `observability/config/grafana/provisioning/dashboards/machine/spark-machine-logs.json` | Systemd journal and file logs |
| `observability/config/grafana/provisioning/dashboards/machine/spark-llamacpp-observability.json` | llama.cpp inference metrics |
| `observability/config/grafana/provisioning/dashboards/machine/spark-vllm-observability.json` | vLLM inference metrics |
| `observability/config/grafana/provisioning/alerting/machine-alerts.yaml` | Alert rules |
| `observability/docs/README.md` | Observability layer documentation |
| `observability/docs/architecture.md` | Observability architecture overview |
| `observability/docs/dashboard-standards.md` | Dashboard design standards |
| `observability/docs/interface-telemetry-standard.md` | Telemetry labeling standards for interfaces |
| `observability/docs/labeling.md` | Label taxonomy and conventions |
| `observability/docs/llamacpp-telemetry.md` | llama.cpp telemetry specifics |
| `observability/docs/log-coverage.md` | Log source coverage matrix |

## `scripts/` — Utility Scripts

| File | Description |
|------|-------------|
| `scripts/gpu-persistent-setting.sh` | Apply persistent GPU mode and clock limits |
| `scripts/litellm-claude-smoke-test.sh` | Smoke test for LiteLLM proxy |
| `scripts/nvidia_system_info.py` | NVIDIA system information reporter |
| `scripts/spark-gpu-smoke-test.py` | GPU smoke test (driver, CUDA, container toolkit) |
| `scripts/spark-gpu-throttle-test.py` | GPU throttle behavior test |
| `scripts/spark-a3b-long-context-harness.py` | Long context inference test harness |
| `scripts/cmds.txt` | Reference commands |

## `third-party/` — Third-Party Dependencies

| File | Description |
|------|-------------|
| `third-party/README.md` | Third-party dependency overview |
| `third-party/llama.cpp/` | Git submodule — llama.cpp inference engine (MIT license) |

## `.vscode/` — VS Code Settings

| File | Description |
|------|-------------|
| `.vscode/settings.json` | Workspace settings (exclusions, formatter) |

> **★ Insight**
> - Legacy file indexes in `data/docs/file-index.md` and `interfaces/docs/file-index.md` are superseded by this unified index.
> - The `docs/` directory is the canonical documentation location; per-layer `docs/` subdirectories exist for historical context.
> - Runtime data directories (`data/storage/`, `observability/volumes/`) are excluded from this index — they are created at runtime and tracked in `.gitignore`.
