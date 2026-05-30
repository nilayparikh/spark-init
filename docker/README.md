# Docker — Container Images

Custom Docker images for the `.init` stack on DGX Spark.

## Images

| Image | Path | Purpose | GHCR |
|-------|------|---------|------|
| `llama-cpp-dgx` | `llama-cpp-dgx/Dockerfile` | llama.cpp CUDA inference server | `ghcr.io/nilayparikh/llama-cpp-dgx` |
| `claude-code` | `claude-code/Dockerfile` | Claude Code dev container (NVIDIA PyTorch) | `ghcr.io/nilayparikh/claude-code` |

## Building Locally

```bash
# llama-cpp-dgx
docker build -t ghcr.io/nilayparikh/llama-cpp-dgx:cuda13.1.2-b9222 \
  -f docker/llama-cpp-dgx/Dockerfile .

# claude-code
docker build -t ghcr.io/nilayparikh/claude-code:v0.0.1 \
  -f docker/claude-code/Dockerfile docker/claude-code/
```

## OCI Labels

All images include [OCI standard labels](https://github.com/opencontainers/image-spec/blob/main/annotations.md):

| Label | Value |
|-------|-------|
| `org.opencontainers.image.title` | Image short name |
| `org.opencontainers.image.description` | What the image does |
| `org.opencontainers.image.source` | GitHub repository URL |
| `org.opencontainers.image.url` | Project URL |
| `org.opencontainers.image.licenses` | MIT |
| `org.opencontainers.image.vendor` | Nilay Parikh |
| `org.opencontainers.image.authors` | Maintainer contact |
| `org.opencontainers.image.version` | Git ref / version tag |
| `org.opencontainers.image.revision` | Git commit SHA |
| `org.opencontainers.image.created` | Build timestamp |

These are automatically injected by CI workflows via `docker/metadata-action`.

## Related

- `claude-code.sh` — launches the claude-code container through the local LiteLLM proxy
- `interfaces/docker-compose.interface.yml` — builds the llama-cpp-dgx image for local inference
- `scripts/litellm-claude-smoke-test.sh` — smoke test against the running container
