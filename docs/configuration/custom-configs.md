# Custom Configurations

This page documents the custom configuration files that drive the `.init` stack.

## LiteLLM Configuration

The LiteLLM proxy uses a YAML configuration file mounted at `/app/litellm-config/config.yaml`.

### Structure

```
interfaces/config/litellm/
├── config.yaml                  # Root config — includes provider fragments
└── providers/                   # Per-provider routing fragments
    ├── azure-foundry.yaml       # Azure Foundry models (Kimi K2.6, DeepSeek V4 Flash)
    ├── dgx.yaml                 # Local DGX models (Qwen 3.6 27B, 35B A3B)
    ├── nvidia.yaml              # NVIDIA AI Endpoints (DeepSeek, MiniMax, Kimi)
    └── deepseek.yaml            # DeepSeek native API (V4 Flash, V4 Pro)
```

The root config uses `include` directives to compose provider-specific routing rules. This keeps the configuration modular and easy to extend.

### Model Routing

LiteLLM routes requests based on the `model` parameter in the API call. The configuration maps model IDs to backend providers through the provider fragments. Each fragment defines `model_list` entries with routing parameters and `model_info` metadata.

Anthropic-compatible aliases (`anthropic/...` and `claude-*`) are published alongside the OpenAI-facing names (`openai/...`) so Claude Code can discover models through gateway discovery.

### Adding a New Provider

1. Create a new YAML fragment in `interfaces/config/litellm/providers/`
2. Add the provider's models and routing rules
3. Include the fragment in `config.yaml`
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
- Reasoning budget allocation

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

All metrics and logs share standard platform labels for cross-service correlation. See [Labeling Standard](../observability/labeling.md) for the full label taxonomy.

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
