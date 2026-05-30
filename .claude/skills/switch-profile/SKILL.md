---
name: switch-profile
description: Safely switch the active Docker Compose profile set for the .init stack. Handles teardown of current profiles and startup of the new ones.
disable-model-invocation: true
---

# Switch Docker Compose Profile

Switch the active `COMPOSE_PROFILES` for the .init platform.

## Usage

```
/switch-profile <profile-set>
```

## Available Profile Sets

| Profile Set | Services |
|-------------|----------|
| `llama-qwen-3-6-27b` | data, obs, interface, llama-qwen-3-6-27b |
| `vllm-qwen-3-6-27b` | data, interface, vllm-qwen-3-6-27b |
| `vllm-qwen-3-6-35b-a3b` | data, vllm-qwen-3-6-35b-a3b |
| `data-only` | data |
| `obs-only` | data, obs |
| `interface-only` | data, interface |

## Safety Rules

- `llama-qwen-3-6-27b` and `vllm-qwen-3-6-27b` are **mutually exclusive** (both use host port 8000).
- Always run from the repository root where `docker-compose.yml` lives.
- The `.env` file in the repo root controls `COMPOSE_PROFILES`.

## Steps

1. Read the current `.env` to capture the existing `COMPOSE_PROFILES` value.
2. If the requested profile set is the same as the current one, report "Already active" and exit.
3. Run `docker compose down` to stop the current stack.
4. Update `COMPOSE_PROFILES=` in `.env` to the new profile set.
5. Run `docker compose up -d` to start the new stack.
6. Run `docker compose ps` to verify services are healthy.
7. Report which services are running and on what ports.

## Example

```
/switch-profile vllm-qwen-3-6-27b
```

Output:
```
Stopping current stack (llama-qwen-3-6-27b)...
Updating COMPOSE_PROFILES to: data,interface,vllm-qwen-3-6-27b
Starting new stack...
NAME                STATUS          PORTS
postgres            Up 2 seconds    0.0.0.0:5432->5432/tcp
litellm             Up 1 second     0.0.0.0:4000->4000/tcp
vllm-qwen-3-6-27b   Up 1 second     0.0.0.0:8000->8000/tcp
```
