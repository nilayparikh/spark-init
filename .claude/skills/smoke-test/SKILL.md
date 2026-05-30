---
name: smoke-test
description: Run inference and GPU smoke tests against the active .init stack. Wraps existing test scripts with proper env var handling and result interpretation.
disable-model-invocation: true
---

# Smoke Test

Run health checks against the active .init inference stack.

## Usage

```
/smoke-test [type]
```

## Test Types

| Type | What it checks | Script |
|------|---------------|--------|
| `litellm` | LiteLLM proxy connectivity and model routing | `scripts/litellm-claude-smoke-test.sh` |
| `gpu` | GPU availability and CUDA runtime | `scripts/spark-gpu-smoke-test.py` |
| `all` | Run all available smoke tests (default) | — |

## Prerequisites

- The `.env` file must exist in the repo root with `LITELLM_MASTER_KEY` and `DGX_SPARK_M_API_KEY` set.
- For `litellm` tests: the `interface` profile must be active and LiteLLM must be reachable at `http://localhost:4000`.
- For `gpu` tests: NVIDIA drivers and `nvidia-smi` must be available.

## Steps

### litellm

1. Source `.env` to load `LITELLM_MASTER_KEY`.
2. Check if `http://localhost:4000` is reachable.
3. Run `scripts/litellm-claude-smoke-test.sh`.
4. Parse output for:
   - HTTP 200 responses
   - Model list includes expected models
   - Completion response is non-empty
5. Report pass/fail for each check.

### gpu

1. Run `python3 scripts/spark-gpu-smoke-test.py`.
2. Parse output for:
   - GPU detection (NVIDIA device found)
   - CUDA version
   - Memory allocation test
3. Report pass/fail for each check.

## Example

```
/smoke-test litellm
```

Output:
```
LiteLLM Smoke Test
==================
Proxy reachable: PASS (HTTP 200)
Model list: PASS (3 models found)
Completion: PASS (response received)

All checks passed.
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `Connection refused` | LiteLLM not running | Run `docker compose up -d` |
| `401 Unauthorized` | `LITELLM_MASTER_KEY` mismatch | Check `.env` and restart LiteLLM |
| `No GPU found` | NVIDIA runtime not configured | Check `nvidia-smi` and Docker GPU support |
