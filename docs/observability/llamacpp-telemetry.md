# llama.cpp Telemetry

## Native Endpoints

- `GET /metrics`: native Prometheus-compatible exporter. Requires `--metrics` at process start.
- `GET /slots`: current per-slot runtime state. Enabled by default unless `--no-slots` is set.
- `GET /props`: runtime configuration and capability metadata.

## Native Metrics Meaning

| Native Metric | Meaning | Standard Metric |
| --- | --- | --- |
| `llamacpp:prompt_tokens_total` | Total prompt tokens processed across requests. | `llm_provider_input_tokens_total` |
| `llamacpp:prompt_seconds_total` | Total prompt-processing time in seconds. | `llm_provider_input_seconds_total` |
| `llamacpp:prompt_tokens_seconds` | Current average prompt throughput. | `llm_provider_input_tokens_per_second` |
| `llamacpp:tokens_predicted_total` | Total output tokens generated across requests. | `llm_provider_output_tokens_total` |
| `llamacpp:tokens_predicted_seconds_total` | Total generation time in seconds. | `llm_provider_output_seconds_total` |
| `llamacpp:predicted_tokens_seconds` | Current average generation throughput. | `llm_provider_output_tokens_per_second` |
| `llamacpp:requests_processing` | Number of requests currently being processed. | `llm_provider_requests_active` |
| `llamacpp:requests_deferred` | Number of requests currently queued or deferred. | `llm_provider_requests_deferred` |
| `llamacpp:n_tokens_max` | High watermark of total context tokens observed by the server. | `llm_provider_context_tokens_high_watermark` |
| `llamacpp:n_decode_total` | Total `llama_decode()` calls executed. | `llm_provider_decode_calls_total` |
| `llamacpp:n_busy_slots_per_decode` | Average number of busy slots per decode call. | `llm_provider_busy_slots_per_decode` |

## Derived Slot And Runtime Metrics

The lightweight exporter also converts `GET /slots` and `GET /props` into Prometheus metrics so Grafana can show live request shape and runtime metadata:

- `llm_provider_total_slots`
- `llm_provider_server_sleeping`
- `llm_provider_endpoint_metrics_enabled`
- `llm_provider_endpoint_slots_enabled`
- `llm_provider_endpoint_props_enabled`
- `llm_provider_slot_processing{slot_id}`
- `llm_provider_slot_context_capacity_tokens{slot_id}`
- `llm_provider_slot_generation_limit_tokens{slot_id}`
- `llm_provider_slot_output_tokens_generated{slot_id}`
- `llm_provider_slot_output_tokens_remaining{slot_id}`
- `llm_provider_slot_speculative_enabled{slot_id}`
- `llm_provider_slot_task_id{slot_id}`
- `llm_provider_exporter_source_up{source="native_metrics|slots|props"}`

## What llama.cpp Does Not Expose Natively

The native telemetry does **not** provide a durable per-request event record containing:

- completed request input token count per request
- completed request output token count per request
- request latency histogram
- request identifiers with prompt and completion sizes attached

That means the current server-side scrape can show:

- aggregate prompt and generation totals
- current in-flight request state
- context high watermark
- live slot output progress

It cannot reconstruct historical request-by-request prompt and completion sizes after the request finishes.

## If Per-Request Records Are Required

To capture completed request records in a standardized way, add one of these in front of or alongside the provider:

1. an HTTP middleware or reverse proxy that records request and response token fields
2. client-side instrumentation that emits request metrics after each completion
3. a dedicated provider adapter that converts response timing payloads into metrics or traces

For llama.cpp specifically, the response payload already includes `timings.prompt_n`, `timings.cache_n`, and `timings.predicted_n`, so a proxy or client adapter can produce exact per-request context records without guessing.
