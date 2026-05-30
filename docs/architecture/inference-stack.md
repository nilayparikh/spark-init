# Inference Stack

The inference layer provides OpenAI-compatible API endpoints powered by llama.cpp as the local backend runtime.

## Architecture

```mermaid
graph LR
    subgraph "User Clients"
        A["VS Code / CLI / Agents"]
    end

    subgraph "LiteLLM Proxy (:4000)"
        B["Authentication & Routing"]
        C["Multi-Provider Config"]
    end

    subgraph "Local Backends"
        D["llama.cpp<br/>Standard (Qwen 3.6 27B)<br/>(:8000)"]
        E["llama.cpp<br/>35B A3B (multimodal)<br/>(:8001)"]
    end

    subgraph "Cloud Providers"
        G["Azure Foundry"]
        H["NVIDIA AI Endpoints"]
        I["DeepSeek"]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    C --> G
    C --> H
```

## Supported Models

The `.init` stack supports two local model backends:

| Model | Description | Format | Profile |
|-------|-------------|--------|---------|
| **Standard** (Qwen 3.6 27B) | Full 27B parameter model with MTP | GGUF (NVFP4) | `llama-qwen-3-6-27b` |
| **35B A3B** (Qwen 3.6 35B A3B) | Multimodal 35B A3B model with MTP and mmproj | GGUF (NVFP4) | `llama-qwen-3-6-35b-a3b` |

> **Note:** Only llama.cpp is supported as the inference backend on DGX Spark hardware due to SM120/SM121 limitations (missing TMEM, unoptimized kernels, MTP shape mismatch).

## llama.cpp Backend

The llama.cpp backend provides CUDA-accelerated inference for GGUF-quantized models.

### Build Configuration

The Dockerfile builds llama.cpp with these key settings:

- **CUDA 13.1.2** — Targets NVIDIA Blackwell/Ada GPUs
- **Architecture 12.1** — Optimized for compute capability
- **Speculative decoding with MTP** — Multi-Token Prediction for faster inference

### Runtime Configuration (27B)

The 27B backend runs with these optimized parameters:

```
--min-p 0.05
-c 131072          # Context window: 128K tokens
-b 2048            # Batch size
--parallel 1      # Parallel requests
--cont-batching
--cache-prompt
--swa-full
-t 8              # Threads
-tb 8             # Threads per batch
--mlock
--port 8080
--host 0.0.0.0
--metrics
--timeout 120
```

### Runtime Configuration (35B A3B)

The 35B A3B backend uses the same parameters as the 27B, with these differences:

```
-c 262144         # Context window: 256K tokens
-mm /models/mmproj.gguf  # Multimodal projector for vision
```

### Speculative Decoding

Both backends use speculative decoding with MTP (Multi-Token Prediction):

```
--spec-type draft-mtp,ngram-mod
--spec-draft-n-max 2
--spec-draft-p-min 0.88
--spec-draft-ngl 99
```

This allows the model to predict multiple tokens per forward pass, significantly improving throughput.

## Model Configuration

### Standard Model (Qwen 3.6 27B)

- **Format**: GGUF with NVFP4 quantization
- **Context window**: 128K tokens
- **MTP**: Multi-Token Prediction enabled for faster inference
- **VRAM requirement**: Scales with NVFP4 quantization profile

### 35B A3B Model (Qwen 3.6 35B A3B)

- **Format**: GGUF with NVFP4 quantization
- **Context window**: 256K tokens
- **Multimodal**: Supports vision via separate mmproj BF16 GGUF file
- **MTP**: Multi-Token Prediction enabled for faster inference

## LiteLLM Proxy

The LiteLLM proxy provides a unified OpenAI-compatible API surface.

### Multi-Provider Routing

```
Azure Foundry → AZURE_ORCHESTRATOR_
NVIDIA AI Endpoints → NVIDIA_
DeepSeek → DEEPSEEK_
Local backends → INTERFACE_
```

### Model Naming Conventions

The proxy publishes models under two naming schemes:

- `openai/<Provider>/...` — Standard OpenAI-compatible naming for IDE clients
- `anthropic/<Provider>/...` — Claude compatibility aliases for Claude Code

Claude compatibility aliases:

- `claude-opus-4.7`
- `claude-sonnet-4.6`
- `claude-haiku-4.6`
- `claude-haiku-4-5-20251001`
- `claude-haiku-4-5`

See [Developer Clients](../interfaces/developer-clients.md) for detailed client configuration.

### Authentication

```
Authorization: Bearer $LITELLM_MASTER_KEY
```

## Profile Mutual Exclusivity

`llama-qwen-3-6-27b` and `llama-qwen-3-6-35b-a3b` use separate host ports (8000 and 8001 respectively) and can run simultaneously. Both require the `interface` profile for the LiteLLM proxy.

```
# Valid combinations
COMPOSE_PROFILES=data,obs,interface,llama-qwen-3-6-27b
COMPOSE_PROFILES=data,obs,interface,llama-qwen-3-6-35b-a3b
COMPOSE_PROFILES=data,obs,interface,llama-qwen-3-6-27b,llama-qwen-3-6-35b-a3b
```

## Chat Template Configuration

Qwen 3.6 models use a custom Jinja chat template mounted into the llama.cpp container:

```
./config/qwen3.6/chat_template.jinja:/workspace/chat_template.jinja:ro
```

The template is loaded with `--jinja --chat-template-file /workspace/chat_template.jinja` and enables proper reasoning format support (`--reasoning on --reasoning-format deepseek`).
