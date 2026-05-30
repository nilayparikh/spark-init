# Architecture

`.init` is three Docker Compose layers, one network, and one `.env` file.

## Bird's-Eye View

```
You / VS Code / Claude Code
        │
        ▼
┌───────────────────────────────┐
│   LiteLLM Proxy (:4000)       │  ← API gateway (auth, routing, logging)
│   interface profile            │
├───────────────────────────────┤
│   llama.cpp (:8000 / :8001)   │  ← GPU inference (27B & 35B)
│   interface profile            │
└──────────┬────────────────────┘
           │
           ▼
┌───────────────────────────────┐
│   Alloy → Mimir/Loki          │  ← Auto-collected metrics & logs
│   obs profile                  │
├───────────────────────────────┤
│   Grafana (:3000)              │  ← Dashboards
└──────────┬────────────────────┘
           │
           ▼
┌───────────────────────────────┐
│   PostgreSQL (:5432)           │  ← Shared database
│   data profile                 │
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

**Runs:** LiteLLM proxy + llama.cpp (one container per model)

LiteLLM is the front door. It authenticates requests, routes by model name, logs usage to Postgres, and exposes Prometheus metrics. llama.cpp containers run on host ports with full GPU access.

LiteLLM reaches llama.cpp via `host.docker.internal:8000` (or `:8001`) — the inference containers publish directly to the host network for zero-overhead GPU access.

## Networking

All containers share the `init_default` external network, defined in `network/docker-compose.yaml`. Services discover each other by container name (Docker's embedded DNS).

The external network is what lets the three compose files talk to each other. Create it once:

```bash
docker network create init_default
```

## Profile Dependency Rules

```yaml
data                    # just Postgres
data + obs              # Postgres + Grafana stack
data + interface        # Postgres + LiteLLM proxy
data + obs + interface  # Postgres + Grafana + proxy (no local models)
data + obs + interface + llama-qwen-3-6-27b   # full stack (default)
```

All `depends_on` conditions use health checks — Postgres must report `pg_isready` before Grafana or LiteLLM start.

## Why This Design?

- **One switchboard** — `COMPOSE_PROFILES` is the only thing you change to reshape the stack
- **No vendor lock-in** — LiteLLM means you can swap out the inference backend or add cloud providers without changing clients
- **Observable by default** — every service emits telemetry; you don't configure monitoring, it's just there
- **Manual start only** — `restart: "no"` across the board. The stack never consumes GPU resources unless you explicitly ask for it
