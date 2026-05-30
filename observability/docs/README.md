# Observability Standards

This directory is the contract for how the local observability stack is organized.

- `architecture.md`: stack shape, service responsibilities, dashboard layout, and alerting decisions.
- `labeling.md`: required labels, reserved values, and host-specific metric conventions.
- `log-coverage.md`: journal and file log coverage for this Ubuntu-based Spark machine.
- `dashboard-standards.md`: dashboard expectations, refresh policy, datasource conventions, and alert inventory.
- Docker container telemetry is collected through cAdvisor and surfaced in the `Spark Docker Containers` dashboard.
- Docker container stdout and stderr logs are collected through Alloy Docker discovery and surfaced in the `Spark Container Logs` dashboard.
- `llamacpp-telemetry.md`: native llama.cpp metrics, slot metadata, and what they do or do not tell us.
- `interface-telemetry-standard.md`: the provider-agnostic metric template future interface runtimes should be transformed into.

Keep these documents updated whenever collectors, labels, or dashboards change.
