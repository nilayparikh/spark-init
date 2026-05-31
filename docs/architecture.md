# Architecture

`.init` is three Docker Compose layers, one network, and one `.env` file.

## Bird's-Eye View

```
You / VS Code / Claude Code
        │
        ▼
┌───────────────────────────────┐
│   LiteLLM Proxy (:4000)       │  ← API gateway (auth, routing, logging)
│   litellm / interface profile  │
├───────────────────────────────┤
│   llama.cpp 27B (:8000)       │  ← GPU inference (128K context)
│   llama-qwen-3-6-27b profile  │
├───────────────────────────────┤
│   llama.cpp 35B A3B (:8001)   │  ← GPU inference (256K context, vision)
│   llama-qwen-3-6-35b-a3b profile│
└──────────┬────────────────────┘
           │
           ▼
┌───────────────────────────────┐
│   Alloy → Mimir/Loki          │  ← Auto-collected metrics & logs
│   alloy / mimir / loki profiles│
├───────────────────────────────┤
│   Grafana (:3000)              │  ← Dashboards
│   grafana profile              │
└──────────┬────────────────────┘
           │
           ▼
┌───────────────────────────────┐
│   PostgreSQL (:5432)           │  ← Shared database
│   postgres / data profile      │
└───────────────────────────────┘
           │
           ▼
┌───────────────────────────────┐
│   Cloudflare Tunnel           │  ← External access
│   cloudflared profile         │
└───────────────────────────────┘
```

## Three Layers

Each layer lives in its own directory with its own `docker-compose.*.yml`, and activates via `COMPOSE_PROFILES`.

### Data Layer (`data/`)

**Runs:** PostgreSQL

Postgres is the shared database for Grafana (dashboards, users) and LiteLLM (usage logs, provider config). Bootstrap scripts in `data/config/postgres-init/` create the databases and users automatically on first start.

### Observability Layer (`observability/`)

**Runs:** Alloy → Mimir (metrics) + Loki (logs) → Grafana

Metrics and logs flow in one direction. Alloy scrapes everything (GPU via DCGM, containers via cAdvisor, system via Unix exporter, inference via llama.cpp `/metrics`) and ships to Mimir (time-series) and Loki (logs). Grafana visualizes it all from auto-provisioned dashboards.

No configuration needed to start collecting — Alloy auto-discovers running services through the Docker socket.

### Interfaces Layer (`interfaces/`)

**Runs:** LiteLLM proxy + llama.cpp (two containers, one per model)

LiteLLM is the front door. It authenticates requests, routes by model name, logs usage to Postgres, and exposes Prometheus metrics. Two llama.cpp containers run on host ports with full GPU access:

- `llama-qwen-3-6-27b` — Qwen 3.6 27B, host port `8000`, 128K context
- `llama-qwen-3-6-35b-a3b` — Qwen 3.6 35B A3B, host port `8001`, 256K context (vision-capable)

Each has its own unique profile and can run independently or simultaneously.

LiteLLM reaches llama.cpp via `host.docker.internal:8000` (or `:8001`) — the inference containers publish directly to the host network for zero-overhead GPU access.

### Network Layer (`network/`)

**Runs:** Cloudflare Tunnel (`cloudflared`)

The Cloudflare Tunnel provides secure external access to internal services without exposing ports. Configure the tunnel in Cloudflare Zero Trust dashboard and add the tunnel token to `.env.secrets` as `CLOUDFLARE_TUNNEL_TOKEN`.

## Networking

All containers share the `init_default` external network, defined in `network/docker-compose.yaml`. Services discover each other by container name (Docker's embedded DNS).

The external network is what lets the four compose files talk to each other. Create it once:

```bash
docker network create init_default
```

## Profile Dependency Rules

```yaml
data                        # just Postgres
data,obs                    # Postgres + Grafana stack
data,litellm                # Postgres + LiteLLM proxy (cloud models only)
data,litellm,llama-qwen-3-6-27b  # Postgres + LiteLLM + 27B
data,obs,interface          # Postgres + Grafana + proxy + both llama.cpp backends
data,obs,litellm,llama-qwen-3-6-27b  # Postgres + Grafana + LiteLLM + 27B
all                         # everything
```

All `depends_on` conditions use health checks — Postgres must report `pg_isready` before Grafana or LiteLLM start.

## Why This Design?

- **One switchboard** — `COMPOSE_PROFILES` is the only thing you change to reshape the stack
- **No vendor lock-in** — LiteLLM means you can swap out the inference backend or add cloud providers without changing clients
- **Observable by default** — every service emits telemetry; you don't configure monitoring, it's just there
- **Manual start only** — `restart: "no"` across the board. The stack never consumes GPU resources unless you explicitly ask for it
