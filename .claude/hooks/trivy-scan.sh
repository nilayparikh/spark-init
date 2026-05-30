#!/bin/bash
# =============================================================================
# trivy-scan.sh — Post-tool-use hook
#
# Scans every written/modified file for secrets and misconfigurations using
# Trivy. Uses trivy.yaml as config and trivy-secret.yaml for custom rules.
#
# Scanners:  secret, misconfig
# Severity:  CRITICAL, HIGH, MEDIUM
# =============================================================================
set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only run on Edit | Write
[[ ! "$TOOL_NAME" =~ ^(Edit|Write)$ ]] && exit 0
[[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]] && exit 0

# Resolve to absolute path
FILE_PATH=$(cd "$(dirname "$FILE_PATH")" && pwd)/$(basename "$FILE_PATH")

# Skip empty files
[[ ! -s "$FILE_PATH" ]] && exit 0

# Check trivy availability
if ! command -v trivy &>/dev/null; then
  exit 0
fi

# ── Run Trivy — config in trivy.yaml, custom rules in trivy-secret.yaml ──
OUTPUT=$(trivy fs \
  --config /workspace/trivy.yaml \
  --format table \
  --quiet \
  "$FILE_PATH" 2>&1) || true

# Only report if there are actual findings
if echo "$OUTPUT" | grep -qE '(CRITICAL|HIGH|MEDIUM)'; then
  echo "" >&2
  echo "  Trivy findings in $(basename "$FILE_PATH"):" >&2
  echo "$OUTPUT" | grep -E '(CRITICAL|HIGH|MEDIUM)|^  ' >&2
  echo "" >&2
  echo "  -> If real secrets, move to .env and reference via env vars." >&2
  echo "  -> If false positives, add allow-rules to trivy-secret.yaml." >&2
  echo "" >&2
fi

exit 0
