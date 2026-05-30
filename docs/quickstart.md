# Quick Start

Get `.init` running in about 5 minutes.

## What You'll Need

- An NVIDIA DGX Spark (or any NVIDIA GPU with 48 GB+ VRAM)
- Docker ≥ 27.x with Compose plugin
- NVIDIA Container Toolkit (`nvidia-ctk`) configured for Docker
- Ubuntu 24.04 ARM64 (primary platform)

## Start the Stack

Five steps, one minute each:

```bash
# 1. Get the code
git clone https://github.com/nilayparikh/init-stack.git
cd init-stack

# 2. Pull submodules (llama.cpp backend + model weights)
git submodule update --init --recursive

# 3. Configure
cp .env.example .env
# Edit .env:
#   - LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH → point to your GGUF file
#   - LITELLM_MASTER_KEY → set an API key
#   - COMPOSE_PROFILES → choose your stack shape

# 4. Launch
docker compose up -d

# 5. Verify
curl http://localhost:4000/health
curl http://localhost:8000/health
```

## Pick Your Stack Shape

Edit `COMPOSE_PROFILES` in `.env` to choose what runs:

| Profile | What starts | When to use |
|---|---|---|
| `data,obs,interface` | Full stack — both llama.cpp backends | Default — everything |
| `data,litellm,llama-qwen-3-6-27b` | LiteLLM + 27B only | Single model inference |
| `data,litellm` | LiteLLM proxy only | Cloud-only routing |
| `data,obs` | Observability only | Monitor without inference |
| `data` | PostgreSQL only | Just the database |

## Send Your First Request

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "DGX/Qwen3.6-27B",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Stop

```bash
docker compose down        # stops services, keeps data
docker compose down -v     # stops and deletes all data
```

## Need Help?

- `docker compose logs <service>` — check what a service is doing
- `docker compose ps` — see what's running
- [Guides](guides.md) — adding models, GPU tuning, troubleshooting
