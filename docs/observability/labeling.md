# Labeling Standard

## Required Metric Labels

- `cluster_tenant`: logical tenant or machine group. Current value: `spark_dgx_core`.
- `environment`: deployment environment. Current value: `personal`.
- `stack`: observability stack identifier. Current value: `observability-core`.
- `site`: physical or logical site. Current value: `barsana`.
- `role`: machine role. Current value: `spark-dgx`.
- `host`: stable machine identifier. Current value: `barsana`.
- `job`: normalized collector or workload name.
- `instance`: stable scrape identity. Current value for host-scoped metrics: `barsana`.
- `compose_project`: Docker Compose project name for cAdvisor-derived container telemetry.
- `provider_family`: interface runtime family such as `llamacpp`, `vllm`, or `sglang`.
- `interface_name`: repo-local interface name. Current value for llama.cpp: `llama-mtp`.
- `interface_instance`: stable deployment identity. Current value for llama.cpp: `llama-mtp-local`.
- `service_name`: runtime service name. Current value for llama.cpp: `llama-server`.
- `model_alias`: API-facing model identifier when the provider exposes one. Current value for llama.cpp: `qwen3.6_27b`.
- `telemetry_scope`: normalized collector scope. Current values include `interface` and `docker`.

## Required Log Labels

- `cluster_tenant`
- `environment`
- `stack`
- `site`
- `role`
- `host`
- `job`
- `source_type`
- `log_domain`: top-level split used by log dashboards. Current journal values: `kernel`, `service`.
- `log_category`: normalized log subtype. Current values include `system-service`, `kernel`, `gpu-driver`, `container-runtime`, `cloud-init`, `package-management`, and `installer`.
- `vendor`: normalized vendor or subsystem owner. Current journal values: `linux`, `container`, `nvidia`.

## Journal-Derived Log Labels

- `unit`: systemd unit name when available.
- `service_name`: journal syslog identifier when available.
- `transport`: journal transport, such as `kernel` or `syslog`.
- `priority`: journal priority keyword.

## Metric Conventions

- `machine-linux` remains the authoritative host metric job for CPU, memory, disk, and network panels.
- `machine-docker` remains the authoritative Docker container metric job for service-level CPU, memory, filesystem, and network panels.
- `machine-gpu` remains the authoritative GPU metric job.
- `interface-llm` is the normalized job for interface-provider metrics that are intended to work across runtimes.
- Preserve native provider exporter metric names when they exist, but also expose the normalized `llm_provider_*` series for cross-provider dashboards.
- On this host, GPU memory utilization dashboards use `DCGM_FI_DEV_MEM_COPY_UTIL` because the DCGM exporter currently exposes memory activity but not `DCGM_FI_DEV_FB_*` framebuffer counters.
- Do not build GPU memory occupancy panels that assume `DCGM_FI_DEV_FB_FREE` or `DCGM_FI_DEV_FB_USED` without first verifying those counters exist in Mimir.

## Normalized Job Names

- `machine-linux`: host telemetry from Alloy's Unix exporter.
- `machine-docker`: Docker container telemetry from cAdvisor with normalized compose and service labels.
- `machine-gpu`: GPU telemetry from DCGM exporter.
- `interface-llm`: standardized interface-provider metrics and raw provider metrics with normalized labels.
- `machine-journal`: systemd journal logs.
- `ubuntu-cloud-init`: cloud-init text logs.
- `ubuntu-apt`: apt history and terminal logs.
- `ubuntu-dpkg`: dpkg transaction log.
- `ubuntu-installer`: installer, curtin, and subiquity logs.

## Cardinality Rules

- Keep labels low-cardinality and stable across restarts.
- Do not add PID, full command line, request ID, session ID, or user-specific labels to shared collectors.
- Prefer normalized semantic labels over raw file paths in dashboards.
- Prefer `compose_project` and `service_name` over raw cAdvisor `name` values in Docker panels.
- Prefer `log_domain`, `log_category`, and `vendor` for log dashboard slicing before falling back to message regex filters.
- Do not use request identifiers as metric labels for interface-provider telemetry; if a runtime exposes task identifiers, expose them as metric values instead of labels.
- Preserve exporter-native GPU labels such as `gpu` and `UUID` for compatibility, but build dashboards around stable normalized labels first.
