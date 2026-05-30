# OpenAI-Compatible API Reference

The `.init` stack exposes OpenAI-compatible REST endpoints through two layers: the LiteLLM proxy (primary entry point) and the llama.cpp backend (direct access). Both implement the OpenAI chat completions API.

## Endpoints

### LiteLLM Proxy (Recommended)

The LiteLLM proxy is the primary entry point. It handles authentication, routing, and observability.

| Endpoint         | URL                                              | Auth            |
| ---------------- | ------------------------------------------------ | --------------- |
| Chat completions | `POST http://localhost:4000/v1/chat/completions` | Bearer token    |
| List models      | `GET http://localhost:4000/v1/models`            | Bearer token    |
| Metrics          | `GET http://localhost:4000/metrics/`             | None (internal) |

```bash
# Chat completion
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "DGX/Qwen3.6-27B",
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ],
    "temperature": 0.7,
    "max_tokens": 256
  }'

# List available models
curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  http://localhost:4000/v1/models
```

### llama.cpp Direct

The llama.cpp backend is accessible directly, bypassing the proxy. Use this for benchmarking or when you don't need routing.

| Endpoint         | URL                                              | Auth |
| ---------------- | ------------------------------------------------ | ---- |
| Chat completions | `POST http://localhost:8000/v1/chat/completions` | None |
| List models      | `GET http://localhost:8000/v1/models`            | None |
| Metrics          | `GET http://localhost:8000/v1/metrics`           | None |

```bash
# Direct chat completion (no auth)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.6_27b",
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ],
    "temperature": 0.7
  }'
```

## Request Format

### Chat Completions

```json
{
  "model": "DGX/Qwen3.6-27B",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "Explain quantum computing." }
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 2048,
  "stream": false
}
```

| Parameter           | Type    | Default  | Description                                     |
| ------------------- | ------- | -------- | ----------------------------------------------- |
| `model`             | string  | required | Model identifier (see naming conventions below) |
| `messages`          | array   | required | Chat history with `role` and `content`          |
| `temperature`       | float   | 0.8      | Sampling temperature (0–1)                      |
| `top_p`             | float   | 0.95     | Nucleus sampling threshold                      |
| `max_tokens`        | integer | ∞        | Maximum tokens to generate                      |
| `stream`            | boolean | false    | Enable SSE streaming                            |
| `frequency_penalty` | float   | 0        | Penalty for repeated tokens                     |
| `presence_penalty`  | float   | 0        | Penalty for new tokens                          |

### Streaming

Set `"stream": true` to receive Server-Sent Events:

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "DGX/Qwen3.6-27B",
    "messages": [{"role": "user", "content": "Count to 10"}],
    "stream": true
  }'
```

Each chunk is a `data:` line containing a JSON object with a `delta` field:

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","choices":[{"delta":{"content":"One"},"finish_reason":null}]}
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","choices":[{"delta":{"content":"."},"finish_reason":null}]}
...
data: [DONE]
```

## Model Naming Conventions

The gateway publishes models under `<Provider>/<Name>` identifiers and canonical `.INIT/` aliases for Claude Code routing.

### All Available Models

| Model ID | Provider | Type |
|----------|----------|------|
| `DGX/Qwen3.6-27B` | Local llama.cpp (27B) | Chat |
| `DGX/Qwen3.6-35B-A3B` | Local llama.cpp (35B A3B) | Chat |
| `Azure/Kimi-K2.6` | Azure Foundry | Chat |
| `Azure/DeepSeek V4 Flash` | Azure Foundry | Chat |
| `DeepSeek/DeepSeek-V4-Flash` | DeepSeek native | Chat |
| `DeepSeek/DeepSeek-V4-Pro` | DeepSeek native | Chat |
| `NVIDIA/DeepSeek-V4-Flash` | NVIDIA AI Endpoints | Chat |
| `NVIDIA/MiniMax-M2.7` | NVIDIA AI Endpoints | Chat |
| `NVIDIA/Kimi-K2.6` | NVIDIA AI Endpoints | Chat |
| `OpenCodeZen/MIMO-V2.5-FREE` | OpenCode Zen | Chat |
| `OpenCodeZen/NEMOTRON-3-SUPER-FREE` | OpenCode Zen | Chat |
| `OpenCodeZen/DEEPSEEK-V4-FLASH-FREE` | OpenCode Zen | Chat |
| `OpenCodeZen/BIG-PICKLE` | OpenCode Zen | Chat |

### Canonical Aliases (.INIT/)

The proxy publishes model group aliases for Claude Code model selection:

| Alias | Routes To |
|-------|-----------|
| `.INIT/Ultra` | `OpenCodeZen/BIG-PICKLE` |
| `.INIT/Pro` | `DGX/Qwen3.6-27B` |
| `.INIT/Flash` | `DGX/Qwen3.6-35B-A3B` |

Use `/model .INIT/Pro` in Claude Code to select the local 27B backend.

### llama.cpp Direct

Direct access uses the model name as loaded by llama.cpp:

```
qwen3.6_27b
qwen3.6_35b_a3b
```

## Response Format

### Non-Streaming

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "DGX/Qwen3.6-27B",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "2 + 2 equals 4."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 8,
    "total_tokens": 20
  }
}
```

### Error Responses

```json
{
  "object": "error",
  "message": "Invalid API key",
  "type": "invalid_request_error",
  "param": null,
  "code": "invalid_api_key"
}
```

## SDK Compatibility

The OpenAI-compatible endpoints work with standard client libraries:

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key=os.environ["LITELLM_MASTER_KEY"],
)

response = client.chat.completions.create(
    model="DGX/Qwen3.6-27B",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

### cURL (Models List)

```bash
curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  http://localhost:4000/v1/models | python3 -m json.tool
```

## LiteLLM-Specific Features

The proxy adds capabilities beyond the base OpenAI API:

- **Multi-provider routing** — Configure multiple backends in `config.yaml`; LiteLLM routes based on model name
- **Retry policy** — Automatic retries on timeout and rate-limit errors (5 retries by default)
- **Usage logging** — Token usage stored in PostgreSQL for cost tracking
- **Prometheus metrics** — Request counts, latency, and token usage at `/metrics/`

> **★ Insight**
>
> - Always route through LiteLLM (`:4000`) in production — it provides auth, retries, and observability that llama.cpp lacks.
> - Use direct llama.cpp (`:8000`) only for benchmarking or internal tooling where auth overhead is undesirable.
> - LiteLLM translates OpenAI-shaped requests to the upstream backend using the `model` field in `litellm_params`, defined in provider configs under `interfaces/config/litellm/providers/`.
