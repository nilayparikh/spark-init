# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-05-28

### Added

- Initial open-source release of the .init stack
- Modular Docker Compose platform for local AI inference and observability
- Three-layer architecture: data (Postgres), observability (Grafana/Mimir/Loki/Alloy), interfaces (LiteLLM + llama.cpp)
- Profile-driven stack composition via COMPOSE_PROFILES
- OpenAI-compatible API proxy with multi-provider routing (Azure Foundry, NVIDIA AI Endpoints, DeepSeek)
- Full observability stack: metrics (Mimir), logs (Loki), traces, GPU telemetry (DCGM exporter)
- Support for Qwen 3.6 models (27B and 35B A3B variants)
- CUDA-accelerated inference on NVIDIA Blackwell/Ada GPUs
- MkDocs Material documentation site
- GitHub Actions CI/CD workflows (lint, Docker build, docs deployment)

### Known Limitations

- Primary platform is Ubuntu 24.04 ARM64 (DGX Spark). x86_64 support is experimental.
- llama.cpp and vLLM 27B profiles are mutually exclusive (both use host port 8000).
- Model weights are not included — users must download separately.
- Requires NVIDIA GPU with compute capability ≥9.0 and minimum 48GB VRAM for 27B models.
