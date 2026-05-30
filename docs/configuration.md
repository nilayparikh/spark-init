# Configuration

Everything flows through `.env`. One file controls the full stack.

## The Pattern

```bash
cp .env.example .env
# Edit .env
docker compose up -d
```

Docker Compose loads `.env` automatically and injects variables into every container. The `.env.example` file documents every variable with a default and a comment — it's the source of truth.

## What You'll Set

### Stack Shape

`COMPOSE_PROFILES` is the only variable that changes what services start. See [Quickstart](quickstart.md) for the common combinations.

### Model Paths

Point to your GGUF files:

```bash
LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH=/path/to/qwen3.6-27b.gguf
LLAMA_QWEN_3_6_35B_A3B_GGUF_MODEL_PATH=/path/to/qwen3.6-35b-a3b.gguf
LLAMA_QWEN_3_6_35B_A3B_MMPROJ_MODEL_PATH=/path/to/mmproj-BF16.gguf
```

These are bind-mounted into the llama.cpp containers as `/models/model.gguf`.

### API Keys

| Variable | What it's for |
|---|---|
| `LITELLM_MASTER_KEY` | Required — auth for the proxy |
| `MICROSOFT_FOUNDRY_API_KEY` | Azure Foundry cloud models |
| `NVIDIA_API_KEY` | NVIDIA AI Endpoints |
| `DEEPSEEK_API_KEY` | DeepSeek API |
| `OPENCODE_ZEN_API_KEY` | OpenCode Zen |

No key = that provider is disabled. Local models always work.

### Ports

You can rebind any port if there's a conflict:

```bash
LITELLM_PORT=4000          # API gateway
LLAMA_QWEN_3_6_27B_HOST_PORT=8000   # 27B inference
LLAMA_QWEN_3_6_35B_A3B_HOST_PORT=8001  # 35B inference
GRAFANA_ROOT_URL=http://localhost:3000/
```

## Provider Configuration

LiteLLM routing lives in `interfaces/config/litellm/`. The root `config.yaml` includes per-provider fragments from `providers/`:

```
providers/
├── dgx-spark.yaml        # Local models (Qwen 3.6 27B, 35B A3B)
├── azure-foundry.yaml    # Azure Foundry
├── nvidia.yaml           # NVIDIA AI Endpoints
├── deepseek.yaml         # DeepSeek native
└── opencode-zen.yaml     # OpenCode Zen
```

Each fragment defines a `model_list` with the upstream URL, API key (from environment variable), and model name. To add a new provider, create a new fragment and include it in `config.yaml`.

## Chat Template

Qwen 3.6 uses a custom Jinja2 template at `interfaces/config/qwen3.6/chat_template.jinja`. It's mounted into both llama.cpp containers and loaded with `--jinja --chat-template-file /workspace/chat_template.jinja --reasoning on --reasoning-format deepseek`.

## Alloy Configuration

The observability pipeline is defined in `observability/config/config.alloy` (HCL format). It defines three things:

1. **What to scrape** — Docker socket for container discovery, `/metrics` endpoints, Unix exporter, systemd journal
2. **Where to send it** — Mimir for metrics, Loki for logs
3. **Labels to add** — `environment`, `host`, `job`, etc. for cross-service correlation

Edit this file if you want to add custom scrape targets or change label values.

## Grafana

Dashboards and data sources are auto-provisioned from `observability/config/grafana/provisioning/`:

```
provisioning/
├── datasources/    → Mimir + Loki connection config
├── dashboards/     → JSON dashboard definitions
└── alerting/       → Alert rule thresholds
```

Grafana reads these on startup. Edit a dashboard JSON and run `docker compose restart grafana` to apply changes.
