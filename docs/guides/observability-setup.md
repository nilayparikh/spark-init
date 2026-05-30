# Observability Setup

This guide walks you through the full observability stack: metrics collection with Grafana Alloy, time-series storage with Mimir, log aggregation with Loki, and visualization with Grafana dashboards.

## Architecture Overview

The observability layer consists of five services that work together:

```
Service        → Collected By    → Stored In    → Visualized In
─────────────────────────────────────────────────────────────────
Host (CPU/RAM) → Alloy (node_exp) → Mimir        → Grafana (machine-observability)
GPU (DCGM)     → Alloy (dcgm)     → Mimir        → Grafana (machine-observability)
Docker         → cAdvisor → Alloy → Mimir        → Grafana (docker-containers)
LiteLLM        → Alloy (scrape)   → Mimir        → Grafana (llamacpp-observability)
llama.cpp      → Alloy (scrape)   → Mimir        → Grafana (llamacpp-observability)
Container logs → Alloy (docker)   → Loki         → Grafana (container-logs)
Systemd journal→ Alloy (journal)  → Loki         → Grafana (machine-logs)
```

## Starting the Observability Stack

Enable the `obs` and `data` profiles in `.env`:

```bash
COMPOSE_PROFILES=data,obs
```

Then start the stack:

```bash
docker compose up -d
```

This launches five containers:

| Service | Image | Host Port | Purpose |
|---------|-------|-----------|---------|
| Grafana | `grafana/grafana-oss:latest` | 3000 | Dashboard UI |
| Mimir | `grafana/mimir:latest` | 9009 | Metrics storage (Prometheus-compatible) |
| Loki | `grafana/loki:latest` | 3100 | Log storage |
| Alloy | `grafana/alloy:latest` | — | Metrics & log collector |
| cAdvisor | `gcr.io/cadvisor/cadvisor:v0.52.1` | — | Container resource metrics |
| DCGM Exporter | `nvcr.io/nvidia/k8s/dcgm-exporter` | 9400 | GPU telemetry |

## Alloy Configuration

Alloy is the central collector. Its configuration lives at `observability/config/config.alloy` and is mounted into the Alloy container. The config defines three classes of collection:

### Metrics Collection

Alloy scrapes metrics from five sources and forwards them to Mimir:

1. **Host metrics** — CPU, memory, disk via `prometheus.exporter.unix` (scraped every 5s)
2. **GPU metrics** — DCGM exporter at `gpu-telemetry:9400` (every 5s)
3. **Docker/container metrics** — cAdvisor at `cadvisor:8080` (every 15s)
4. **LiteLLM metrics** — auto-discovered via Docker labels at `litellm:4000/metrics/` (every 30s)
5. **llama.cpp metrics** — auto-discovered at `llama-qwen-3-6-27b:8080` (every 15s)

Each scrape pipeline applies a `prometheus.relabel` component that enriches raw metrics with standard labels:

```
cluster_tenant, environment, stack, site, role, host, instance, job
```

These labels enable cross-service correlation in Grafana. For example, filtering by `environment="personal"` and `stack="observability-core"` shows all metrics from the observability layer.

### Log Collection

Alloy collects logs from three sources and ships them to Loki:

1. **Docker container logs** — via `loki.source.docker`, reading all containers from the Docker socket
2. **systemd journal** — via `loki.source.journal`, reading `/host/root/var/log/journal`
3. **File tails** — via `loki.source.file`, covering cloud-init, dpkg, apt, and installer logs

Each log stream is tagged with structured labels (`source_type`, `log_domain`, `log_category`, `vendor`) for filtering in Grafana Explore.

### Service Discovery

Alley uses Docker-based service discovery to find LiteLLM and llama.cpp metrics endpoints dynamically:

```alloy
discovery.docker "containers" {
  host = "unix:///var/run/docker.sock"
}

discovery.relabel "litellm_metrics_target" {
  targets = discovery.docker.containers.targets

  rule {
    source_labels = ["__meta_docker_container_label_com_docker_compose_service"]
    action        = "keep"
    regex         = "litellm"
  }
}
```

This means new services that match the label pattern are automatically picked up on the next scrape cycle — no config reload required.

## Grafana Dashboards

Dashboards are auto-provisioned from `observability/config/grafana/provisioning/`.

### Dashboard Provider

```yaml
# observability/config/grafana/provisioning/dashboards/dashboard-providers.yaml
apiVersion: 1
providers:
  - name: "machine"
    folder: "Machine"
    options:
      path: /etc/grafana/provisioning/dashboards/machine
      folderUid: machine
```

### Available Dashboards

| Dashboard File | Description |
|---------------|-------------|
| `spark-machine-observability.json` | Host CPU, memory, disk, and GPU metrics |
| `spark-machine-signals.json` | Combined metrics and log signals overview |
| `spark-container-logs.json` | Docker container log streams |
| `spark-docker-containers.json` | Container resource usage (CPU, memory, network) |
| `spark-machine-logs.json` | Systemd journal and file logs |
| `spark-llamacpp-observability.json` | llama.cpp inference metrics (tokens/s, queue depth, VRAM) |
| `spark-vllm-observability.json` | vLLM inference metrics (if vLLM profile is active) |

### Data Sources

Grafana auto-provisions Mimir and Loki as data sources:

```yaml
# observability/config/grafana/provisioning/datasources/datasources.yaml
apiVersion: 1
datasources:
  - name: Mimir
    type: prometheus
    url: http://mimir:9009/prometheus
    access: proxy
    isDefault: true
  - name: Loki
    type: loki
    url: http://loki:3100
    access: proxy
```

## Alerting

Alert rules live in `observability/config/grafana/provisioning/alerting/machine-alerts.yaml`. These define thresholds for GPU utilization, container health, and inference latency.

## Customizing for Your Environment

The Alloy config contains host-specific labels (`barsana`, `spark_dgx_core`). To adapt for your environment:

1. Edit `observability/config/config.alloy`
2. Replace `barsana` with your hostname
3. Replace `spark_dgx_core` with your cluster identifier
4. Update `environment` from `personal` to your environment name (e.g., `staging`, `production`)

Alternatively, use environment variables and Alloy's `${ENV_VAR}` interpolation for dynamic labeling.

## Verifying the Setup

1. Open Grafana at `http://<host>:3000`
2. Log in with `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` from `.env`
3. Navigate to **Dashboards** → **Machine** folder
4. Confirm the **Machine Observability** dashboard shows host and GPU metrics
5. Navigate to **Explore** → select **Loki** → run `{container_name="litellm"}` to verify log ingestion

> **★ Insight**
> - Alloy replaces both Prometheus and Promtail in the Grafana stack — one binary for metrics and logs.
> - Docker-based service discovery means new containers are auto-discovered; you don't need to edit config when adding inference backends.
> - The label enrichment strategy (cluster_tenant, environment, stack, site, role) provides a consistent filtering dimension across all telemetry.
