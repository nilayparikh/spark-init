# Data Env Reference

These variables live in the root `.env` file and affect the data stack directly or through downstream consumers.

## Postgres Container

| Variable                       | Default                           | Meaning                                             |
| ------------------------------ | --------------------------------- | --------------------------------------------------- |
| `DATA_POSTGRES_IMAGE`          | `postgres:latest`                 | Image used for the shared Postgres service.         |
| `DATA_POSTGRES_CONTAINER_NAME` | `postgres`                        | Container name.                                     |
| `DATA_POSTGRES_BIND_HOST`      | `0.0.0.0`                         | Host bind address for Postgres.                     |
| `DATA_POSTGRES_PORT`           | `5432`                            | Host port forwarded to the container.               |
| `DATA_POSTGRES_DB`             | `platform`                        | Default database created by the image entrypoint.   |
| `DATA_POSTGRES_USER`           | `platform_admin`                  | Default admin user created by the image entrypoint. |
| `DATA_POSTGRES_PASSWORD`       | `platform_admin_local`            | Default admin password.                             |
| `DATA_POSTGRES_PGDATA`         | `/var/lib/postgresql/data/pgdata` | Internal PostgreSQL data directory.                 |

## Grafana Bootstrap

| Variable                 | Default                      | Used by                                      |
| ------------------------ | ---------------------------- | -------------------------------------------- |
| `GRAFANA_DB_NAME`        | `grafana`                    | Postgres init script, Grafana compose config |
| `GRAFANA_DB_USER`        | `grafana`                    | Postgres init script, Grafana compose config |
| `GRAFANA_DB_PASSWORD`    | `grafana_local_obsv`         | Postgres init script, Grafana compose config |
| `GRAFANA_ADMIN_USER`     | `admin`                      | Grafana compose config                       |
| `GRAFANA_ADMIN_PASSWORD` | `local_observability_admin`  | Grafana compose config                       |
| `GRAFANA_DOMAIN`         | `barsana.local`              | Grafana compose config                       |
| `GRAFANA_ROOT_URL`       | `http://barsana.local:3000/` | Grafana compose config                       |

## LiteLLM Database Bootstrap

| Variable                 | Default                                                              | Used by                                 |
| ------------------------ | -------------------------------------------------------------------- | --------------------------------------- |
| `INTERFACE_DB_NAME`      | `litellm_interface`                                                  | Postgres init script                    |
| `INTERFACE_DB_USER`      | `litellm_interface`                                                  | Postgres init script                    |
| `INTERFACE_DB_PASSWORD`  | `litellm_interface_local`                                            | Postgres init script                    |
| `INTERFACE_DATABASE_URL` | `postgresql://litellm_interface:...@postgres:5432/litellm_interface` | LiteLLM compose config and LiteLLM YAML |
