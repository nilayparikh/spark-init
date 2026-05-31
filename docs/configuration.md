# Configuration

Everything flows through your environment files. Two files control the full stack:

| File           | Purpose                                                        | Committed?    |
| -------------- | -------------------------------------------------------------- | ------------- |
| `.env`         | Safe defaults and configuration (profiles, model paths, ports) | ✅ Git        |
| `.env.secrets` | Secrets only (passwords, API keys, tokens)                     | ❌ Gitignored |

**Interpolation order** (later overrides earlier): `.env` → `.env.secrets`

## The Pattern

```bash
cp .env.example .env
cp .env.secrets.example .env.secrets
# Edit .env for configuration
# Edit .env.secrets for secrets
docker compose --env-file .env --env-file .env.secrets up -d
```

Docker Compose loads variables from both files and injects them into every container. The `.env.example` file documents every variable with a default and a comment — it's the source of truth. Secrets live in `.env.secrets` to prevent accidental commits.

## What You'll Set

`.env.example` is organized into sections. Here's what each one controls.

### Stack Shape

`COMPOSE_PROFILES` is the only variable that changes what services start. See [Quickstart](quickstart.md) for the common combinations.

### Secrets

Database passwords, API keys, and auth tokens go in `.env.secrets` (never committed). Template values are in `.env.secrets.example`.

| Variable                    | Purpose                                  |
| --------------------------- | ---------------------------------------- |
| `DATA_POSTGRES_PASSWORD`    | PostgreSQL admin password                |
| `GRAFANA_DB_PASSWORD`       | Grafana's Postgres user password         |
| `GRAFANA_ADMIN_PASSWORD`    | Grafana web UI admin password            |
| `INTERFACE_DB_PASSWORD`     | LiteLLM's Postgres user password         |
| `LITELLM_MASTER_KEY`        | Required — auth for the proxy            |
| `CLOUDFLARE_TUNNEL_TOKEN`   | Cloudflare Tunnel token for external access |
| `MICROSOFT_FOUNDRY_API_KEY` | Azure Foundry cloud models               |
| `NVIDIA_API_KEY`            | NVIDIA AI Endpoints                      |
| `DEEPSEEK_API_KEY`          | DeepSeek API                             |
| `OPENCODE_ZEN_API_KEY`      | OpenCode Zen                             |
| `HF_TOKEN`                  | Hugging Face token (for claude-code.sh)  |
| `GH_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub tokens (for claude-code.sh) |

No cloud API key = that provider is disabled. Local models always work.

### Deployment Configuration (Section 3)

Database settings, Grafana domain, model paths, and cloud provider endpoints.

**Model paths** — point to your GGUF files on disk:

```bash
LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH=/path/to/qwen3.6-27b.gguf
LLAMA_QWEN_3_6_35B_A3B_GGUF_MODEL_PATH=/path/to/qwen3.6-35b-a3b.gguf
LLAMA_QWEN_3_6_35B_A3B_MMPROJ_MODEL_PATH=/path/to/mmproj-BF16.gguf
```

These are bind-mounted into the llama.cpp containers as `/models/model.gguf`.

**Ports** — you can rebind any port if there's a conflict:

```bash
LITELLM_PORT=4000                             # API gateway
LLAMA_QWEN_3_6_27B_HOST_PORT=8000             # 27B inference
LLAMA_QWEN_3_6_35B_A3B_HOST_PORT=8001         # 35B inference
GRAFANA_ROOT_URL=http://localhost:3000/
```

**Cloud provider base URLs** — override the default API endpoints for any provider.

### Inference Engine Tuning (Section 4)

Controls llama.cpp flags per model: context size, batch sizes, thread counts, speculative decoding parameters, KV cache type, and timeout. Values are consumed by `interfaces/docker-compose.interface.yml` as llama.cpp CLI arguments.

Two sub-sections for the two models:
- **4a. Qwen 3.6 27B (`.INIT/Pro`)** — 128K context, 8 threads, MTP speculative decoding
- **4b. Qwen 3.6 35B A3B (`.INIT/Flash`)** — 256K context, q8_0 KV cache, 8 threads

Tune these to match your workload — increase batch size for throughput, reduce threads for power savings.

### LiteLLM Router (Section 5)

Controls retry behaviour, model aliases (`.INIT/Ultra`, `.INIT/Pro`, `.INIT/Flash`, `.INIT/AIR`), and logging settings for the LiteLLM proxy. These are referenced via `os.environ/` in `interfaces/config/litellm/config.yaml`.

### Observability Pipeline (Section 6)

Infrastructure identity labels, scrape intervals, service ports, log levels, and retention periods for Mimir, Loki, and Grafana. All defaults are tuned for a single-host DGX Spark deployment.

### Claude Code Container (Section 7)

Controls the `claude-code.sh` launcher script: registry, image tag, container name, proxy URL, and terminal dimensions. See [Guides](guides.md) for usage.

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
