# Data File Index

## Files

| File                                                 | Purpose                                                                                                         | Key parameters / knobs                                             |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `data/docker-compose.data.yml`                       | Starts the shared Postgres container, exports port `5432`, and passes bootstrap credentials into the container. | `DATA_POSTGRES_*`, `GRAFANA_DB_*`, `INTERFACE_DB_*`.               |
| `data/config/postgres-init/010-grafana.sh`           | Creates or updates the Grafana role and creates the Grafana database on first bootstrap.                        | `GRAFANA_DB_NAME`, `GRAFANA_DB_USER`, `GRAFANA_DB_PASSWORD`.       |
| `data/config/postgres-init/020-litellm-interface.sh` | Creates or updates the LiteLLM role and creates the interface database on first bootstrap.                      | `INTERFACE_DB_NAME`, `INTERFACE_DB_USER`, `INTERFACE_DB_PASSWORD`. |

## Operational Notes

- The two init scripts are now shell scripts instead of static SQL so that role names and passwords can be driven from the root `.env` file.
- These init scripts only run during initial database creation. If the Postgres volume already exists, changing the env values does not retroactively rebuild users or databases unless you reinitialize the volume or run the equivalent SQL manually.
