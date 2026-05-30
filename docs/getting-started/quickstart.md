# Quick Start

Get the full `.init` stack running in 5 minutes.

## Prerequisites Checklist

Before you begin, ensure your system has:

- **Docker** ≥ 27.x with Compose plugin
- **NVIDIA GPU** with driver ≥ 570 (Blackwell/Ada recommended)
- **nvidia-container-toolkit** installed and configured
- **Ubuntu 24.04 ARM64** (primary supported platform)
- Minimum **48GB VRAM** for 27B models

## Step-by-Step

### 1. Clone the Repository

```bash
git clone https://github.com/nilayparikh/init-stack.git
cd .init
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your local settings. The critical variables to set:

| Variable                             | Purpose                          | Example                                 |
| ------------------------------------ | -------------------------------- | --------------------------------------- |
| `COMPOSE_PROFILES`                   | Stack shape selection            | `data,obs,interface,llama-qwen-3-6-27b` |
| `LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH` | Path to your GGUF model file     | `/path/to/model.gguf`                   |
| `LITELLM_MASTER_KEY`                 | LiteLLM proxy authentication key | `sk-your-secret-key`                    |
| `AZURE_ORCHESTRATOR_API_KEY`         | Azure Foundry API key (optional) | Leave empty if not using cloud models   |

> **Note:** The `.env` file is git-ignored. Only `.env.example` is committed. Never commit your `.env`.

### 3. Choose Your Stack Shape

Set `COMPOSE_PROFILES` in `.env` to one of these configurations:

| Profile Set                             | Services                      | Use Case                              |
| --------------------------------------- | ----------------------------- | ------------------------------------- |
| `data,obs,interface,llama-qwen-3-6-27b` | Full stack with llama.cpp 27B | Default — everything running together |
| `data,obs`                              | Data + observability only     | Monitoring without inference backends |
| `data`                                  | Data layer only               | PostgreSQL for persistent storage     |
| `obs`                                   | Observability only            | Grafana/Mimir/Loki monitoring stack   |

### 4. Start the Stack

```bash
docker compose up -d
```

This starts all services matching your `COMPOSE_PROFILES`. The first run will pull Docker images and may take a few minutes.

### 5. Verify Everything is Running

```bash
# Check service status
docker compose ps

# Verify LiteLLM proxy health (if interface profile is active)
curl -f http://localhost:4000/health | head -20

# Verify llama.cpp backend health (if llama-qwen-3-6-27b profile is active)
curl -f http://localhost:8000/health | head -20

# Check Grafana (if obs profile is active)
open http://localhost:3000
```

## Expected Endpoints

| Service       | Endpoint                   | Profile              | Notes                                                |
| ------------- | -------------------------- | -------------------- | ---------------------------------------------------- |
| LiteLLM proxy | `http://localhost:4000`    | `interface`          | OpenAI-compatible API, requires `LITELLM_MASTER_KEY` |
| llama.cpp 27B | `http://localhost:8000/v1` | `llama-qwen-3-6-27b` | Direct inference with Standard (Qwen 3.6 27B) model  |
| Grafana       | `http://localhost:3000`    | `obs`                | Default login: admin / local_observability_admin     |

## First Request

Once the stack is running, test the LiteLLM proxy with a completion request:

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "openai/qwen3.6_27b",
    "messages": [{"role": "user", "content": "Say hello in one sentence."}],
    "max_tokens": 50
  }' | python3 -m json.tool | head -30
```

## Stopping the Stack

```bash
# Stop all services (preserves volumes)
docker compose down

# Stop and remove volumes (destructive — loses database data)
docker compose down -v
```

## Troubleshooting Quick Wins

- **`nvidia-container-toolkit` not configured** → Run `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker`
- **Port 8000 already in use** → Another process is binding to port 8000; stop it or change the port mapping
- **Model not found** → Verify `LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH` in `.env` points to an existing `.gguf` file
- **CUDA errors** → Ensure `nvidia-smi` shows your GPU and driver is ≥ 570

For detailed troubleshooting, see [Troubleshooting Guide](../guides/troubleshooting.md).
