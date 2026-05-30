---
name: project-goals
description: High-level purpose and design philosophy of the .init platform
metadata:
  type: project
---

## Project Goals

`.init` is a modular, composable local AI inference platform for NVIDIA DGX Spark hardware. It aims to be:

1. **Self-contained** — Everything runs locally via Docker Compose. No cloud dependencies for core inference.
2. **Observable by default** — Every service emits telemetry, visualized in Grafana. Alloy scrapes all endpoints.
3. **Profiles-driven composition** — `COMPOSE_PROFILES` in `.env` selects which layers start. Data, observability, and interfaces are independently composable.
4. **OpenAI-compatible** — LiteLLM proxy exposes a standard `/v1/chat/completions` endpoint. Any OpenAI client works.
5. **Reproducible** — One `docker compose up -d` starts the full stack. `.env.example` documents every variable.

### Design Principles

- Each layer owns its compose file and config — no cross-layer coupling
- Git submodules for weights and inference engine avoid storing binaries in-repo
- `.env` is the single source of truth for routing, secrets, and profiles
- Linting hooks on every edit to enforce YAML/shell/Python quality

### Non-Goals

- Not a production hosting platform — designed for a single DGX Spark
- Not a training infrastructure — inference only
- Not a general-purpose MCP gateway — LiteLLM is specifically for LLM routing
