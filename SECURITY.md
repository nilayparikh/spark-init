# Security Policy

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in `.init`, please report it responsibly using one of the methods below.

### How to Report

**Option 1: GitHub Private Vulnerability Reporting (Preferred)**
Use GitHub's private vulnerability reporting feature:

1. Go to the repository **Security** tab
2. Click **Report a vulnerability**
3. Follow the prompts to submit your report privately

**Option 2: Email**
Send an email to `security@[your-domain].com` with the details of the vulnerability.

### Response Timeline

We aim to acknowledge reports within **48 hours**. We will keep you informed of our progress and may ask for additional information.

### What to Include in Your Report

Please include as much of the following information as possible:

- **Description:** A clear description of the vulnerability
- **Steps to reproduce:** Detailed steps to reproduce the issue
- **Impact assessment:** What is the potential impact if exploited
- **Environment:** Docker version, NVIDIA driver version, OS details
- **Suggested fix** (if you have one)

## Scope

### In Scope

Vulnerabilities in `.init` project code and configurations:

- Docker Compose configuration files (`docker-compose.yml`, `docker-compose.data.yml`, `docker-compose.obs.yml`, `docker-compose.interface.yml`)
- Build scripts and Dockerfiles
- LiteLLM configuration templates
- Observability exporter configurations
- Initialization scripts
- Custom Python/Shell scripts in the repository

### Out of Scope

The following are **not** in scope for `.init` security reports, as they are maintained by third-party vendors:

- **NVIDIA CUDA base images** — Report to NVIDIA via their [security program](https://www.nvidia.com/en-us/security/)
- **Grafana OSS images** (Alloy, Mimir, Loki) — Report to Grafana Labs
- **PostgreSQL upstream images** — Report to the PostgreSQL project
- **LiteLLM application code** (upstream bugs) — Report to BerriAI
- **llama.cpp upstream code** — Report to ggml-org
- Model weights or model-specific vulnerabilities

## Security Best Practices for Users

When deploying `.init` in production:

1. Never commit `.env` files containing secrets
2. Use Docker secrets or a vault solution for sensitive configuration
3. Keep Docker images updated to their latest patched versions
4. Restrict network access to exposed ports
5. Review the `docker-compose.yml` files for any services that expose ports to `0.0.0.0`
