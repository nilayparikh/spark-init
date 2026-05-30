# Development Setup

This guide walks you through setting up a local development environment for the `.init` stack.

## Prerequisites

- **OS**: Ubuntu 24.04 ARM64 (primary development platform)
- **Docker** ≥ 27.x with Compose plugin
- **NVIDIA GPU** with driver ≥ 570
- **nvidia-container-toolkit** installed and configured
- **Git** ≥ 2.40

## Clone the Repository

```bash
git clone https://github.com/[owner]/init-stack.git
cd .init
git submodule update --init --recursive
```

The `third-party/llama.cpp/` directory is a git submodule — the `--recursive` flag ensures it is populated.

## Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your local settings. Critical variables to update:

| Variable                             | What to Change                         |
| ------------------------------------ | -------------------------------------- |
| `LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH` | Path to your GGUF model file on disk   |
| `LLAMA_QWEN_3_6_27B_BINARY_PATH`     | Path to compiled `llama-server` binary |
| `LITELLM_MASTER_KEY`                 | Your preferred API key                 |
| `GRAFANA_ADMIN_PASSWORD`             | A strong password for Grafana          |

## Start the Stack

```bash
# Full stack (data + observability + interface)
docker compose up -d

# Check status
docker compose ps

# View logs for a specific service
docker compose logs -f litellm
```

## Development Workflow

### Iterating on Compose Files

After editing a compose file:

```bash
docker compose up -d --force-recreate <service>
```

### Iterating on Alloy Configuration

Alloy requires a reload to pick up config changes:

```bash
docker compose restart alloy
```

### Iterating on Grafana Dashboards

Dashboards are provisioned from JSON files in `observability/config/grafana/provisioning/dashboards/`. After editing a dashboard JSON file:

```bash
docker compose restart grafana
```

Grafana re-reads provisioned dashboards on startup.

### Iterating on LiteLLM Configuration

After editing `interfaces/config/litellm/config.yaml`:

```bash
docker compose restart litellm
```

### Building the llama.cpp Image Locally

```bash
docker build -t nilayparikh/llama-cpp-dgx:cuda13.1.2-local \
  -f interfaces/dockerfiles/Dockerfile interfaces/dockerfiles/
```

Update `.env` to use the local image:

```bash
LLAMA_QWEN_3_6_27B_IMAGE_REPO=nilayparikh/llama-cpp-dgx
LLAMA_CPP_TAG=local
```

## Dev Container

The repository includes a VS Code Dev Container configuration (`.devcontainer/`). It provides:

- GPU access (`--gpus=all`)
- Host networking (`--network=host`) for service discovery
- Docker-outside-of-Docker for managing compose stacks
- Recommended extensions: Docker, Python, YAML

Launch from VS Code:

```
Ctrl+Shift+P → Dev Containers: Reopen in Container
```

## Linting

Run the same checks that CI runs:

```bash
# YAML lint
pip install yamllint
yamllint -d "{extends: default, rules: {line-length: disable, truthy: disable}}" \
  $(find . -name 'docker-compose*.yml' -o -name '*.yaml' -path '*/config/*')

# Shell lint
shellcheck scripts/*.sh data/config/postgres-init/*.sh

# Python syntax check
find scripts/ -name '*.py' -print0 | xargs -0 -I{} python3 -m py_compile {}
```

## Testing

The stack includes smoke tests in `scripts/`:

```bash
# GPU smoke test
python3 scripts/spark-gpu-smoke-test.py

# LiteLLM proxy smoke test
bash scripts/litellm-claude-smoke-test.sh

# GPU throttle behavior test
python3 scripts/spark-gpu-throttle-test.py
```

## Clean Slate

To reset the entire stack (destructive — removes all data):

```bash
docker compose down -v
docker compose up -d
```

> **★ Insight**
>
> - Always run `git submodule update --init --recursive` after cloning — the llama.cpp submodule is required for the inference backend.
> - The Dev Container uses `--network=host` so Alloy can discover containers via the Docker socket; this is simpler than managing Docker networks in a nested container.
> - `docker compose down -v` destroys all volumes including PostgreSQL data and Grafana dashboards. Use selectively.
