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
    "model": "openai/qwen3.6_27b",
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
    "model": "qwen3.6-27b",
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
  "model": "openai/qwen3.6_27b",
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
    "model": "openai/qwen3.6_27b",
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

### LiteLLM Proxy

Through the proxy, models are identified by the routing name defined in the LiteLLM config (`interfaces/config/litellm/`):

```
openai/<model-alias>
```

For example:
- `openai/qwen3.6_27b` — Qwen 3.6 27B via llama.cpp
- `openai/Kimi-K2.6-1` — Azure orchestrator model

The `openai/` prefix tells LiteLLM to route using the OpenAI-compatible backend. The alias maps to a specific provider and endpoint in the LiteLLM config.

### llama.cpp Direct

Direct access uses the model name as loaded by llama.cpp (typically the GGUF filename without extension):

```
qwen3.6-27b-text-nvfp4-mtp
```

## Response Format

### Non-Streaming

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "openai/qwen3.6_27b",
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
    model="openai/qwen3.6_27b",
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
> - The `openai/` model prefix in LiteLLM is a routing convention, not a requirement — it maps to the `openai/*` provider in the config.
