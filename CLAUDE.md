# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`.init` is a modular Docker Compose platform for local AI inference and observability on NVIDIA DGX/Spark hardware. It brings together data storage (PostgreSQL), full-stack observability (Grafana/Mimir/Loki/Alloy/DCGM), and OpenAI-compatible AI inference (LiteLLM + llama.cpp) — all composable via Docker Compose profiles.

## Model Fleet

The platform routes through four models with different capabilities, costs, and constraints.
Gateway model discovery maps aliases to actual models via `ANTHROPIC_DEFAULT_*_MODEL` env vars
set by `claude-code.sh`:

| Alias | Agent Model | Actual Model | Host | Cost | Concurrency | Best For |
|-------|------------|-------------|------|------|-------------|----------|
| **.INIT/Ultra** | `opus` | DeepSeek-V4-Pro | External | $$$$ | Many parallel | Architecture, planning, complex reasoning |
| **.INIT/Pro** | `sonnet` | DGX/Qwen3.6-27B | Local (port 8000) | Free | **1 only** | Bounded implementation, precise code writing |
| **.INIT/Flash** | `haiku` | DeepSeek-V4-Flash | External | $ | Many parallel | Discovery, searching, broad scanning, web research |
| **.INIT/Air** | `.INIT/Air` | DGX/Qwen3.6-35B-A3B | Local (port 8001) | Free | **1 only** | Mechanical scanning, large-file reading (256K ctx), pattern matching |

### ⚠️ Critical: Local Model Concurrency

**Pro and AIR each run on a llama.cpp backend that handles exactly ONE request at a time.**
This is the single most important constraint for this project:

- ❌ **Never** spawn two Pro agents simultaneously — they share port 8000
- ❌ **Never** spawn two AIR agents simultaneously — they share port 8001
- ✅ Pro (port 8000) and AIR (port 8001) CAN run simultaneously — different backends
- ✅ Flash and Ultra CAN run in parallel with anything — external APIs handle concurrency
- ✅ `pipeline()` with a single Pro/AIR stage serializes automatically

## Agent Execution Architecture

Every non-trivial task follows a **cost-aware, model-optimized** execution pattern.
Choose the architectural pattern based on task complexity:

### Tier Model

| Tier | Model | Role |
|------|-------|------|
| **Orchestrator** | Flash (haiku) | Parse intent, discover files, communicate results, spawn agents/workflows |
| **Planner** | Ultra (opus) | Architecture decisions, complex reasoning, workflow design |
| **Implementer** | Pro (sonnet) | Code generation, refactoring, precise file edits |
| **Scanner** | AIR (.INIT/Air) | Bulk file reading, pattern matching, cross-reference sweeps |
| **Reviewer** | Flash or Pro | Broad scanning (Flash) or deep verification (Pro) |

### Decision Tree — How to Route Work

```
Task received
│
├─ TRIVIAL? (typo, single-line fix, rename, simple question)
│  → Handle inline. No agents needed. Flash orchestrator does it directly.
│
├─ SIMPLE? (1-2 files, well-defined change, no discovery needed)
│  → Spawn 1 Pro agent (worker-pro). Bounded, isolated, free.
│
├─ DISCOVERY-HEAVY? (need to find files, understand patterns)
│  → Light workflow:
│     Phase 1: 2-4 Flash agents scan in parallel (cheap, fast)
│     Phase 2: 1-2 Pro agents implement per finding (pipeline, serialized)
│
├─ MULTI-FILE? (3+ files, dependencies, architectural impact)
│  → Full workflow:
│     Phase 1: Flash agents discover (parallel)
│     Phase 2: Ultra plans architecture (workflow-designer)
│     Phase 3: Pro agents implement (pipeline — serialized)
│     Phase 4: Flash agents review (parallel, adversarial)
│
├─ AUDIT / SWEEP? (codebase-wide, security, quality)
│  → Sweep workflow:
│     Phase 1: Flash + AIR scan dimensions (parallel)
│     Phase 2: Deduplicate findings (inline in script)
│     Phase 3: Pro verifies each finding (pipeline — serialized)
│     Phase 4: Flash synthesizes report
│
├─ RESEARCH? (multi-source, before any code)
│  → Research workflow:
│     Phase 1: Flash agents research multiple angles (parallel, WebSearch)
│     Phase 2: Ultra synthesizes findings
│
└─ MIGRATION? (many files, pattern-based mechanical changes)
   → Pipeline workflow:
      Phase 1: AIR discovers all sites (1 agent, 256K context)
      Phase 2: Pro implements per file (pipeline — serialized)
      Phase 3: Flash reviews all changes (parallel)
```

### Cost Optimization Rules

| Rule | Rationale |
|------|-----------|
| Discovery **always** Flash | 12x cheaper than Ultra, faster, parallel-capable |
| Implementation **always** Pro | Free (local GPU), and bounded implementation is its strength |
| Architecture/planning **always** Ultra | Only model smart enough for complex multi-file planning |
| Mechanical scanning **always** AIR | Free, 256K context, good enough for grep/find-like work |
| Review **Flash-first** | Broad scan cheaply; Pro for deep verification of specific findings |
| Serialize Pro & AIR | Local models reject concurrent requests |
| Batch external models | Flash and Ultra agents run freely in parallel |

### Subagent Reference

| Subagent | Model | Tools | When to Use |
|----------|-------|-------|-------------|
| `worker-explore` | Flash (haiku) | Glob, Grep, LS, Read, Bash, WebFetch, WebSearch | Codebase search, context gathering, file discovery |
| `worker-pro` | Pro (sonnet) | * (all) | Bounded implementation: coding, refactoring, script writing. **Serialize.** |
| `worker-air` | AIR (.INIT/Air) | Read, Glob, Grep, LS, Bash, WebFetch | Mechanical scanning, large-file reading, pattern matching. **Serialize.** |
| `workflow-designer` | Ultra (opus) | Read, Glob, Grep, LS, Bash, WebFetch, WebSearch | Design optimal workflow scripts for complex multi-agent tasks |
| `reviewer` | Flash (haiku) | Read, Glob, Grep, LS, Bash, WebFetch, WebSearch | General code review — broad scanning (Flash) or deep verification (override to Pro) |
| `infra-reviewer` | Pro (sonnet) | * (all) | Docker Compose, configs, GPU setup review |
| `security-reviewer` | Pro (sonnet) | * (all) | Secrets, network exposure, container security review |
| `docs-reviewer` | Flash (haiku) | Read, Glob, Grep, LS, Bash, WebFetch | Documentation accuracy and consistency review |

### Agent Serialization in Workflows

When writing workflow scripts, follow these serialization rules:

```js
// ✅ CORRECT: Pro agents serialized via pipeline()
pipeline(
  implementationTasks,
  task => agent(task.prompt, {model: 'sonnet', phase: 'Implement'})
)

// ✅ CORRECT: AIR agents serialized via pipeline()
pipeline(
  scanTasks,
  task => agent(task.prompt, {model: '.INIT/Air', phase: 'Scan'})
)

// ✅ CORRECT: Flash agents in parallel (external API)
const results = await parallel([
  () => agent('Scan auth', {model: 'haiku', phase: 'Discover'}),
  () => agent('Scan routes', {model: 'haiku', phase: 'Discover'}),
  () => agent('Scan configs', {model: 'haiku', phase: 'Discover'}),
])

// ✅ CORRECT: Pro + AIR concurrently (different backends)
const [proResult, airResult] = await parallel([
  () => agent('Implement X', {model: 'sonnet', phase: 'Implement'}),
  () => agent('Scan configs', {model: '.INIT/Air', phase: 'Scan'}),
])

// ❌ WRONG: Two Pro agents in parallel (same backend, will fail)
const results = await parallel([
  () => agent('Implement X', {model: 'sonnet'}),
  () => agent('Implement Y', {model: 'sonnet'}),
])
```

### Delegation Protocol

For inline agent spawning (not workflow scripts):

1. **Analyze** with Flash — discover files, understand scope
2. **Specify** a `<task_specification>` with exact requirements
3. **Delegate** to the right model:
   - Simple bounded change → 1 Pro agent
   - Complex multi-file → spawn workflow-designer first, then execute its plan
4. **Verify** with Flash reviewer after each change
5. **Synthesize** and communicate to user

### What Loads Where

- **CLAUDE.md** → loaded by orchestrator AND all subagents
- **Memory files** → loaded at session start for pattern reinforcement
- **Subagent prompts** → loaded when that subagent is spawned
- **Workflow scripts** → in `.claude/workflows/` (project) or `~/.claude/workflows/` (user)

## Big-Picture Architecture

Three layers, each independently composable through `COMPOSE_PROFILES`. Every service
also has its own unique profile for fine-grained control:

| Layer             | Directory        | Services                                    | Stack Profiles                 | Unique Profiles |
| ----------------- | ---------------- | ------------------------------------------- | ------------------------------ | --------------- |
| **Data**          | `data/`          | PostgreSQL                                  | `data`                         | `postgres`      |
| **Observability** | `observability/` | Mimir, Loki, Alloy, Grafana, DCGM, cAdvisor | `obs`                          | `mimir`, `loki`, `alloy`, `grafana`, `gpu-telemetry`, `cadvisor` |
| **Interfaces**    | `interfaces/`    | LiteLLM proxy, llama.cpp backend            | `interface`                    | `litellm`, `llama-qwen-3-6-27b`, `llama-qwen-3-6-35b-a3b` |
| **Network**       | `network/`       | Cloudflare Tunnel                           | —                              | `cloudflared`  |

Data flow: clients → LiteLLM proxy (`:4000`) → llama.cpp (`:8000`) → GPU. Alloy scrapes all services and streams to Mimir/Loki for Grafana visualization. All services share the `init_default` Docker network.

### Compose Structure

- Root `docker-compose.yml` includes all sub-compose files via `include:`
- Each layer has its own compose file: `data/docker-compose.data.yml`, `observability/docker-compose.obs.yml`, `interfaces/docker-compose.interface.yml`
- `network/docker-compose.yaml` defines the shared external network
- `.env` is the switchboard — `COMPOSE_PROFILES` controls which services start

### Key Dependencies

- `interface` requires `data` (Postgres for LiteLLM)
- `obs` requires `data` (Postgres for Grafana)
- `llama-qwen-3-6-27b` is independent of `obs`
- `third-party/llama.cpp/` is a git submodule providing the inference backend

## Working with the Stack

### Start/Stop

```bash
# Full stack (all layers + both llama.cpp backends)
# Secrets come from ~/.bashrc (exported env vars); .env provides paths/profiles
docker compose --env-file .env up -d

# Check status
docker compose ps

# Stop everything
docker compose down
```

### Profile Selection

Each service has a unique profile. Stack profiles (`data`, `obs`, `interface`) activate
all services in a layer. Use `all` to start everything.

Edit `COMPOSE_PROFILES` in `.env`, then run `docker compose --env-file .env up -d`. Common shapes:

```
# Full stack (all layers + both llama.cpp backends)
COMPOSE_PROFILES=data,obs,interface

# Everything (shorthand)
COMPOSE_PROFILES=all

# Data + observability only
COMPOSE_PROFILES=data,obs

# LiteLLM + 27B only (no observability)
COMPOSE_PROFILES=data,litellm,llama-qwen-3-6-27b

# API proxy only (cloud models, no local llama.cpp)
COMPOSE_PROFILES=data,litellm

# Just a single service (e.g., PostgreSQL only)
COMPOSE_PROFILES=postgres
```

### Endpoints

| Service       | URL                        | Auth                                          |
| ------------- | -------------------------- | --------------------------------------------- |
| LiteLLM proxy | `http://localhost:4000`    | `LITELLM_MASTER_KEY`                          |
| llama.cpp     | `http://localhost:8000/v1` | None                                          |
| Grafana       | `http://<host>:3000`       | `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD` |

### Environment

First-time setup — copy the template and initialize submodules:

```bash
cp .env.example .env                      # edit with your paths and hostname
git submodule update --init --recursive    # pulls llama.cpp + model weights
```

Secrets (API keys, passwords) are stored in a separate `.env.secrets` file at an
external location and sourced via `~/.bashrc`:

```bash
# In ~/.bashrc:
export $(grep -v '^#' /path/to/.env.secrets | xargs)
```

`.env.secrets.example` is tracked in git as a template — copy it to your secrets
location and fill in values. Never commit `.env.secrets`.

Then start with:

```bash
docker compose --env-file .env up -d
```

Critical settings:

- `LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH` — must point to a valid GGUF model file on disk (set in `.env`)
- `LITELLM_MASTER_KEY` — auth key for the proxy (set in `.env.secrets`, loaded via `~/.bashrc`)

### Secret Protection

A unified Trivy-based system with two layers of scanning and one CI pipeline:

| Touchpoint | What it does |
|------------|-------------|
| **Per-write hook** | `trivy-scan.sh` — scans every written file immediately (default mode) |
| **End-of-session sweep** | `trivy-scan.sh MODE=end-of-session` — scans all `git diff --name-only` changed files |
| **CI workflow** | `.github/workflows/trivy.yml` — full repo scan on push/PR + daily |

The config files that drive these scans:

- `trivy.yaml` — config: scanners, severity, paths
- `trivy-secret.yaml` — rules: custom regex patterns

**Working with secrets:**

- **Always** use `.env.example` for `.env` template changes (never edit `.env`-checked-in)
- `.env.secrets` is stored **externally** — loaded by `~/.bashrc`, never in the repo
- **Never** hardcode a secret in source code — reference it via an environment variable
- **At session end**, run `! .claude/hooks/compare-env.sh` to check if `.env` needs updating
- **Secret values** can only be checked by the user directly (`grep VAR /path/to/.env.secrets`)
- **False positives** → add allow-rules to `trivy-secret.yaml`

## Linting & CI

No test suite — this is an infrastructure repository. CI runs three lint jobs:

```bash
# YAML lint (docker-compose files + configs)
pip install yamllint
yamllint -d "{extends: default, rules: {line-length: disable, truthy: disable}}" \
  $(find . -name 'docker-compose*.yml' -o -name '*.yaml' -path '*/config/*')

# Shell lint
shellcheck scripts/*.sh data/config/postgres-init/*.sh

# Python syntax check
find scripts/ -name '*.py' -print0 | xargs -0 -I{} python3 -m py_compile {}
```

The `scripts/` directory is currently empty, so the ShellCheck and Python jobs are no-ops. If scripts are re-added, those checks resume coverage automatically.

GitHub Actions (`.github/workflows/`):

- `lint.yml` — YAML, ShellCheck, Python syntax on push/PR to main
- `trivy.yml` — Full repo secret + misconfig scan on push/PR + daily schedule
- `docker-build-llama-cpp-dgx.yml` — Build and push `llama-cpp-dgx` image to GHCR on push to main/tags
- `docker-build-claude-code.yml` — Build and push `claude-code` image to GHCR on push to main/tags
- `deploy-docs.yml` — Deploy MkDocs site

## Building Docker Images

```bash
# llama-cpp-dgx
docker build -t ghcr.io/nilayparikh/llama-cpp-dgx:cuda13.1.2-b9222 \
  -f docker/llama-cpp-dgx/Dockerfile .

# claude-code
docker build -t ghcr.io/nilayparikh/claude-code:v0.0.1 \
  -f docker/claude-code/Dockerfile docker/claude-code/
```

Each image is also built by CI when its `docker/<image>/` directory changes.

## `claude-code.sh`

Launches an isolated Claude Code container (NVIDIA PyTorch base) routed through the local LiteLLM proxy. It:

1. Reads `.env` for model routing; auth tokens come from environment (exported by `~/.bashrc`)
2. Builds the container image from `docker/claude-code/Dockerfile` if not cached
3. Runs Claude Code with `ANTHROPIC_BASE_URL` pointing to the LiteLLM proxy at `http://barsana.local:4000`

The image uses `.INIT/Pro`, `.INIT/Flash`, `.INIT/Ultra` model aliases mapped to the LiteLLM backends (see `claude-code.sh` for the full routing table).

## File Map (for AI Agents)

This indexed catalog covers all source files, configuration, and documentation. Use it to locate any file without searching.

### Root-Level

| File | Purpose |
| -------------------- | --------------------------------------------------------- |
| `docker-compose.yml` | Root compose — includes all sub-compose files via `include:` |
| `.env.example` | All configurable variables with defaults and descriptions |
| `claude-code.sh` | Launch Claude Code container routed through LiteLLM proxy |
| `mkdocs.yml` | MkDocs site configuration (Material theme) |
| `CLAUDE.md` | This file — guidance for AI agents |
| `.env.secrets.example` | Secret variables template (API keys, passwords) |
| `.claude/hooks/` | Trivy-based security scanning + env comparison hooks |
| `trivy.yaml` | Trivy scan strategy reference |
| `trivy-secret.yaml` | Custom Trivy secret rules (OpenAI keys, DB strings) |
| `CHANGELOG.md` / `CONTRIBUTING.md` / `SECURITY.md` / `CODE_OF_CONDUCT.md` | Standard community health files |
| `third-party/README.md` | Third-party dependency and submodule notes |

### Data Layer (`data/`)

| File | Purpose |
| ---------------------------------------------------- | --------------------------------------------------------- |
| `data/docker-compose.data.yml` | PostgreSQL service definition with health check |
| `data/config/postgres-init/010-grafana.sh` | Creates Grafana database + user on first start |
| `data/config/postgres-init/020-litellm-interface.sh` | Creates LiteLLM database + user on first start |

### Interfaces Layer (`interfaces/`)

| File | Purpose |
| -------------------------------------------------------- | --------------------------------------------------------- |
| `interfaces/docker-compose.interface.yml` | LiteLLM proxy + llama.cpp service definitions (all flags documented inline) |
| `interfaces/README.md` | Interfaces layer overview — architecture and design decisions |
| `interfaces/config/litellm/config.yaml` | LiteLLM routing: provider includes, model_group_alias, retry policy |
| `interfaces/config/litellm/providers/dgx-spark.yaml` | Local DGX model routing (27B + 35B A3B) |
| `interfaces/config/litellm/providers/azure-foundry.yaml` | Azure Foundry cloud models |
| `interfaces/config/litellm/providers/deepseek.yaml` | DeepSeek native API |
| `interfaces/config/litellm/providers/nvidia.yaml` | NVIDIA AI Endpoints |
| `interfaces/config/litellm/providers/opencode-zen.yaml` | OpenCode Zen models |
| `interfaces/config/qwen3.6/chat_template.jinja` | Jinja2 chat template for Qwen 3.6 (reasoning format) |

### Docker Layer (`docker/`)

| File | Purpose |
| ---------------------------------------------------- | --------------------------------------------------------- |
| `docker/llama-cpp-dgx/Dockerfile` | llama.cpp CUDA Docker image (aarch64, CUDA 13.1.2) |
| `docker/claude-code/Dockerfile` | Claude Code dev container (NVIDIA PyTorch, aarch64) |
| `docker/README.md` | Build instructions and OCI label reference |

### Observability Layer (`observability/`)

| File | Purpose |
| -------------------------------------------- | --------------------------------------------------------- |
| `observability/docker-compose.obs.yml` | Mimir, Loki, Alloy, cAdvisor, DCGM, Grafana service definitions |
| `observability/config/config.alloy` | Grafana Alloy pipeline — scrape configs + label conventions (all inline) |
| `observability/config/loki-config.yaml` | Loki single-binary storage config |
| `observability/config/mimir-config.yaml` | Mimir single-binary storage config |
| `observability/config/grafana/provisioning/datasources/` | Mimir + Loki data source definitions |
| `observability/config/grafana/provisioning/dashboards/machine/` | JSON dashboard definitions |
| `observability/config/grafana/provisioning/alerting/machine-alerts.yaml` | Alert rules (GPU thermal, filesystem, host saturation) |

### Network (`network/`)

| File | Purpose |
| ----------------------------- | --------------------------------------------------------- |
| `network/docker-compose.yaml` | Cloudflare Tunnel service for external access |

### Scripts (`scripts/`)

| File | Purpose |
| ---- | ------- |
| *(empty)* | All scripts were removed. ShellCheck/Python CI jobs are no-ops until scripts are re-added. |

### Documentation (`docs/`)

| File | Purpose (Human-First) |
| --------------------------------------------------------- | --------------------------------------------------------- |
| `docs/index.md` | Project overview and quick start |
| `docs/quickstart.md` | 5-minute getting-started guide |
| `docs/capabilities.md` | Feature-driven capability reference |
| `docs/label-management.md` | Service label conventions and management |
| `docs/architecture.md` | High-level architecture (one diagram, three layers) |
| `docs/configuration.md` | How-to configure (profiles, .env) |
| `docs/guides.md` | Task-oriented recipes (add model, GPU tuning, troubleshooting) |
| `docs/reference.md` | Quick-lookup tables (models, ports, scripts) |

### GitHub CI (`.github/workflows/`)

| File | Purpose |
| --------------------------------------------------------- | --------------------------------------------------------- |
| `.github/workflows/lint.yml` | YAML lint, ShellCheck, Python syntax on push/PR |
| `.github/workflows/trivy.yml` | Full repo secret + misconfig scan on push/PR + daily |
| `.github/workflows/docker-build-llama-cpp-dgx.yml` | Build `llama-cpp-dgx` image and push to GHCR |
| `.github/workflows/docker-build-claude-code.yml` | Build `claude-code` image and push to GHCR |
| `.github/workflows/deploy-docs.yml` | Deploy MkDocs site to GitHub Pages |

## Submodules

- `third-party/llama.cpp/` — inference backend (ggml-org/llama.cpp)
- `models/qwen3.6-27b-text-nvfp4-mtp/` — Qwen 3.6 27B GGUF model weights
- `models/qwen3.6-35b-a3b-nvfp4-mtp/` — Qwen 3.6 35B A3B GGUF model weights

All initialized via `git submodule update --init --recursive`.
