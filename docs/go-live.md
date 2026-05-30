# Go-Live Plan: Open Source Release

This document tracks all tasks required to finalize the `.init` stack repository for open-source release.

---

## Project Summary

The `.init` stack is a modular, profile-driven Docker Compose platform for local AI inference and observability on NVIDIA DGX/Spark hardware. It composes three layers:

- **Data**: shared PostgreSQL with multi-tenant bootstrap scripts
- **Observability**: Grafana Alloy, Mimir, Loki, cAdvisor, DCGM exporter, and Grafana dashboards
- **Interfaces**: LiteLLM proxy with llama.cpp backend (Standard Qwen 3.6 27B / Lite)

---

## Workstreams

### WS1: Legal & Governance Files (Critical Path)

| #   | Task                                 | Status | Details                                                                                                                                                           |
| --- | ------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1 | Create `LICENSE` (Apache 2.0)        | ✅     | Required — without a license, the code is all-rights-reserved by default. Apache 2.0 chosen for explicit patent grant (critical for AI/ML infrastructure).        |
| 1.2 | Create `NOTICE` file                 | ✅     | Required by Apache 2.0 — lists third-party dependencies and their licenses (llama.cpp MIT, LiteLLM MIT, CUDA EULA notice, Grafana AGPL/LGPL, PostgreSQL license). |
| 1.3 | Create `CONTRIBUTING.md`             | ✅     | PR process, coding standards, testing requirements, dev environment setup.                                                                                        |
| 1.4 | Create `CODE_OF_CONDUCT.md`          | ✅     | Contributor Covenant v2.1 (widely adopted standard).                                                                                                              |
| 1.5 | Create `SECURITY.md`                 | ✅     | Vulnerability disclosure policy — private email/form for reports, 48hr acknowledgment SLA, scope definition.                                                      |
| 1.6 | Verify third-party LICENSE retention | ✅     | Ensure `third-party/llama.cpp/LICENSE` is present and all vendored components retain original license files.                                                      |

### WS2: Documentation Restructure & GitHub Pages

| #    | Task                                                         | Status                                                                                                           | Details                                                                                                                                                                                                    |
| ---- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2.1  | Create top-level `docs/` structure with MkDocs Material site | ✅                                                                                                                | Move from scattered subdirectory docs to unified `docs/` with `mkdocs.yml`. Current docs are in `interfaces/docs/`, `observability/docs/`, and `data/docs/` — consolidate into a coherent navigation tree. |
| 2.2  | Write `docs/index.md` (site home)                            | ✅                                                                                                                | Project overview, quick start, feature highlights, architecture diagram link.                                                                                                                              |
| 2.3  | Write `docs/getting-started/quickstart.md`                   | ✅                                                                                                                | 5-minute Docker Compose spin-up guide with copy-paste commands. Prerequisites (NVIDIA GPU, Docker, nvidia-container-toolkit).                                                                              |
| 2.4  | Write `docs/getting-started/prerequisites.md`                | ✅                                                                                                                | System requirements: Ubuntu 24.04 ARM64, CUDA 13.x, NVIDIA driver ≥570, Docker ≥27.x.                                                                                                                      |
| 2.5  | Write `docs/architecture/overview.md`                        | ✅                                                                                                                | High-level component diagram (Mermaid), data flow between layers, profile selection logic. Expand from existing `observability/docs/architecture.md`.                                                      |
| 2.6  | Write `docs/configuration/docker-compose.md`                 | ✅                                                                                                                | Compose file reference — all profiles, services, ports, and volume mounts.                                                                                                                                 |
| 2.7  | Write `docs/configuration/environment-variables.md`          | ✅                                                                                                                | Consolidate from `interfaces/docs/env-reference.md`, `data/docs/env-reference.md`. Full env var catalog grouped by component.                                                                              |
| 2.8  | Write `docs/guides/adding-models.md`                         | ✅                                                                                                                | How to add new GGUF models, convert with llama.cpp tools, wire into LiteLLM config.                                                                                                                        |
| 2.9  | Write `docs/guides/observability-setup.md`                   | ✅                                                                                                                | Wiring metrics/logs/traces — Alloy config, Grafana provisioning, dashboard standards. Expand from existing observability docs.                                                                             |
| 2.10 | Write `docs/guides/gpu-configuration.md`                     | ✅                                                                                                                | GPU passthrough, persistent settings (from `scripts/gpu-persistent-setting.sh`), DCGM setup.                                                                                                               |
| 2.11 | Write `docs/guides/troubleshooting.md`                       | ✅ Common issues: CUDA stub linking, model loading failures, port conflicts, LiteLLM auth issues.                 |
| 2.12 | Write `docs/api/openai-compatible.md`                        | ✅                                                                                                                | Inference API reference — OpenAI-compatible endpoints at localhost:4000 and localhost:8000. Model naming conventions.                                                                                      |
| 2.13 | Write `docs/reference/file-index.md`                         | ✅                                                                                                                | Consolidate from existing `interfaces/docs/file-index.md` and `data/docs/file-index.md`. Master file catalog for the entire project.                                                                       |
| 2.14 | Create `.github/workflows/deploy-docs.yml`                   | ✅ MkDocs → GitHub Pages deployment workflow. Triggers on pushes to main branch, paths: docs/\*\* and mkdocs.yml. |
| 2.15 | Create `mkdocs.yml` config file at project root              | ✅ Material theme, navigation tree, search plugin, social cards config.                                           |

### WS3: README.md Enhancement

| #   | Task                                                                                                                     | Status                                                                                                                 | Details |
| --- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | ------- |
| 3.1 | Add badge row to README.md                                                                                               | ✅ Build status (GitHub Actions), license badge (Apache 2.0), Docker image tags, Python version if applicable.          |
| 3.2 | Add one-line tagline and project description                                                                             | ✅ Clear elevator pitch: "Modular Docker Compose platform for local AI inference and observability on NVIDIA hardware." |
| 3.3 | Add feature highlights section with links to docs/ ✅ Bullet list of key capabilities with hyperlinks to the MkDocs site. |
| 3.4 | Add architecture diagram (Mermaid) or link to docs/architecture/overview.md                                              | ✅ Visual overview of the three-layer stack.                                                                            |
| 3.5 | Add "Contributing" section with link to CONTRIBUTING.md                                                                  | ✅ Invitation for community contributions, code of conduct reference.                                                   |
| 3.6 | Add license declaration at bottom of README.md                                                                           | ✅ Standard Apache 2.0 footer with copyright year and holder.                                                           |

### WS4: GitHub Actions Workflows

| #   | Task                                                                                                                                                                      | Status                                                                                                                                                       | Details |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| 4.1 | Create `.github/workflows/deploy-docs.yml` (also in WS2) ✅ MkDocs → GitHub Pages deployment workflow. Triggers on pushes to main branch, paths: docs/\*\* and mkdocs.yml. |
| 4.2 | Create `.github/workflows/docker-build.yml`                                                                                                                               | ✅ Multi-arch Docker image build for llama.cpp runtime (ARM64). Build on push to main and on tags. Push to GitHub Container Registry (ghcr.io) or Docker Hub. |
| 4.3 | Create `.github/workflows/lint.yml`                                                                                                                                       | ✅ YAML linting for docker-compose files, shellcheck for scripts, basic Python linting.                                                                       |
| 4.4 | Create `.github/ISSUE_TEMPLATE/bug-report.yml`                                                                                                                            | ✅ Structured bug report form: environment, GPU model, Docker version, steps to reproduce.                                                                    |
| 4.5 | Create `.github/ISSUE_TEMPLATE/feature-request.yml`                                                                                                                       | ✅ Structured feature request form: description, use case, alternatives considered.                                                                           |
| 4.6 | Create `.github/PULL_REQUEST_TEMPLATE.md`                                                                                                                                 | ✅ PR template: description, related issues, testing performed, docs updated checkbox.                                                                        |
| 4.7 | Create `.github/FUNDING.yml` (optional)                                                                                                                                   | ☐ If applicable — GitHub Sponsors or Open Collective link. (Optional, skipped.)                                                                                                   |

### WS5: Project Hygiene & .gitignore

| #   | Task                                                                           | Status                                                                                                                                                        | Details |
| --- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| 5.1 | Enhance `.gitignore` for open-source readiness                                 | ✅ Add: `.cache/`, `.venv/`, `*.egg-info/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/` (some already present). Add model weight patterns, build outputs. |
| 5.2 | Create `.editorconfig`                                                         | ✅ Consistent coding styles across editors: 2-space indent for YAML/JSON, UTF-8 encoding, trailing whitespace cleanup.                                         |
| 5.3 | Clean up `scripts/cmds.txxt` (typo in filename)                                | ✅ Renamed to `scripts/cmds.txt`.                                                                                                                             |
| 5.4 | Remove `.cache/`, `.venv/`, `.mypy_cache/`, `.pytest_cache/` from git tracking | ✅ These directories are not committed.                                                                                                                       |
| 5.5 | Create `CHANGELOG.md`                                                          | ✅ Initial v1.0.0 release notes documenting the open-source launch, features, and known limitations.                                                           |
| 5.6 | Create `.github/CODEOWNERS` (optional)                                         | ✅ Define review ownership for key directories (docs/, interfaces/, observability/).                                                                           |

---

## Execution Order

```
Phase 1 (Blocking): WS1 — Legal & Governance
  └── Cannot publish without LICENSE file.

Phase 2 (Parallel): WS2, WS3, WS4, WS5
  ├── All can proceed once LICENSE exists.
  ├── WS2 and WS3 share context (README links to docs/).
  └── WS4 workflows reference files from all other workstreams.

Phase 3 (Final): Integration review
  └── Verify all cross-references, badges, and links work.
```

---

## Open Source Readiness Checklist

| Criteria                                                           | Status            |
| ------------------------------------------------------------------ | ----------------- |
| License file present and valid                                     | ✅                |
| README.md has project overview + quick start                       | ✅                |
| CONTRIBUTING.md exists with clear process                          | ✅                |
| CODE_OF_CONDUCT.md exists                                          | ✅                |
| SECURITY.md with vulnerability reporting policy                    | ✅                |
| NOTICE file with third-party attributions (Apache 2.0 requirement) | ✅                |
| .gitignore excludes secrets, build artifacts, model weights        | ✅                |
| GitHub Pages docs site deployed and accessible                     | ☐ (workflow ready, needs first deploy) |
| GitHub Actions CI workflows configured                             | ✅                |
| Issue templates for bug reports and feature requests               | ✅                |
| PR template with contribution guidelines reference                 | ✅                |
| CHANGELOG.md with initial release notes                            | ✅                |
| All `.env` files excluded from git (only `.env.example` committed) | ✅                |
| No hardcoded secrets in source files                               | ✅ (verified)     |
| Third-party LICENSE files retained in vendor directories           | ✅ (verified)     |

---

## Notes on Licensing Decisions

| Component                          | License                       | Compatibility with Apache 2.0                                                                               |
| ---------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------- |
| llama.cpp (third-party/)           | MIT ✅                        | Fully compatible — permissive, no copyleft. Retain original LICENSE.                                        |
| LiteLLM (Docker image)             | MIT ✅                        | Used as a runtime dependency via Docker image, not vendored source. No license conflict.                    |
| CUDA Toolkit (NVIDIA base images)  | Proprietary (CUDA EULA)       | Not redistributed as source — users pull NVIDIA base images. Document as runtime dependency.                |
| Grafana/Mimir/Loki (Docker images) | AGPL/LGPL                     | Used as runtime dependencies via Docker images, not vendored. No license conflict with our Apache 2.0 code. |
| PostgreSQL (Docker image)          | PostgreSQL License (BSD-like) | Runtime dependency via Docker image. Compatible.                                                            |
| Qwen model weights                 | Model-specific license        | Not redistributed in this repo — users download separately. Document download instructions in docs/.        |

---

## GitHub Pages Site Structure (Planned)

```
docs/
├── index.md                          # Home: project overview + quick start
├── getting-started/
│   ├── quickstart.md                 # 5-minute Docker Compose spin-up
│   └── prerequisites.md              # System requirements (GPU, Docker, etc.)
├── architecture/
│   ├── overview.md                   # High-level component diagram
│   ├── inference-stack.md            # llama.cpp / vLLM layer
│   ├── observability-stack.md        # Grafana, Loki, Mimir, Alloy
│   └── networking.md                 # Docker networks, service discovery
├── configuration/
│   ├── docker-compose.md             # Compose file reference + profiles
│   ├── environment-variables.md      # Full env var catalog
│   └── custom-configs.md             # LiteLLM config, chat templates
├── guides/
│   ├── adding-models.md              # How to add new GGUF models
│   ├── observability-setup.md        # Wiring metrics/logs/traces
│   ├── gpu-configuration.md          # GPU passthrough, DCGM setup
│   └── troubleshooting.md            # Common issues and fixes
├── api/
│   └── openai-compatible.md          # Inference API reference
├── reference/
│   ├── file-index.md                 # Master file catalog
│   └── docker-images.md              # Available images and tags
└── contributing/
    ├── development.md                # Local dev setup
    └── docs-guide.md                 # How to contribute to docs
```
