# Environment Variables

All configuration flows through the `.env` file. This page catalogs every variable grouped by component.

## How It Works

1. Copy `.env.example` to `.env` (the latter is git-ignored)
2. Edit `.env` with your local settings
3. Docker Compose automatically loads all variables into service containers
4. Set `COMPOSE_PROFILES` to control which services start

```bash
cp .env.example .env
# Edit .env, then:
docker compose up -d
```

## General

| Variable           | Default                                 | Description            |
| ------------------ | --------------------------------------- | ---------------------- |
| `COMPOSE_PROFILES` | `data,obs,interface,llama-qwen-3-6-27b` | Stack shape selection. |

## Data / Postgres

| Variable                       | Default                | Description                              |
| ------------------------------ | ---------------------- | ---------------------------------------- |
| `DATA_POSTGRES_IMAGE`          | `postgres:latest`      | PostgreSQL Docker image.                 |
| `DATA_POSTGRES_CONTAINER_NAME` | `postgres`             | Container name for the Postgres service. |
| `DATA_POSTGRES_BIND_HOST`      | `0.0.0.0`              | Host interface to bind PostgreSQL to.    |
| `DATA_POSTGRES_PORT`           | `5432`                 | Host port for PostgreSQL.                |
| `DATA_POSTGRES_DB`             | `platform`             | Default database name.                   |
| `DATA_POSTGRES_USER`           | `platform_admin`       | PostgreSQL superuser.                    |
| `DATA_POSTGRES_PASSWORD`       | `platform_admin_local` | PostgreSQL superuser password.           |

## Observability / Grafana

| Variable                 | Default                      | Description                                                    |
| ------------------------ | ---------------------------- | -------------------------------------------------------------- |
| `GRAFANA_DB_NAME`        | `grafana`                    | Grafana's database name (inside shared Postgres).              |
| `GRAFANA_DB_USER`        | `grafana`                    | Grafana's database user.                                       |
| `GRAFANA_DB_PASSWORD`    | `grafana_local_obsv`         | Grafana's database password.                                   |
| `GRAFANA_ADMIN_USER`     | `admin`                      | Grafana admin username.                                        |
| `GRAFANA_ADMIN_PASSWORD` | `local_observability_admin`  | Grafana admin password.                                        |
| `GRAFANA_DOMAIN`         | `barsana.local`              | Domain for Grafana's root URL.                                 |
| `GRAFANA_ROOT_URL`       | `http://barsana.local:3000/` | Full root URL for Grafana (used in alerts and embedded links). |
| `LOKI_RETENTION_PERIOD`  | `2d`                         | Log retention period for Loki.                                 |
| `MIMIR_RETENTION_PERIOD` | `7d`                         | Metric retention period for Mimir.                             |

## LiteLLM Proxy

| Variable                 | Default                                                                                  | Description                                                          |
| ------------------------ | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `LITELLM_IMAGE`          | `docker.litellm.ai/berriai/litellm:latest`                                               | LiteLLM Docker image.                                                |
| `LITELLM_CONTAINER_NAME` | `litellm`                                                                                | Container name for the LiteLLM proxy.                                |
| `LITELLM_PORT`           | `4000`                                                                                   | Host port for the LiteLLM proxy.                                     |
| `LITELLM_BIND_HOST`      | `0.0.0.0`                                                                                | Host interface to bind LiteLLM to.                                   |
| `LITELLM_LOG_LEVEL`      | `INFO`                                                                                   | Logging level for LiteLLM (DEBUG, INFO, WARNING, ERROR).             |
| `LITELLM_MASTER_KEY`     | `sk-interface-ui-local`                                                                  | Master API key for the LiteLLM proxy. **Change this in production.** |
| `INTERFACE_DATABASE_URL` | `postgresql://litellm_interface:litellm_interface_local@postgres:5432/litellm_interface` | LiteLLM's database connection string.                                |
| `DGX_SPARK_M_BASE_URL`   | `http://host.docker.internal:8000/v1`                                                    | Upstream URL for the DGX Spark M (Qwen 3.6 27B) backend.             |
| `DGX_SPARK_M_API_KEY`    | `sk-dummy`                                                                               | API key placeholder for the DGX Spark M backend.                     |
| `DGX_SPARK_M_MODEL`      | `openai/qwen3.6_27b`                                                                     | Model identifier LiteLLM uses for the DGX Spark M provider.          |
| `DGX_SPARK_S_BASE_URL`   | `http://host.docker.internal:8001/v1`                                                    | Upstream URL for the DGX Spark S (Qwen 3.6 35B A3B) backend.         |
| `DGX_SPARK_S_API_KEY`    | `sk-dummy`                                                                               | API key placeholder for the DGX Spark S backend.                     |
| `DGX_SPARK_S_MODEL`      | `openai/qwen3.6_35b_a3b`                                                                 | Model identifier LiteLLM uses for the DGX Spark S provider.          |

## Cloud Provider Keys

| Variable                     | Default                                        | Description                                            |
| ---------------------------- | ---------------------------------------------- | ------------------------------------------------------ |
| `MICROSOFT_FOUNDRY_API_BASE` | `https://tuts.services.ai.azure.com/openai/v1` | Azure Foundry API endpoint.                            |
| `MICROSOFT_FOUNDRY_API_KEY`  | _(required for cloud models)_                  | API key for Azure Foundry.                             |
| `AZURE_ORCHESTRATOR_MODEL`   | `openai/Kimi-K2.6-1`                           | Default cloud orchestrator model ID.                   |
| `OPENCODE_ZEN_BASE_URL`      | `https://opencode.ai/zen/v1`                   | OpenCode Zen API base URL for the Zen provider models. |
| `OPENCODE_ZEN_API_KEY`       | _(required for OpenCode Zen)_                  | API key for OpenCode Zen.                              |
| `NVIDIA_BASE_URL`            | `https://integrate.api.nvidia.com/v1`          | NVIDIA AI Endpoints base URL.                          |
| `NVIDIA_API_KEY`             | _(required for NVIDIA models)_                 | NVIDIA API key.                                        |
| `DEEPSEEK_BASE_URL`          | `https://api.deepseek.com`                     | DeepSeek API base URL.                                 |
| `DEEPSEEK_API_KEY`           | _(required for DeepSeek models)_               | DeepSeek API key.                                      |

## llama.cpp Backend (27B)

| Variable                             | Default                               | Description                                                                                    |
| ------------------------------------ | ------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `LLAMA_CPP_TAG`                      | `b9222`                               | llama.cpp git tag or commit to build from.                                                     |
| `LLAMA_QWEN_3_6_27B_IMAGE_REPO`      | `nilayparikh/llama-cpp-dgx`           | Docker image repository for the llama.cpp backend.                                             |
| `LLAMA_QWEN_3_6_27B_CONTAINER_NAME`  | `llama-qwen-3-6-27b`                  | Container name for the 27B model backend.                                                      |
| `LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH` | _(required)_                          | Absolute path to the GGUF model file on the host filesystem.                                   |
| `LLAMA_QWEN_3_6_27B_HOST_PORT`       | `8000`                                | Host port for the 27B model backend.                                                           |
| `LLAMA_QWEN_3_6_27B_BIND_HOST`       | `0.0.0.0`                             | Host interface to bind the backend to.                                                         |
| `LLAMA_QWEN_3_6_27B_CONTAINER_PORT`  | `8080`                                | Internal container port for llama.cpp.                                                         |
| `DGX_SPARK_M_BASE_URL`               | `http://host.docker.internal:8000/v1` | Base URL for the DGX Spark M backend (as seen from LiteLLM).                                   |
| `DGX_SPARK_M_API_KEY`                | `sk-dummy`                            | API key for the DGX Spark M backend (llama.cpp doesn't require auth, but LiteLLM expects one). |
| `DGX_SPARK_M_MODEL`                  | `openai/qwen3.6_27b`                  | Model ID exposed by LiteLLM for the DGX Spark M model.                                         |

## llama.cpp Backend (35B A3B)

| Variable                                   | Default                               | Description                                                  |
| ------------------------------------------ | ------------------------------------- | ------------------------------------------------------------ |
| `LLAMA_QWEN_3_6_35B_A3B_CONTAINER_NAME`    | `llama-qwen-3-6-35b-a3b`              | Container name for the 35B A3B backend.                      |
| `LLAMA_QWEN_3_6_35B_A3B_IMAGE_REPO`        | `nilayparikh/llama-cpp-dgx`           | Docker image repository for the 35B A3B backend.             |
| `LLAMA_QWEN_3_6_35B_A3B_GGUF_MODEL_PATH`   | _(required)_                          | Absolute path to the 35B A3B GGUF model file.                |
| `LLAMA_QWEN_3_6_35B_A3B_MMPROJ_MODEL_PATH` | _(required for vision)_               | Absolute path to the multimodal projector GGUF file.         |
| `LLAMA_QWEN_3_6_35B_A3B_HOST_PORT`         | `8001`                                | Host port for the 35B A3B backend.                           |
| `LLAMA_QWEN_3_6_35B_A3B_BIND_HOST`         | `0.0.0.0`                             | Host interface to bind the 35B A3B backend to.               |
| `LLAMA_QWEN_3_6_35B_A3B_CONTAINER_PORT`    | `8080`                                | Internal container port for llama.cpp.                       |
| `DGX_SPARK_S_BASE_URL`                     | `http://host.docker.internal:8001/v1` | Base URL for the DGX Spark S backend (as seen from LiteLLM). |
| `DGX_SPARK_S_API_KEY`                      | `sk-dummy`                            | API key for the DGX Spark S backend.                         |
| `DGX_SPARK_S_MODEL`                        | `openai/qwen3.6_35b_a3b`              | Model ID exposed by LiteLLM for the DGX Spark S model.       |

## Security Notes

- **Never commit `.env`** — it is git-ignored. Only `.env.example` is committed.
- **Change default passwords** before exposing the stack to any network beyond localhost.
- **Rotate `LITELLM_MASTER_KEY`** regularly and use a strong, unique value.
- `DGX_SPARK_M_API_KEY` and `DGX_SPARK_S_API_KEY` can remain `sk-dummy` because llama.cpp doesn't enforce authentication — the proxy handles auth before requests reach the backend.
