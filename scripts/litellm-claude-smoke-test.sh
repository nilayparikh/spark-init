#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${LITELLM_BASE_URL:-http://localhost:4000}"
API_KEY="${LITELLM_API_KEY:-}"
CONTAINER_NAME="${LITELLM_CONTAINER_NAME:-litellm}"
TIMEOUT_SECONDS="${LITELLM_SMOKE_TIMEOUT:-60}"
PROMPT_TEXT="${LITELLM_SMOKE_PROMPT:-Reply with exactly OK.}"
DISCOVERY_ONLY=0
READINESS_ATTEMPTS="${LITELLM_READINESS_ATTEMPTS:-12}"
READINESS_SLEEP_SECONDS="${LITELLM_READINESS_SLEEP_SECONDS:-2}"

DEFAULT_MODELS=(
  "azure-anthropic-kimi-k2.6"
  "azure-anthropic-deepseek-v4-flash"
  "dgx-anthropic-qwen3.6-27b-swe"
  "dgx-anthropic-qwen3.6-27b-writing"
  "nvidia-anthropic-deepseek-v4-flash"
  "nvidia-anthropic-minimax-m2.7"
  "nvidia-anthropic-kimi-k2.6"
  "deepseek-anthropic-deepseek-v4-flash"
  "deepseek-anthropic-deepseek-v4-pro"
  "claude-opus-4.7"
  "claude-sonnet-4.6"
  "claude-haiku-4.6"
  "claude-haiku-4-5-20251001"
  "claude-haiku-4-5"
)

SELECTED_MODELS=()

usage() {
  cat <<'EOF'
Usage: ./scripts/litellm-claude-smoke-test.sh [options]

Options:
  --base-url URL         LiteLLM base URL. Default: http://localhost:4000
  --api-key KEY          LiteLLM API key. Falls back to the running litellm container key.
  --container NAME       LiteLLM container name for API key fallback. Default: litellm
  --timeout SECONDS      Curl timeout per request. Default: 60
  --model MODEL_ID       Restrict validation to one public model ID. Repeatable.
  --readiness-attempts N Retry /v1/models readiness before failing. Default: 12
  --discovery-only       Only verify /v1/models publication; skip live /v1/messages probes.
  --help                 Show this help text.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url)
      BASE_URL="$2"
      shift 2
      ;;
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --container)
      CONTAINER_NAME="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT_SECONDS="$2"
      shift 2
      ;;
    --readiness-attempts)
      READINESS_ATTEMPTS="$2"
      shift 2
      ;;
    --model)
      SELECTED_MODELS+=("$2")
      shift 2
      ;;
    --discovery-only)
      DISCOVERY_ONLY=1
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ${#SELECTED_MODELS[@]} -eq 0 ]]; then
  SELECTED_MODELS=("${DEFAULT_MODELS[@]}")
fi

resolve_api_key() {
  if [[ -n "$API_KEY" ]]; then
    return
  fi

  if command -v docker >/dev/null 2>&1 && docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    API_KEY="$(docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$CONTAINER_NAME" | awk -F= '/^LITELLM_MASTER_KEY=/{sub(/^[^=]*=/, ""); print; exit}')"
  fi

  if [[ -z "$API_KEY" ]]; then
    echo "Unable to resolve LiteLLM API key. Set LITELLM_API_KEY or pass --api-key." >&2
    exit 1
  fi
}

extract_missing_models() {
  local models_file="$1"
  shift

  python3 - "$models_file" "$@" <<'PY'
import json
import sys

payload_path = sys.argv[1]
requested = sys.argv[2:]
with open(payload_path, "r", encoding="utf-8") as handle:
    payload = json.load(handle)

available = {item.get("id") for item in payload.get("data", []) if item.get("id")}
missing = [model for model in requested if model not in available]
for model in missing:
    print(model)
PY
}

extract_response_summary() {
  local response_file="$1"

  python3 - "$response_file" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    payload = json.load(handle)

error = payload.get("error")
if isinstance(error, dict):
    message = error.get("message") or json.dumps(error, ensure_ascii=True)
    print(message)
    raise SystemExit(0)

content = payload.get("content") or []
for item in content:
    if item.get("type") == "text":
        print((item.get("text") or "").strip())
        raise SystemExit(0)

print(json.dumps(payload, ensure_ascii=True))
PY
}

resolve_api_key

wait_for_models_ready() {
  local attempt
  local response_file="$1"
  local status_code="000"

  for (( attempt = 1; attempt <= READINESS_ATTEMPTS; attempt++ )); do
    if status_code="$(curl -sS --max-time "$TIMEOUT_SECONDS" -o "$response_file" -w '%{http_code}' -H "Authorization: Bearer $API_KEY" "$BASE_URL/v1/models" 2>/dev/null)"; then
      if [[ "$status_code" == "200" ]]; then
        printf '%s' "$status_code"
        return 0
      fi
    fi

    if [[ "$attempt" -lt "$READINESS_ATTEMPTS" ]]; then
      sleep "$READINESS_SLEEP_SECONDS"
    fi
  done

  printf '%s' "$status_code"
  return 1
}

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

models_file="$tmpdir/models.json"
if ! status_code="$(wait_for_models_ready "$models_file")"; then
  echo "Discovery request failed before an HTTP response was returned after ${READINESS_ATTEMPTS} readiness attempts." >&2
  cat "$models_file" 2>/dev/null >&2 || true
  exit 1
fi

if [[ "$status_code" != "200" ]]; then
  echo "Discovery request failed with HTTP $status_code" >&2
  cat "$models_file" >&2
  exit 1
fi

missing_models_file="$tmpdir/missing-models.txt"
extract_missing_models "$models_file" "${SELECTED_MODELS[@]}" > "$missing_models_file"

if [[ -s "$missing_models_file" ]]; then
  echo "Missing published Anthropic-facing model IDs:" >&2
  cat "$missing_models_file" >&2
  exit 1
fi

echo "Discovery OK for ${#SELECTED_MODELS[@]} model IDs."

if [[ "$DISCOVERY_ONLY" == "1" ]]; then
  exit 0
fi

probe_failures=0

for model in "${SELECTED_MODELS[@]}"; do
  request_file="$tmpdir/request.json"
  response_file="$tmpdir/${model//[^A-Za-z0-9._-]/_}.json"

  python3 - "$model" "$PROMPT_TEXT" > "$request_file" <<'PY'
import json
import sys

payload = {
    "model": sys.argv[1],
    "max_tokens": 16,
    "messages": [{"role": "user", "content": sys.argv[2]}],
}
json.dump(payload, sys.stdout)
PY

  if ! status_code="$(curl -sS --max-time "$TIMEOUT_SECONDS" -o "$response_file" -w '%{http_code}' -X POST "$BASE_URL/v1/messages" -H "content-type: application/json" -H "x-api-key: $API_KEY" -H 'anthropic-version: 2023-06-01' --data @"$request_file")"; then
    echo "FAIL $model transport error: curl exited before an HTTP response was returned" >&2
    probe_failures=1
    continue
  fi

  if [[ "$status_code" != "200" ]]; then
    echo "FAIL $model HTTP $status_code: $(extract_response_summary "$response_file")" >&2
    probe_failures=1
    continue
  fi

  echo "PASS $model: $(extract_response_summary "$response_file")"
done

exit "$probe_failures"