# .init Stack

**AI-augmented software engineering, on your NVIDIA DGX Spark.**

`.init` is a single Docker Compose stack that turns your DGX Spark into a private AI inference server. It gives you local LLMs with an OpenAI-compatible API, full observability, and the option to blend in cloud models — all from one `.env` file.

## What You Get

| You want to... | `.init` gives you... |
|---|---|
| Run local LLMs on your GPU | llama.cpp with Qwen 3.6 models (27B & 35B A3B) behind an OpenAI-compatible proxy on `:4000` |
| See what's happening | Auto-collected GPU metrics, logs, and dashboards in Grafana on `:3000` |
| Mix local + cloud models | LiteLLM proxy routes by model name — local stays free, cloud costs what it costs |
| Use it from any tool | VS Code, Claude Code, cURL, Cline, Continue — anything that speaks OpenAI or Anthropic API |
| Keep your data private | Everything runs locally. No data leaves your machine unless you add a cloud provider. |

## Quick Start

```bash
git clone https://github.com/nilayparikh/init-stack.git
cd init-stack
git submodule update --init --recursive   # pulls llama.cpp + model weights
cp .env.example .env                      # configure your paths & keys
docker compose up -d                      # start everything
```

You're running. Hit `http://localhost:4000/v1/chat/completions` with any OpenAI client.

## A Note on This Documentation

These docs are written for humans who want to understand and use `.init` — not catalog every config file. Technical depth lives inline in the code: compose files, config YAMLs, and scripts are annotated with comments that AI coding agents and operators can rely on.

If you're an AI agent working with this codebase, read `CLAUDE.md` for the complete file map and architectural guidance.
