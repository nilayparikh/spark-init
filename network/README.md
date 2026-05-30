# Network — Docker Network & Tunnel

Shared Docker infrastructure for the `.init` stack on DGX Spark.

## What This Is

Two things:

1. **`init_default`** — The external Docker network that connects all three layers
2. **`cloudflared`** — Optional Cloudflare Tunnel for external access

### `init_default` Network

All three layers (data, observability, interfaces) communicate over a shared external network called `init_default`. This is what makes cross-compose-file service discovery work — containers resolve each other by name through Docker's embedded DNS.

**Create it once:**

```bash
docker network create init_default
```

**Who talks to whom:**

| From | To | How |
|---|---|---|
| Alloy | Mimir, Loki | `mimir:9009`, `loki:3100` |
| Grafana | Postgres, Mimir, Loki | `postgres:5432`, `mimir:9009`, `loki:3100` |
| LiteLLM | Postgres | `postgres:5432` |
| LiteLLM | llama.cpp | `host.docker.internal:8000` (host port) |

### Cloudflare Tunnel

The `cloudflared` service provides secure external access to the stack (Grafana, LiteLLM, etc.) without opening firewall ports. Requires `CLOUDFLARE_TUNNEL_TOKEN` in `.env`.

Activate with profile: `cloudflared` (or `all`).

```bash
# .env
CLOUDFLARE_TUNNEL_TOKEN=your-token-here
COMPOSE_PROFILES=data,obs,interface,cloudflared
```

## DGX Spark Context

DGX Spark runs as a single-node edge workstation. The external network is designed for this:

- **No multi-host orchestration** — single `docker compose` stack, one machine
- **Host ports for inference** — llama.cpp binds to host ports (`:8000`, `:8001`) for direct GPU access via `host.docker.internal`
- **No overlay networking needed** — Docker's built-in DNS on a single bridge network is sufficient
