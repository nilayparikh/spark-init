# Architecture

## Scope

This observability stack is a personal, local-first platform for the Spark DGX machine. It prioritizes:

- low operational weight
- trusted local storage
- stable labels and dashboard layout
- extendability for future modules

## Components

- `postgres`: shared platform database. Grafana uses its own database and user inside the shared instance.
- `mimir`: local metrics backend, single-binary, filesystem-backed.
- `loki`: local log backend, single-binary, filesystem-backed.
- `alloy`: host metrics and log collector.
- `cadvisor`: Docker container telemetry collector.
- `llamacpp-telemetry`: lightweight bridge exporter for llama.cpp native metrics, slot state, and props metadata.
- `gpu-telemetry`: NVIDIA DCGM exporter for GPU telemetry.
- `grafana`: UI and dashboard layer.

## Collection Strategy

- Host telemetry comes from Alloy's `prometheus.exporter.unix` collector.
- Docker container telemetry comes from cAdvisor and is scraped every 15 seconds.
- Interface-specific endpoint scrapes are gated by Docker container discovery so inactive profiles do not produce dead scrape targets or mislabel whichever runtime currently owns a shared host port.
- GPU telemetry comes from DCGM exporter and is scraped every 5 seconds.
- llama.cpp runtime telemetry comes from the native `/metrics` endpoint plus a lightweight exporter that also surfaces `/slots` and `/props` state into Prometheus format.
- System and NVIDIA events come primarily from the persistent systemd journal.
- Journal logs are enriched with normalized `log_domain`, `log_category`, and `vendor` labels so dashboards can split kernel and NVIDIA activity from service and container activity.
- Ubuntu text logs that are not ideal to rely on through journal replay alone are tailed directly from disk.

## Design Decisions

- Metrics and logs share the same host, role, environment, and stack labels.
- `job` names are normalized for dashboards instead of exposing raw collector names.
- Interface providers keep their native exporter metrics when available, but also emit normalized `llm_provider_*` metrics so Grafana can use one dashboard shape across runtimes.
- Journal is the primary Linux log surface to avoid relying on rotating text files for kernel and system service events.
- File tails are restricted to platform maintenance logs to avoid duplicate ingestion from syslog-style files already present in the journal.
- Grafana provisions four machine dashboards from file: overview, detailed host signals, dedicated logs, and Docker container telemetry.
- Grafana also provisions a dedicated container log dashboard for Docker stdout and stderr streams with compose project, profile, service, and container filters.
- Grafana also provisions a provider-agnostic interface dashboard for runtime request and token telemetry.
- Grafana alert rules are also provisioned from file so thermal, filesystem, and host saturation checks stay versioned with the rest of the stack.
- GPU memory utilization currently uses `DCGM_FI_DEV_MEM_COPY_UTIL` because the active DCGM exporter surface on this host does not expose `DCGM_FI_DEV_FB_*` counters.

## Profiles

- `data`: durable shared data services.
- `obs`: observability services and collectors.
