# OpenAI-Compatible API Reference

The `.init` stack exposes OpenAI-compatible REST endpoints through two layers: the LiteLLM proxy (primary entry point) and the llama.cpp backend (direct access). Both implement the OpenAI chat completions API.

## Endpoints

### LiteLLM Proxy (Recommended)

The LiteLLM proxy is the primary entry point. It handles authentication, routing, and observability.

| Endpoint | URL | Auth |
|----------|-----|------|
| Chat completions | `POST http://localhost:4000/v1/chat/completions` | Bearer token |
| List models | `GET http://localhost:4000/v1/models` | Bearer token |
| Metrics | `GET http://localhost:4000/metrics/` | None (internal) |

```bash
# Chat completion
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "openai/DGX/Qwen3.6 27B/SWE",
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

| Endpoint | URL | Auth |
|----------|-----|------|
| Chat completions | `POST http://localhost:8000/v1/chat/completions` | None |
| List models | `GET http://localhost:8000/v1/models` | None |
| Metrics | `GET http://localhost:8000/v1/metrics` | None |

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
  "model": "openai/DGX/Qwen3.6 27B/SWE",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing."}
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 2048,
  "stream": false
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | required | Model identifier (see naming conventions below) |
| `messages` | array | required | Chat history with `role` and `content` |
| `temperature` | float | 0.8 | Sampling temperature (0–1) |
| `top_p` | float | 0.95 | Nucleus sampling threshold |
| `max_tokens` | integer | ∞ | Maximum tokens to generate |
| `stream` | boolean | false | Enable SSE streaming |
| `frequency_penalty` | float | 0 | Penalty for repeated tokens |
| `presence_penalty` | float | 0 | Penalty for new tokens |

### Streaming

Set `"stream": true` to receive Server-Sent Events:

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "openai/DGX/Qwen3.6 27B/SWE",
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

### OpenAI-Facing (IDE Clients)

For OpenAI-compatible clients (VS Code, Cline, Continue, etc.):

- `openai/DGX/Qwen3.6 27B/SWE` — Qwen 3.6 27B via llama.cpp
- `openai/DGX/Qwen3.6 27B/Writing` — Qwen 3.6 27B Writing variant
- `openai/Azure/Kimi K2.6/Master Orchestrator` — Azure Foundry Kimi K2.6
- `openai/Azure/DeepSeek V4 Flash` — Azure Foundry DeepSeek
- `openai/NVIDIA/Kimi K2.6` — NVIDIA AI Endpoints Kimi K2.6
- `openai/NVIDIA/MiniMax M2.7` — NVIDIA AI Endpoints MiniMax
- `openai/DeepSeek/DeepSeek V4 Flash` — DeepSeek native
- `openai/DeepSeek/DeepSeek V4 Pro` — DeepSeek native

### Anthropic-Facing (Claude Code)

For Claude Code and Anthropic-compatible clients:

- `anthropic/DGX/Qwen3.6 27B/SWE`
- `anthropic/DGX/Qwen3.6 27B/Writing`
- `anthropic/Azure/Kimi K2.6/Master Orchestrator`
- `anthropic/NVIDIA/Kimi K2.6`
- `anthropic/DeepSeek/DeepSeek V4 Pro`
- `claude-opus-4.7`
- `claude-sonnet-4.6`
- `claude-haiku-4.6`
- `claude-haiku-4-5-20251001`
- `claude-haiku-4-5`

See [Developer Clients](../interfaces/developer-clients.md) for detailed client configuration.

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
  "model": "openai/DGX/Qwen3.6 27B/SWE",
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
    model="openai/DGX/Qwen3.6 27B/SWE",
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

- **Multi-provider routing** — Configure multiple backends in `litellm-config.yaml`; LiteLLM routes based on model name
- **Retry policy** — Automatic retries on timeout and rate-limit errors (5 retries by default)
- **Usage logging** — Token usage stored in PostgreSQL for cost tracking
- **Prometheus metrics** — Request counts, latency, and token usage at `/metrics/`

> **★ Insight**
> - Always route through LiteLLM (`:4000`) in production — it provides auth, retries, and observability that llama.cpp lacks.
> - Use direct llama.cpp (`:8000`) only for benchmarking or internal tooling where auth overhead is undesirable.
> - The `openai/` and `anthropic/` model prefixes are routing conventions — they map to provider configs under `interfaces/config/litellm/providers/`.
