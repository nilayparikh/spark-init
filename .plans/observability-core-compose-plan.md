# Observability Core Compose Plan

## Outcome

- Implement a lightweight personal observability foundation rooted at the repository level with Docker Compose `include:`.
- Keep the composition model extendable so future modules can be added as new root-level includes without restructuring the existing stack.
- Use filesystem-backed Grafana Mimir and Grafana Loki to avoid unnecessary MinIO overhead for a trusted single-node deployment.
- Keep PostgreSQL as the shared platform database service, while isolating Grafana into its own dedicated database so future modules can follow the same separation pattern.

## Architecture Decisions

- The root `docker-compose.yml` stays minimal and only composes module files.
- `data/` owns shared persistence concerns and the shared PostgreSQL service.
- `observability/` owns Alloy, Mimir, Loki, Grafana, and all observability-specific configuration.
- Durable backend state lives under `data/storage/`:
	- PostgreSQL data
	- Mimir local TSDB and object-store filesystem state
	- Loki local TSDB filesystem state
- Observability-local mutable state lives under `observability/volumes/`:
	- Alloy positions and local state
	- Grafana plugin/cache state while its canonical application data remains in PostgreSQL
- Stable container naming is enforced with `container_name` values matching service names: `postgres`, `mimir`, `loki`, `alloy`, `grafana`.
- Profiles remain the control surface for selective startup:
	- `storage`
	- `core-telemetry`
	- `ingestion-edge`
	- `visualization`
- Health-gated boot is used where the image provides a reliable probe path. PostgreSQL uses `pg_isready`. The Grafana Mimir, Loki, and Alloy images are effectively distroless, so downstream ordering uses deterministic `service_started` dependencies plus built-in client retry behavior instead of brittle shell-based healthchecks.

## Files To Maintain

- `docker-compose.yml`
- `data/docker-compose.data.yml`
- `data/config/postgres-init/010-grafana.sql`
- `observability/docker-compose.obs.yml`
- `observability/config/config.alloy`
- `observability/config/mimir-config.yaml`
- `observability/config/loki-config.yaml`
- `observability/config/alertmanager-fallback.yaml`
- `observability/config/grafana/provisioning/datasources/datasources.yaml`

## Runtime Expectations

- Alloy scrapes host metrics through mounted host `proc`, `sys`, and rootfs paths.
- Alloy forwards metrics directly to Mimir at `http://mimir:9009/api/v1/push`.
- Alloy tails host log files from `/var/log` through the mounted host rootfs and forwards them directly to Loki at `http://loki:3100/loki/api/v1/push`.
- Mimir exposes Prometheus-compatible APIs at the root path so Grafana can use a standard Prometheus datasource without a standalone Prometheus server.
- Grafana provisions Mimir and Loki datasources automatically and stores its application data in PostgreSQL.

## Validation Plan

- Run `docker compose config` from the repository root.
- Start the stack by profile from the repository root.
- Confirm container state with `docker compose ps`.
- Confirm PostgreSQL readiness through Compose health status.
- Confirm Mimir readiness with `curl http://127.0.0.1:9009/ready`.
- Confirm Loki readiness with `curl http://127.0.0.1:3100/ready`.
- Confirm Alloy is running and exposing its UI on `http://127.0.0.1:12345/`.
- Query Mimir for a simple metric such as `up` after Alloy has been running long enough to remote write samples.
- Query Loki for at least one host log line sourced from `/var/log`.
- Confirm Grafana starts with provisioned datasources backed by PostgreSQL.