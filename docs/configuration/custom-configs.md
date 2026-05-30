# Custom Configurations

This page documents the custom configuration files that drive the `.init` stack.

## LiteLLM Configuration

The LiteLLM proxy uses a YAML configuration file mounted at `/app/litellm-config/litellm-config.yaml`.

### Structure

```
interfaces/config/litellm/
├── litellm-config.yaml          # Root config — includes provider fragments
└── providers/                   # Per-provider routing fragments
    ├── azure-foundry.yaml       # Azure Foundry models
    ├── nvidia-ai-endpoints.yaml  # NVIDIA AI Endpoints
    └── deepseek.yaml            # DeepSeek API
```

The root config uses `include` directives to compose provider-specific routing rules. This keeps the configuration modular and easy to extend.

### Model Routing

LiteLLM routes requests based on the `model` parameter in the API call. The configuration maps model IDs to backend providers:

```yaml
model_list:
  - model_name: openai/qwen3.6_27b
    litellm_params:
      model: openai/qwen3.6_27b
      api_base: http://host.docker.internal:8000/v1
      api_key: sk-dummy

  - model_name: openai/Kimi-K2.6-1
    litellm_params:
      model: azure/Kimi-K2.6-1
      api_base: https://tuts.services.ai.azure.com/openai/v1
```

### Adding a New Provider

1. Create a new YAML fragment in `interfaces/config/litellm/providers/`
2. Add the provider's models and routing rules
3. Include the fragment in `litellm-config.yaml`
4. Restart the LiteLLM container: `docker compose restart litellm`

## Chat Templates

Qwen 3.6 models use a custom Jinja chat template mounted into the llama.cpp container:

```
interfaces/config/qwen3.6/chat_template.jinja
```

The template is loaded with these llama.cpp flags:

```
--jinja --chat-template-file /workspace/chat_template.jinja
--reasoning on --reasoning-format deepseek
```

### Template Purpose

The chat template ensures proper formatting for:

- Multi-turn conversations with system, user, and assistant roles
- Tool call responses with XML-tagged content
- Reasoning budget allocation (512 tokens)

## Alloy Configuration

Grafana Alloy uses an HCL pipeline configuration at `observability/config/config.alloy`:

```hcl
prometheus.exporter.unix "host" {
  # Collects CPU, memory, disk metrics every 10 seconds
}

discovery.docker "interfaces" {
  # Discovers running containers and their labels
}

loki.source.journal "system" {
  # Collects systemd journal entries with normalized labels
}
```

### Label Conventions

All metrics and logs share these standard labels:

- `host` — Machine hostname or identifier
- `role` — Service role (e.g., `inference`, `proxy`, `collector`)
- `environment` — Deployment environment (e.g., `local`, `staging`)
- `stack` — Platform identifier (`.init`)

## Mimir Configuration

Mimir runs in single-binary mode with filesystem-backed storage. Configuration at `observability/config/mimir-config.yaml`:

```yaml
mimir:
  multitenancy_enabled: false
  blocks_storage:
    backend: filesystem
    filesystem:
      directory: /mimir/tsdb
```

## Loki Configuration

Loki runs in single-binary mode with filesystem-backed storage. Configuration at `observability/config/loki-config.yaml`:

```yaml
loki:
  storage_config:
    tsdb_shipper:
      active_read_directory: /loki/tsdb-shipper-active
      cache_location: /loki/tsdb-shipper-cache
  compactor:
    working_directory: /loki/compactor
```

## Grafana Provisioning

Grafana provisions data sources, dashboards, and alert rules from files in `observability/config/grafana/provisioning/`:

```
observability/config/grafana/provisioning/
├── datasources/                  # Data source configurations
│   ├── mimir.yaml                # Mimir metrics backend
│   └── loki.yaml                 # Loki logs backend
├── dashboards/                   # Dashboard definitions
│   └── *.json                    # JSON dashboard files
└── alerting/                     # Alert rule groups
    └── *.yaml                    # Alert rule definitions
```

### Provisioning Behavior

- Grafana reads provisioning files on startup and when the config volume changes
- Dashboards are auto-imported and updated from file
- Data sources are created with the exact connection parameters defined in YAML
- Alert rules are loaded into Mimir's alert manager
