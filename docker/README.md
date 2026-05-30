# Docker — Container Images

Custom Docker images for the `.init` stack on DGX Spark.

## Contents

| Path | Purpose |
|---|---|
| `claude-code/Dockerfile` | Claude Code dev container (NVIDIA PyTorch base, aarch64) |

## `docker/claude-code/`

A PyTorch-based container for running Claude Code via `claude-code.sh`. It includes:

- NVIDIA PyTorch 26.04 base (CUDA 13.1.2, aarch64)
- Claude Code CLI (`@anthropic-ai/claude-code`)
- Developer utilities: gh CLI, ripgrep, fd, ast-grep, difftastic, scc
- Pre-configured environment variables for LiteLLM proxy routing

### Building

```bash
docker build -t nilayparikh/dgx-dev:v0.0.1 \
  -f docker/claude-code/Dockerfile docker/claude-code/
```

### Why a Separate Container?

Running Claude Code inside a container ensures:

1. **Isolated environment** — no dependency conflicts with host tools
2. **Consistent routing** — `ANTHROPIC_BASE_URL` is hard-coded to point at the local LiteLLM proxy
3. **GPU access** — `--gpus all` and `--network host` give the container full hardware access

### DGX Spark Notes

The Dockerfile targets `linux/arm64` (aarch64) for DGX Spark's Grace CPU. All utility binaries are downloaded as `aarch64` builds. The NVIDIA PyTorch base image is optimized for Grace Blackwell.

## Related

- `interfaces/dockerfiles/Dockerfile` — llama.cpp CUDA build image (separate from this dev container)
