# Interface Telemetry Standard

## Goal

Every interface runtime should be transformed into a common metric shape so one Grafana dashboard can compare request pressure, token throughput, and context usage across providers.

## Required Labels

- Shared platform labels: `cluster_tenant`, `environment`, `stack`, `site`, `role`, `host`
- Interface identity labels: `provider_family`, `interface_name`, `interface_instance`, `service_name`, `model_alias`
- Routing labels: `job=interface-llm`, `instance=<stable interface instance>`, `telemetry_scope=interface`

## Standard Metric Set

These metrics form the minimum provider-agnostic contract:

- `llm_provider_requests_active`
- `llm_provider_requests_deferred`
- `llm_provider_input_tokens_total`
- `llm_provider_input_seconds_total`
- `llm_provider_input_tokens_per_second`
- `llm_provider_output_tokens_total`
- `llm_provider_output_seconds_total`
- `llm_provider_output_tokens_per_second`
- `llm_provider_context_tokens_high_watermark`
- `llm_provider_decode_calls_total`
- `llm_provider_busy_slots_per_decode`
- `llm_provider_total_slots`
- `llm_provider_slot_processing{slot_id}`
- `llm_provider_slot_context_capacity_tokens{slot_id}`
- `llm_provider_slot_generation_limit_tokens{slot_id}`
- `llm_provider_slot_output_tokens_generated{slot_id}`
- `llm_provider_slot_output_tokens_remaining{slot_id}`
- `llm_provider_slot_speculative_enabled{slot_id}`
- `llm_provider_exporter_source_up{source}`

## Transformation Rules

1. Preserve native exporter metrics if the runtime already exposes them.
2. Add the normalized `llm_provider_*` series alongside the native metrics.
3. Never turn request IDs into labels; if a runtime exposes task IDs, export them as metric values only.
4. Keep slot-level labels limited to `slot_id` and other low-cardinality runtime dimensions.
5. If a runtime cannot expose a standard metric directly, document the gap instead of synthesizing incorrect data.

## Provider Gap Policy

Some providers expose only aggregate counters, while others expose request or batch state.

- If a metric exists natively, map it directly.
- If it can be derived exactly from a provider metadata endpoint, export the derived metric.
- If it requires guessing or sampling that loses correctness, do not emit it as a standard metric.

## llama.cpp Mapping Status

- Aggregate request and token throughput: supported.
- Current slot state and output progress: supported via `/slots`.
- Completed per-request prompt and completion sizes: not supported from server telemetry alone.

## Dashboard Contract

The shared interface dashboard should assume only the normalized metric set above. Provider-specific dashboards may add native metrics, but the cross-provider dashboard should not depend on provider-exclusive names.