#!/bin/bash
# =============================================================================
# trivy-scan.sh — Post-tool-use hook
#
# Scans every written/modified file for secrets and misconfigurations using
# Trivy. Replaces the old protect-env.sh + scan-secrets.sh + run-linter.sh
# multi-hook system with a single unified scan.
#
# Scanners:  secret, misconfig
# Severity:  CRITICAL, HIGH, MEDIUM
# Config:    trivy-secret.yaml (custom rule definitions)
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

# ── Skip paths that are expected to contain secrets or are irrelevant ──
echo "$FILE_PATH" | grep -q '/\.env$' && exit 0
echo "$FILE_PATH" | grep -q '/\.env\.example$' && exit 0
echo "$FILE_PATH" | grep -qE '(trivy\.yaml|trivy-secret\.yaml)$' && exit 0
echo "$FILE_PATH" | grep -q '/\.claude/hooks/' && exit 0
echo "$FILE_PATH" | grep -q '/\.git/' && exit 0

# Skip empty files
[[ ! -s "$FILE_PATH" ]] && exit 0

# Check trivy availability
if ! command -v trivy &>/dev/null; then
  exit 0
fi

# ── Run Trivy: secret + misconfig scan on the single file ─────────────
OUTPUT=$(trivy fs \
  --scanners secret,misconfig \
  --secret-config /workspace/trivy-secret.yaml \
  --severity CRITICAL,HIGH,MEDIUM \
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
