# Capabilities

What `.init` can do for you, organized by what you want to accomplish.

---

## Run Local LLMs

The stack serves two Qwen 3.6 models through `llama.cpp` on your GPU.

| Model | Parameters | Context | Port | Best for |
|---|---|---|---|---|
| Qwen 3.6 27B | 27B | 128K tokens | `:8000` | Day-to-day coding, chat, reasoning |
| Qwen 3.6 35B A3B | 35B (3.5B active) | 256K tokens | `:8001` | Long context, vision tasks |

Both use speculative decoding (MTP) for faster generation. No GPU sharing — each gets the full card when active.

**Try it:**

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3.6_27b", "messages": [{"role": "user", "content": "Write a quick sort in Python"}]}'
```

## Use the OpenAI-Compatible API

Everything routes through LiteLLM at `http://localhost:4000/v1`. This is the one endpoint you need.

| What | URL | Auth |
|---|---|---|
| Chat completions | `POST /v1/chat/completions` | Bearer token |
| List models | `GET /v1/models` | Bearer token |
| Available models | `DGX/Qwen3.6-27B`, `DGX/Qwen3.6-35B-A3B`, and cloud provider models | — |

**From Python:**

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:4000/v1", api_key="<your-key>")
response = client.chat.completions.create(
    model="DGX/Qwen3.6-27B",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**From Claude Code:**

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="<your-key>"
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
claude
# then: /model .INIT/Pro  (or .INIT/Flash, .INIT/Ultra)
```

**From VS Code / Cline / Continue:**

```json
{ "baseURL": "http://localhost:4000/v1", "model": "DGX/Qwen3.6-27B" }
```

## Mix Local and Cloud Models

LiteLLM routes by model name. Use a local model for quick tasks, a cloud model for hard ones — same API key, same endpoint.

| Model ID | Where it runs |
|---|---|
| `DGX/Qwen3.6-27B` | Your GPU (free) |
| `Azure/Kimi-K2.6` | Azure Foundry (metered) |
| `DeepSeek/DeepSeek-V4-Pro` | DeepSeek API (metered) |
| `NVIDIA/Kimi-K2.6` | NVIDIA AI Endpoints (metered) |
| `OpenCodeZen/BIG-PICKLE` | OpenCode Zen (metered) |

Set API keys in `.env` and they show up automatically. No keys = local-only mode.

## Observe Everything

Open Grafana at `http://localhost:3000` (login: `admin` / password from `.env`). You'll see:

- **GPU utilization, memory, thermals** — live from DCGM
- **Token throughput** — requests/second, tokens/second for each model
- **Container health** — CPU, memory, network per service
- **System logs** — kernel events, container logs, all searchable

All collected automatically by Grafana Alloy. No configuration needed — it discovers services and starts scraping.

## Use the Gateway Model Discovery

For Claude Code, the proxy publishes three `.INIT/` aliases that show up in `/model`:

| Alias | Backs onto | When to use |
|---|---|---|
| `.INIT/Flash` | DGX/Qwen3.6-35B-A3B | Fast, large context, vision |
| `.INIT/Pro` | DGX/Qwen3.6-27B | Deep reasoning, coding |
| `.INIT/Ultra` | OpenCodeZen/BIG-PICKLE | Hardest problems (cloud) |

These are configured in `interfaces/config/litellm/config.yaml` under `model_group_alias`.

## Available Endpoints

| Service | Address | What it does |
|---|---|---|
| LiteLLM proxy | `http://localhost:4000` | API gateway, auth, routing |
| llama.cpp (27B) | `http://localhost:8000` | Direct inference |
| llama.cpp (35B) | `http://localhost:8001` | Direct inference |
| Grafana | `http://localhost:3000` | Dashboards |
| PostgreSQL | `localhost:5432` | Shared database |
