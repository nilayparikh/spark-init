# Dashboard Standards

## Default Dashboard

- Dashboard title: `Spark Machine Overview`
- Folder: `Observability`
- Refresh interval: `5s`
- Default home dashboard path points to the provisioned machine dashboard JSON.

## Provisioned Dashboards

- `Spark Machine Overview`: fast status view with top-level saturation, disk capacity, GPU thermals, and split journal summaries.
- `Spark Machine Signals`: detailed CPU, memory, filesystem, disk, network, and GPU signal dashboard.
- `Spark Machine Logs`: dedicated log dashboard for kernel and NVIDIA events, service and container events, disk and filesystem events, and Ubuntu maintenance history. Default time range: `24h`.
- `Spark Container Logs`: dedicated Docker stdout and stderr dashboard with `compose_project`, `profile_name`, `service_name`, and `container_name` filters. Default time range: `6h`.
- `Spark Docker Containers`: Docker-oriented dashboard for service availability, CPU, memory, throttling, network throughput, filesystem usage, uptime, and packet-drop visibility.
- `Spark Interface Providers`: normalized provider dashboard for request pressure, token throughput, context high watermark, and current slot state across interface runtimes.

## Datasource Conventions

- Metrics datasource UID: `mimir`
- Logs datasource UID: `loki`

## Alert Rules

- `Spark GPU Thermal High`: warns when GPU temperature stays above 82C for 2 minutes.
- `Spark Filesystem Pressure`: warns when a tracked filesystem stays above 85% used for 10 minutes.
- `Spark Host Saturated`: warns when CPU busy stays above 90% for 5 minutes.
- Alert rules are provisioned from file and linked back to the overview dashboard panels they explain.

## Panel Groups

- health and saturation
- host CPU, memory, disk, and network
- GPU utilization, memory, thermals, power, and clocks
- Docker service availability, CPU usage, throttling, memory working set, RSS, network throughput, filesystem usage, uptime, and packet drops
- interface-provider request pressure, token throughput, and context saturation
- interface-provider slot state and output progress
- Docker stdout and stderr exploration with label-driven filters and error-focused views
- split journal events for kernel and NVIDIA versus service and container activity
- disk capacity and disk event visibility
- Ubuntu maintenance and installer logs

## Query Rules

- Filter dashboards by normalized `host` and `job` labels.
- `machine-docker` is the authoritative job for Docker service panels.
- Prefer low-cardinality labels in legends.
- Prefer `compose_project` and `service_name` over raw cAdvisor container IDs in Docker panels.
- Use GPU-native labels only inside GPU-focused panels.
- Use `DCGM_FI_DEV_MEM_COPY_UTIL` for GPU memory utilization on this host unless framebuffer counters are later confirmed and introduced deliberately.
- Use normalized `llm_provider_*` metrics for cross-provider interface dashboards, and keep native provider metrics available for debugging and validation.
- Use `log_domain`, `log_category`, and `vendor` labels to split journal views before adding message regex filters.
- Keep panels readable on a single machine without requiring template drilling for basic status.
