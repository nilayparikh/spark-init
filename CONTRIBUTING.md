# Contributing to .init

Thank you for your interest in contributing to `.init`! This document outlines the process for contributing to the project.

## Prerequisites

Before you begin, ensure your development environment meets these requirements:

- **Docker** ≥ 27.x (with Compose plugin)
- **NVIDIA GPU** with driver ≥ 570
- **Ubuntu 24.04 ARM64** (primary development platform)
- **nvidia-container-toolkit** installed and configured
- Git

## Development Environment Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/[owner]/init-stack.git
   cd .init
   ```

2. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

3. **Install the NVIDIA Container Toolkit** (if not already installed):
   Follow the [official installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) for your distribution.

## Running the Stack Locally

Start all three layers (data, observability, interfaces):

```bash
docker compose up -d
```

To start individual layers:

```bash
# Data layer only
docker compose -f docker-compose.yml -f data/docker-compose.data.yml up -d

# Observability layer only
docker compose -f docker-compose.yml -f observability/docker-compose.obs.yml up -d

# Interface layer only
docker compose -f docker-compose.yml -f interfaces/docker-compose.interface.yml up -d
```

Check service health:

```bash
docker compose ps
```

## Pull Request Process

1. **Fork** the repository.
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit with descriptive messages.
4. **Push** your branch and open a Pull Request against `main`.
5. Use a **descriptive PR title** that summarizes the change (e.g., "Add Loki log retention configuration" or "Fix health check timeout for LiteLLM interface").
6. **Link related issues** in the PR description using GitHub keywords (`fixes #123`, `refs #456`).

## Coding Standards

- **YAML indentation:** Use 2-space indentation consistently across all `docker-compose` and configuration files.
- **Commit messages:** Write meaningful, imperative commit messages (e.g., "Add Mimir compactor configuration" rather than "updated config").
- **File naming:** Use kebab-case for filenames and directories.
- **Environment variables:** Document all new environment variables in the relevant `docs/env-reference.md`.

## Testing Requirements

Before submitting a Pull Request:

1. **Test locally:** Run your changes with `docker compose up` and verify all services start successfully.
2. **Verify health checks:** Confirm that all service health checks pass and containers report a healthy status.
3. **Test teardown and restart:** Run `docker compose down && docker compose up -d` to ensure clean restarts work correctly.
4. **Validate configuration:** Check that no secrets or sensitive values are committed (use `.env` files, which are gitignored).

## Documentation Updates

**Every feature change must include documentation updates in the same Pull Request.** At minimum:

- Update `docs/file-index.md` if new files or directories are added.
- Update relevant `docs/env-reference.md` for new environment variables.
- Update layer-specific README files (e.g., `observability/docs/README.md`) for architectural changes.
- Update the root `README.md` if user-facing behavior changes.

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

## Questions?

If you have questions or need help, open a GitHub Discussion or Issue in the repository.
