# Data Layer — PostgreSQL

Shared PostgreSQL for the `.init` stack on DGX Spark.

## Role

PostgreSQL is the shared persistence layer for two consumers:

| Consumer | Database | Purpose |
|---|---|---|
| **Grafana** | `grafana` | Dashboards, users, data sources |
| **LiteLLM** | `litellm_interface` | Spend logs, provider config, model metadata |

Both databases and their users are created automatically on first start via bootstrap scripts in `config/postgres-init/`.

## DGX Spark Context

PostgreSQL runs in a container alongside the inference and observability stacks, sharing the `init_default` network. On DGX Spark's 128 GB unified memory, Postgres uses negligible resources (~200 MB RSS) — it's never a bottleneck.

The database stores LiteLLM's usage logs, which is valuable for tracking token consumption across local and cloud models from a single DGX Spark node.

## Files

| Path | Purpose |
|---|---|
| `docker-compose.data.yml` | Service definition with health check (`pg_isready`) |
| `config/postgres-init/010-grafana.sh` | Bootstrap: creates grafana database + user |
| `config/postgres-init/020-litellm-interface.sh` | Bootstrap: creates litellm_interface database + user |
| `storage/` | Runtime data directory (git-ignored) |

## Depends On

- `network/` — requires `init_default` external network

## Depended On By

- `observability/` — Grafana requires Postgres before starting
- `interfaces/` — LiteLLM requires Postgres before starting
