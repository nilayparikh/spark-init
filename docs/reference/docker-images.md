# Docker Images

This reference lists all Docker images used by the `.init` stack, organized by layer. Image tags are parameterized via `.env` variables where applicable.

## Data Layer

| Image | Default Tag | Env Variable | Purpose |
|-------|-------------|--------------|---------|
| `postgres` | `latest` | `DATA_POSTGRES_IMAGE` | Shared PostgreSQL for Grafana and LiteLLM databases |

## Observability Layer

| Image | Default Tag | Purpose |
|-------|-------------|---------|
| `grafana/grafana-oss` | `latest` | Dashboard and visualization UI |
| `grafana/mimir` | `latest` | Prometheus-compatible metrics storage |
| `grafana/loki` | `latest` | Log aggregation storage |
| `grafana/alloy` | `latest` | Metrics and log collector (replaces Prometheus + Promtail) |
| `gcr.io/cadvisor/cadvisor` | `v0.52.1` | Container resource monitoring |
| `nvcr.io/nvidia/k8s/dcgm-exporter` | `4.5.3-4.8.2-distroless` | NVIDIA GPU telemetry exporter |
| `cloudflare/cloudflared` | `latest` | Cloudflare Tunnel (optional, for external access) |

## Interface Layer

| Image | Default Tag | Env Variable | Purpose |
|-------|-------------|--------------|---------|
| `docker.litellm.ai/berriai/litellm` | `latest` | `LITELLM_IMAGE` | LiteLLM proxy (OpenAI-compatible API gateway) |
| `nilayparikh/llama-cpp-dgx` | `cuda13.1.2-b9222` | `LLAMA_QWEN_3_6_27B_IMAGE_REPO`, `LLAMA_CPP_TAG` | llama.cpp inference backend for Qwen 3.6 27B |

## Building the llama.cpp Image

The `nilayparikh/llama-cpp-dgx` image is built from `interfaces/dockerfiles/Dockerfile`:

```bash
# Build locally
docker build -t nilayparikh/llama-cpp-dgx:cuda13.1.2-b9222 \
  -f interfaces/dockerfiles/Dockerfile interfaces/dockerfiles/
```

The image is also built by CI (`.github/workflows/docker-build.yml`) on pushes to `main` and on tags. It targets ARM64 (aarch64) for NVIDIA DGX/Spark hardware.

### Image Tags

| Tag Pattern | Description |
|-------------|-------------|
| `cuda13.1.2-b9222` | CUDA 13.1.2 with llama.cpp commit b9222 |
| `cuda13.1.2-latest` | CUDA 13.1.2 with latest llama.cpp main branch |

The `LLAMA_CPP_TAG` variable in `.env` controls which commit is used. Update it to pull a newer build:

```bash
# .env
LLAMA_CPP_TAG=b9222
```

## Image Registry

| Image | Registry | Authentication |
|-------|----------|----------------|
| `postgres` | Docker Hub | Public |
| `grafana/*` | Docker Hub | Public |
| `gcr.io/cadvisor/cadvisor` | Google Container Registry | Public |
| `nvcr.io/nvidia/k8s/dcgm-exporter` | NVIDIA Container Registry | Public (NVIDIA NGC login required for some tags) |
| `cloudflare/cloudflared` | Docker Hub | Public |
| `docker.litellm.ai/berriai/litellm` | LiteLLM Registry | Public |
| `nilayparikh/llama-cpp-dgx` | Docker Hub | Public |

## Reducing Image Pull Times

For environments with slow or unreliable internet, pre-pull and tag images locally:

```bash
# Pre-pull all images
docker compose pull

# Or pull individually
docker pull grafana/grafana-oss:latest
docker pull grafana/mimir:latest
docker pull grafana/loki:latest
docker pull grafana/alloy:latest
```

## Pinning Image Versions

The default `.env.example` uses `latest` tags for convenience. For production deployments, pin to specific digests:

```bash
# Get image digest
docker inspect --format='{{index .RepoDigests 0}}' grafana/grafana-oss:latest

# Pin in .env
DATA_POSTGRES_IMAGE=postgres@sha256:abc123...
```

> **★ Insight**
> - The only custom-built image is `nilayparikh/llama-cpp-dgx` — all others are pulled from public registries.
> - `latest` tags are convenient for local development but should be pinned to digests for reproducible deployments.
> - The DCGM exporter uses a distroless NVIDIA base image — no shell, just the metrics binary at `:9400`.
