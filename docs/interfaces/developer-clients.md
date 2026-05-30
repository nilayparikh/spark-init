# Developer Client Notes

This proxy intentionally exposes three stable request surfaces:

- OpenAI Chat Completions on `http://localhost:4000/v1/chat/completions`
- OpenAI Responses on `http://localhost:4000/v1/responses`
- Anthropic Messages on `http://localhost:4000/v1/messages`

## Best Practices

1. Keep the public route truthful about the client-facing contract and the upstream adapter truthful about the real backend.
2. Use `drop_params: true` with a tight `supported_openai_params` allowlist for custom or OpenAI-compatible backends. This keeps OpenAI-style developer clients working without forwarding a noisy or deprecated param surface.
3. Publish Claude Code-safe discovery aliases with `.INIT/` prefix for gateway model discovery.
4. Leave `forward_client_headers_to_llm_api` off unless you are deliberately forwarding Claude Max or Team OAuth headers to Anthropic's first-party API. Turning it on globally against non-Anthropic backends can leak gateway auth headers upstream.
5. Keep the public catalog consistent. Model IDs follow the `<Provider>/<Name>` convention.
6. Use exact hardcoded aliases only when a client truly requires them.

## OpenAI-Compatible IDE Clients

Use this shape for VS Code extensions, Codex-style clients, Continue, Cline, OpenClaw, Hermes Agent, and other OpenAI-compatible tools:

```json
{
  "baseURL": "http://localhost:4000/v1",
  "apiKey": "<LITELLM_MASTER_KEY or scoped virtual key>",
  "model": "DGX/Qwen3.6-27B"
}
```

## OpenClaw

OpenClaw expects an OpenAI-compatible endpoint. Point it at `http://localhost:4000/v1`, authenticate with a LiteLLM bearer key, and use any model ID from the [available models catalog](../api/openai-compatible.md#all-available-models).

If the OpenClaw config exposes an API selector, use its OpenAI-completions mode instead of an Anthropic mode.

## Hermes Agent

Hermes Agent uses the OpenAI surface as well. This proxy already validates the key routes Hermes-style clients care about:

- `GET /v1/models`
- `POST /v1/chat/completions`
- `POST /v1/responses`

For Hermes, use any model ID from the [available models catalog](../api/openai-compatible.md#all-available-models).

## Claude Code

Claude Code should target the Anthropic surface on the gateway root, not the OpenAI `/v1` base:

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="<LITELLM_MASTER_KEY or scoped virtual key>"
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
```

After launching `claude`, use `/model` and pick one of the `.INIT/` canonical aliases:

| `/model` value | Backend |
|----------------|---------|
| `.INIT/Pro` | DGX Qwen 3.6 27B (local, llama.cpp) |
| `.INIT/Flash` | DGX Qwen 3.6 35B A3B (local, llama.cpp) |
| `.INIT/Ultra` | OpenCode Zen BIG PICKLE (cloud) |

All `.INIT/` aliases are published on the Anthropic messages surface, discovered via gateway model discovery, and routed via LiteLLM's `model_group_alias` configuration.

Notes:

- The gateway discovery list is filtered by the key you use. A scoped virtual key is the cleanest way to surface only the models you want Claude Code to see.
- `use_chat_completions_url_for_anthropic_messages: true` remains enabled in the root LiteLLM config, so Anthropic-message requests are transparently translated to the OpenAI-compatible backend.
- If you later add a real Anthropic upstream for Claude Max or Team OAuth passthrough, then enable `forward_client_headers_to_llm_api` only for that Anthropic route or model group.

## Claude Smoke Test

Use [scripts/litellm-claude-smoke-test.sh](../../scripts/litellm-claude-smoke-test.sh) to verify Claude Code-facing discovery plus Anthropic Messages routing against a running LiteLLM proxy.

```bash
./scripts/litellm-claude-smoke-test.sh
```

The script will:

- fetch `/v1/models` and verify discoverable model IDs
- send a minimal `POST /v1/messages` probe to each discovered model unless you pass `--discovery-only`
- reuse `LITELLM_API_KEY` when set, or fall back to the running `litellm` container's `LITELLM_MASTER_KEY`

If you want a one-off manual probe instead of the script, use this shape:

```bash
curl -sS \
  -X POST http://localhost:4000/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: ${LITELLM_API_KEY}" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": ".INIT/Pro",
    "max_tokens": 16,
    "messages": [
      {"role": "user", "content": "Reply with exactly OK."}
    ]
  }'
```

Use `--discovery-only` first if the remote provider API keys are unset and you only want to validate model publication.
