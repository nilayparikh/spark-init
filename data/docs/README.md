# Data Stack

The data stack provides the shared Postgres instance used by the interface layer and Grafana.

## Scope

| Surface            | Primary file                                         | Purpose                                                                  |
| ------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| Compose entrypoint | `data/docker-compose.data.yml`                       | Starts Postgres with persistent storage and init scripts.                |
| Bootstrap script   | `data/config/postgres-init/010-grafana.sh`           | Creates the Grafana role and database using env-driven values.           |
| Bootstrap script   | `data/config/postgres-init/020-litellm-interface.sh` | Creates the LiteLLM interface role and database using env-driven values. |

## What Gets Created

1. The main `platform` database defined by `DATA_POSTGRES_DB`.
2. The `grafana` database and role defined by `GRAFANA_DB_*`.
3. The `litellm_interface` database and role defined by `INTERFACE_DB_*`.

## Storage Layout

- `data/storage/postgres`: persistent PostgreSQL data volume bind mount.
- `data/config/postgres-init`: one-time initialization scripts used only during a fresh database bootstrap.

## Documentation Map

- `file-index.md`: file-by-file purpose and runtime notes.
- `env-reference.md`: the root `.env` variables that drive the data stack and its database consumers.
