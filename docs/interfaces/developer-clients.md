# Developer Client Notes

This proxy intentionally exposes three stable request surfaces:

- OpenAI Chat Completions on `http://localhost:4000/v1/chat/completions`
- OpenAI Responses on `http://localhost:4000/v1/responses`
- Anthropic Messages on `http://localhost:4000/v1/messages`

## Best Practices

1. Keep the public route truthful about the client-facing contract and the upstream adapter truthful about the real backend. `*-openai-*` entries stay OpenAI-facing. `*-anthropic-*` entries and `claude-*` aliases are Anthropic-compatible public routes for Claude Code, but they can still reuse an OpenAI-backed LiteLLM adapter when the upstream endpoint is OpenAI-shaped.
2. Use `drop_params: true` with a tight `supported_openai_params` allowlist for custom or OpenAI-compatible backends. This keeps OpenAI-style developer clients working without forwarding a noisy or deprecated param surface.
3. Publish Claude Code-safe discovery aliases with an `anthropic/` prefix. Claude Code gateway discovery only adds models from `/v1/models` whose IDs start with `anthropic` or `claude`.
4. Leave `forward_client_headers_to_llm_api` off unless you are deliberately forwarding Claude Max or Team OAuth headers to Anthropic's first-party API. Turning it on globally against non-Anthropic backends can leak gateway auth headers upstream.
5. Keep the public catalog consistent. This stack now uses `openai/<Provider>/...` and `anthropic/<Provider>/...` for the provider-backed aliases.
6. Use exact hardcoded aliases only when a client truly requires them. This stack publishes the latest Claude compatibility aliases separately from the provider-backed catalog.

## OpenAI-Compatible IDE Clients

Use this shape for VS Code extensions, Codex-style clients, Continue, Cline, OpenClaw, Hermes Agent, and other OpenAI-compatible tools:

```json
{
  "baseURL": "http://localhost:4000/v1",
  "apiKey": "<LITELLM_MASTER_KEY or scoped virtual key>",
  "model": "openai/DGX/Qwen3.6 27B/SWE"
}
```

Recommended OpenAI-facing model IDs:

- `openai/DGX/Qwen3.6 27B/SWE`
- `openai/DGX/Qwen3.6 27B/Writing`
- `openai/Azure/Kimi K2.6/Master Orchestrator`
- `openai/Azure/DeepSeek V4 Flash`
- `openai/NVIDIA/Kimi K2.6`
- `openai/NVIDIA/MiniMax M2.7`
- `openai/DeepSeek/DeepSeek V4 Flash`
- `openai/DeepSeek/DeepSeek V4 Pro`

## OpenClaw

OpenClaw expects an OpenAI-compatible endpoint. Point it at `http://localhost:4000/v1`, authenticate with a LiteLLM bearer key, and use the OpenAI-facing model IDs above.

If the OpenClaw config exposes an API selector, use its OpenAI-completions mode instead of an Anthropic mode.

## Hermes Agent

Hermes Agent uses the OpenAI surface as well. This proxy already validates the key routes Hermes-style clients care about:

- `GET /v1/models`
- `POST /v1/chat/completions`
- `POST /v1/responses`

For Hermes, prefer the OpenAI aliases such as `openai/DGX/Qwen3.6 27B/SWE`.

## Claude Code

Claude Code should target the Anthropic surface on the gateway root, not the OpenAI `/v1` base:

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="<LITELLM_MASTER_KEY or scoped virtual key>"
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
```

After launching `claude`, use `/model` and pick one of the `anthropic/...` discovery aliases or the direct Claude compatibility aliases, for example:

- `anthropic/DGX/Qwen3.6 27B/SWE`
- `anthropic/DGX/Qwen3.6 27B/Writing`
- `anthropic/Azure/Kimi K2.6/Master Orchestrator`
- `anthropic/NVIDIA/Kimi K2.6`
- `anthropic/DeepSeek/DeepSeek V4 Pro`
- `claude-opus-4.7`
- `claude-sonnet-4.6`
- `claude-haiku-4.6`
- `claude-haiku-4-5-20251001`

Current Claude compatibility routing:

- `claude-opus-4-7` routes to the Anthropic-compatible Azure Kimi K2.6 entry
- `claude-sonnet-4-6` routes to the Anthropic-compatible DGX Qwen 3.6 27B SWE entry
- `claude-haiku-4-6` routes to the Anthropic-compatible DGX Qwen 3.6 27B SWE entry
- `claude-haiku-4-5-20251001` routes to the Anthropic-compatible DeepSeek V4 Flash entry
- `claude-haiku-4-5` is also published as Anthropic's convenience alias for the same latest Haiku route

Notes:

- The gateway discovery list is filtered by the key you use. A scoped virtual key is the cleanest way to surface only the models you want Claude Code to see.
- `use_chat_completions_url_for_anthropic_messages: true` remains enabled in the root LiteLLM config, and the `*-anthropic-*` plus `claude-*` routes are published on the Anthropic surface for Claude Code discovery while still reusing the correct upstream adapter for the backing model.
- Anthropic's current latest official Claude identifiers are `claude-opus-4-7`, `claude-sonnet-4-6`, and `claude-haiku-4-5-20251001`; this repo also publishes local Claude Code compatibility aliases `claude-opus-4.7`, `claude-sonnet-4.6`, and `claude-haiku-4.6` for the Anthropic-facing provider routes above.
- If you later add a real Anthropic upstream for Claude Max or Team OAuth passthrough, then enable `forward_client_headers_to_llm_api` only for that Anthropic route or model group.

## Claude Smoke Test

Use [scripts/litellm-claude-smoke-test.sh](../../scripts/litellm-claude-smoke-test.sh) to verify Claude Code-facing discovery plus Anthropic Messages routing against a running LiteLLM proxy.

```bash
./scripts/litellm-claude-smoke-test.sh
```

The script will:

- fetch `/v1/models` and verify every `*-anthropic-*` and `claude-*` public ID is discoverable
- send a minimal `POST /v1/messages` probe to each discovered Anthropic-facing route unless you pass `--discovery-only`
- reuse `LITELLM_API_KEY` when set, or fall back to the running `litellm` container's `LITELLM_MASTER_KEY`

If you want a one-off manual probe instead of the script, use this shape:

```bash
curl -sS \
  -X POST http://localhost:4000/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: ${LITELLM_API_KEY}" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4.7",
    "max_tokens": 16,
    "messages": [
      {"role": "user", "content": "Reply with exactly OK."}
    ]
  }'
```

Use `--discovery-only` first if the remote provider API keys are unset and you only want to validate model publication.
