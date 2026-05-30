"Act as an expert Cloud Infrastructure Architect and DevOps Engineer. Generate a complete, ready-to-run, modular Docker Compose architecture using the official latest Grafana open-source images.

The framework must be cleanly decoupled using native Docker Compose file-extension inclusion ('include:') rules and enforce a strict folder hierarchy for storage persistence, configuration, and volume mappings.

Crucially, the architecture must implement Docker Compose PROFILES to enable targeted service selection, alongside strict conditional service dependencies ('depends_on' with 'condition: service_healthy') to orchestrate the exact initialization order across a multi-tenant, shared infrastructure.

Your output must provide a detailed text-based markdown folder hierarchy and the complete contents of every configuration file, with zero placeholders, ellipses, or omissions.

1. REPOSITORY PATH AND DIRECTORY STRUCTURE SPECIFICATION
   Produce a detailed markdown directory layout conforming exactly to these requirements:

- Root level: Contains only the primary engine orchestration file ('docker-compose.yml') and global setup files.
- Environment Persistence (/data): Houses all state databases. Contains nested subdirectories for configurations ('/data/config') and separate isolated runtime storage paths ('/data/storage').
- Observability Module (/observability): Houses telemetry containers. Contains nested subdirectories for static service configurations ('/observability/config') and specific, dedicated local directory volume mounts ('/observability/volumes').

2. ENGINE PROFILES & SERVICE DEPENDENCY ARCHITECTURE
   To cleanly manage resource scheduling and operational states, every service must be bound to a targeted profile, and enforce deterministic boot ordering:

- Docker Compose Profiles:
  - Profile 'storage': Encompasses the underlying storage engines (MinIO and PostgreSQL).
  - Profile 'core-telemetry': Encompasses the analytical database engines (Mimir and Loki).
  - Profile 'ingestion-edge': Encompasses the local collection agent (Grafana Alloy).
  - Profile 'visualization': Encompasses the graphical user interface frontend (Grafana OSS).
- Manual startup only:
  - Every service must either omit Docker restart automation or set `restart: "no"` explicitly.
  - The stack must never auto-start when the Docker daemon or host boots; operators must manually invoke `docker compose --profile ... up` for any services they want running.
- Deterministic Boot Dependencies:
  - PostgreSQL and MinIO must implement rigorous Docker 'healthcheck' parameters (using pg_isready and minio mc/curl checks respectively).
  - Mimir and Loki must implement 'depends_on' referencing MinIO, with the condition set to 'service_healthy'. They must also export their own explicit HTTP health status endpoints.
  - Grafana Alloy must implement 'depends_on' referencing Mimir and Loki, with conditions set to 'service_healthy', ensuring it never attempts to stream scraped data to uninitialized endpoints.
  - Grafana OSS must implement 'depends_on' referencing PostgreSQL with 'service_healthy'.

3. MODULAR COUPLING SPECIFICATION (ROOT 'docker-compose.yml')
   Write a clean, minimal root orchestrator file at the repository base. It must dynamically pull in backend functionality using native Docker Compose 'include' definitions:

```yaml
include:
  - ./data/docker-compose.data.yml
  - ./observability/docker-compose.obs.yml
```

4. FILE CONTENT CONFIGURATIONS TO GENERATE
   Write the complete production file blocks matching the exact folder targets specified below:

- PATH: ./data/docker-compose.data.yml
  Defines the storage layer under the 'storage' profile. Configure MinIO ('minio/minio:latest') and PostgreSQL ('postgres:latest'). All storage blocks must persist locally to paths under './data/storage/...'. Ensure explicit multi-tenant buckets ('tenant-shared-mimir-metrics' and 'tenant-shared-loki-logs') and dedicated database namespaces are fully established via setup commands.

- PATH: ./observability/docker-compose.obs.yml
  Defines Grafana Alloy ('grafana/alloy:latest' under profile 'ingestion-edge'), Grafana Mimir ('grafana/mimir:latest' under profile 'core-telemetry'), Grafana Loki ('grafana/loki:latest' under profile 'core-telemetry'), and Grafana OSS ('grafana/grafana:latest' under profile 'visualization'). Apply the exact cross-profile 'depends_on' health boundaries here.

- PATH: ./observability/config/config.alloy
  A complete HCL-based pipeline. Alloy must pull host system telemetry (CPU/Memory via native unix components) on a 10s loop and tail host system logs. It must stream metrics to Mimir and logs to Loki, using explicit prefix-labels (e.g., cluster_tenant='spark_dgx_core') attached to every data point to preserve multi-tenant indexing metadata.

- PATH: ./observability/config/mimir-config.yaml & loki-config.yaml
  Write the unified configurations forcing both engines to run in single-binary mode. They must use S3-compliant configurations to push blocks directly into their isolated, prefixed MinIO buckets ('tenant-shared-mimir-metrics' and 'tenant-shared-loki-logs').

5. POST-DEPLOYMENT HOOK-UP & PROFILE EXECUTION INSTRUCTIONS
   Provide the terminal commands to initialize the stack using profile flags from the repository root directory (e.g., targeted booting of storage only, vs launching the entire architecture simultaneously). Provide step-by-step instructions for logging into the Grafana UI on port 3000 to link Mimir and Loki as native data sources."
