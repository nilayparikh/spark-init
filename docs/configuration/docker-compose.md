# Docker Compose Configuration

The `.init` stack uses a modular, profile-driven Docker Compose architecture. This page documents the compose file structure, profiles, services, and volume mounts.

## Repository Structure

```
.init/
├── docker-compose.yml              # Root orchestrator — includes all layer files
├── .env                            # Environment switchboard (git-ignored)
├── .env.example                    # Template with defaults (committed)
│
├── data/                           # Data layer
│   ├── docker-compose.data.yml     # PostgreSQL and bootstrap scripts
│   ├── config/                     # Static configurations
│   │   └── postgres-init/          # Database initialization scripts
│   └── storage/                    # Runtime storage (git-ignored)
│       └── postgres/               # PostgreSQL data directory
│
├── observability/                  # Observability layer
│   ├── docker-compose.obs.yml      # Mimir, Loki, Alloy, Grafana, GPU telemetry
│   ├── config/                     # Static service configurations
│   │   ├── config.alloy            # Alloy HCL pipeline
│   │   ├── loki-config.yaml        # Loki single-binary config
│   │   ├── mimir-config.yaml       # Mimir single-binary config
│   │   └── grafana/                # Grafana provisioning configs
│   │       └── provisioning/       # Dashboards, data sources, alert rules
│   └── volumes/                    # Local directory volume mounts (git-ignored)
│       ├── alloy/                  # Alloy state
│       ├── grafana/                # Grafana dashboards and reports
│       ├── loki/                   # Loki chunks, WAL, compactor
│       └── mimir/                  # Mimir blocks, compactor, object store
│
├── interfaces/                     # Interfaces layer
│   ├── docker-compose.interface.yml# LiteLLM proxy and llama.cpp backend
│   ├── config/                     # Interface configurations
│   │   ├── litellm/                # LiteLLM model routing and provider configs
│   │   └── qwen3.6/                # Chat templates for Qwen 3.6
│   └── dockerfiles/                # Custom Docker images
│       └── Dockerfile              # llama.cpp CUDA build
```

## Root Orchestrator

The root `docker-compose.yml` is minimal — it uses native `include` directives to pull in layer-specific compose files:

```yaml
include:
  - ./data/docker-compose.data.yml
  - ./observability/docker-compose.obs.yml
  - ./interfaces/docker-compose.interface.yml
  - ./network/docker-compose.yaml

networks:
  default:
    external: true
    name: init_default
```

## Profiles

Every service is bound to one or more profiles. The `COMPOSE_PROFILES` variable in `.env` is the single switchboard for the entire platform.

| Profile | Area    | Service(s) | Notes |
| ------- | ------- | ---------- | ----- |
| `data`  | `data/` |

- `postgres`
- Shared dependency for LiteLLM and Grafana.
- Required whenever any service needs Postgres.
-
- `obs`
- `observability/`
- `mimir`, `loki`, `alloy`, `gpu-telemetry`, `grafana`
- Observability stack. Requires `data` if Grafana should use Postgres.
-
- `interface`
- `interfaces/`
- `litellm`
- OpenAI-compatible proxy on port 4000.
-
- `llama-qwen-3-6-27b`
- `interfaces/`
- `llama-qwen-3-6-27b`
- llama.cpp-based Standard model (Qwen 3.6 27B) on host port 8000.
-
- `all`
- All layers
- Convenience profile — starts everything
- Equivalent to: `data,obs,interface,llama-qwen-3-6-27b`

### Recommended Profile Sets

| Stack Shape | COMPOSE_PROFILES | Use Case |
| ----------- | ---------------- | -------- |

- Full stack
- `data,obs,interface,llama-qwen-3-6-27b`
- Default — everything running together
-
- LiteLLM only
- `data,interface`
- Proxy without local inference backend (cloud providers only)
-
- Data + observability
- `data,obs`
- Monitoring without inference backends

## Volume Mounts

All persistent data uses local directory volume mounts. These directories are git-ignored and survive container restarts.

### Data Layer

| Host Path | Container Path | Purpose |
| --------- | -------------- | ------- |

- `data/storage/postgres/`
- `/var/lib/postgresql/data/pgdata`
- PostgreSQL data directory

### Observability Layer

| Host Path | Container Path | Purpose |
| --------- | -------------- | ------- |

- `observability/volumes/alloy/`
- `/alloy`
- Alloy state and cache
-
- `observability/volumes/grafana/csv/`
- `/var/lib/grafana/csv`
- Grafana CSV exports
-
- `observability/volumes/grafana/pdf/`
- `/var/lib/grafana/pdf`
- Grafana PDF reports
-
- `observability/volumes/loki/`
- `/loki`
- Loki chunks, WAL, compactor, tsdb-shipper
-
- `observability/volumes/mimir/`
- `/mimir`
- Mimir blocks, compactor, object store

### Interfaces Layer

| Host Path | Container Path | Purpose |
| --------- | -------------- | ------- |

- `interfaces/config/litellm/`
- `/app/litellm-config/`
- LiteLLM configuration files (read-only)
-
- `interfaces/config/qwen3.6/chat_template.jinja`
- `/workspace/chat_template.jinja`
- Qwen 3.6 chat template (read-only)
-
- `<model_path>.gguf`
- `/models/model.gguf`
- GGUF model file (read-only, from host)

## Health Checks

Every service implements health checks to enforce deterministic boot ordering:

| Service | Health Check | Interval |
| ------- | ------------ | -------- |

- `postgres`
- `pg_isready`
- 10s
-
- `mimir`
- HTTP endpoint
- 30s
-
- `loki`
- HTTP endpoint
- 30s
-
- `grafana`
- HTTP endpoint
- 30s

## Manual Startup Only

Every service sets `restart: "no"` explicitly. The stack **never auto-starts** when the Docker daemon or host boots. Operators must manually invoke `docker compose up -d` for any services they want running.

This design ensures:

- GPU resources are not consumed when inference is not needed
- Model files are only loaded when explicitly requested
- Operators have full control over which profiles are active
