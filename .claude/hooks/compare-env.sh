#!/bin/bash
# =============================================================================
# compare-env.sh — .env vs .env.example sync checker
#
# Compares the key sets between .env and .env.example to find:
#   1) Keys in .env.example missing from .env (need to be added by user)
#   2) Keys in .env not in .env.example (orphaned / cleaned up)
#
# Never outputs secret values — only key names.
#
# Usage:
#   ! .claude/hooks/compare-env.sh
# =============================================================================
set -euo pipefail

# Resolve workspace root (assumes hooks live in .claude/hooks/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"

ENV_FILE="$WORKSPACE/.env"
ENV_EXAMPLE="$WORKSPACE/.env.example"

# ── Color helpers (if terminal supports) ──────────────────────────────────
RED=''; GREEN=''; YELLOW=''; BOLD=''; RESET=''
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  BOLD='\033[1m'
  RESET='\033[0m'
fi

# ── Check prerequisites ───────────────────────────────────────────────────
if [ ! -f "$ENV_EXAMPLE" ]; then
  echo "${RED}❌ .env.example not found at: $ENV_EXAMPLE${RESET}" >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "${YELLOW}⚠️  .env file doesn't exist at: $ENV_FILE${RESET}" >&2
  echo "" >&2
  echo "   To initialize from template:" >&2
  echo "     cp $ENV_EXAMPLE $ENV_FILE" >&2
  echo "   Then fill in the secrets manually." >&2
  exit 0
fi

# ── Extract key names ─────────────────────────────────────────────────────
# Key = everything before the first '=', skipping comments and blank lines
get_keys() {
  grep -v '^[[:space:]]*#' "$1" |
    grep -v '^[[:space:]]*$' |
    grep '=' |
    sed 's/=.*//' |
    sed 's/^[[:space:]]*//' |
    sed 's/[[:space:]]*$//' |
    sort -u
}

EXAMPLE_KEYS=$(get_keys "$ENV_EXAMPLE")
ENV_KEYS=$(get_keys "$ENV_FILE")

# ── Counts ────────────────────────────────────────────────────────────────
EXAMPLE_COUNT=$(echo "$EXAMPLE_KEYS" | wc -l)
ENV_COUNT=$(echo "$ENV_KEYS" | wc -l)

echo ""
echo "${BOLD}═══════════════════════════════════════════════════════════════${RESET}"
echo "${BOLD}  🔄 .env Sync Report${RESET}"
echo "${BOLD}═══════════════════════════════════════════════════════════════${RESET}"
echo ""
echo "  ·env.example:  ${EXAMPLE_COUNT} keys"
echo "  ·env:          ${ENV_COUNT} keys"
echo ""

# ── Keys MISSING from .env (present in example only) ─────────────────────
echo "${BOLD}📋  Keys to ADD to .env:${RESET}"
echo "     (in .env.example but missing from your .env)"
echo ""

MISSING=$(comm -23 <(echo "$EXAMPLE_KEYS") <(echo "$ENV_KEYS"))
if [[ -z "$MISSING" ]]; then
  echo "     ${GREEN}✅ All .env.example keys are present in .env${RESET}"
else
  while IFS= read -r key; do
    [[ -z "$key" ]] && continue
    echo "     ${YELLOW}➕ ${key}${RESET}"
  done <<< "$MISSING"
fi

echo ""

# ── ORPHANED keys (present in .env only) ─────────────────────────────────
echo "${BOLD}🗑️  Orphaned keys (maybe removable):${RESET}"
echo "     (in your .env but not in .env.example)"
echo ""

ORPHANED=$(comm -13 <(echo "$EXAMPLE_KEYS") <(echo "$ENV_KEYS"))
if [[ -z "$ORPHANED" ]]; then
  echo "     ${GREEN}✅ No orphaned keys in .env${RESET}"
else
  while IFS= read -r key; do
    [[ -z "$key" ]] && continue
    echo "     ${YELLOW}🗑️  ${key}${RESET}"
  done <<< "$ORPHANED"
fi

echo ""

# ── Summary ────────────────────────────────────────────────────────────────
echo "${BOLD}═══════════════════════════════════════════════════════════════${RESET}"
if [[ -z "$MISSING" && -z "$ORPHANED" ]]; then
  echo "  ${GREEN}✅ .env is fully in sync with .env.example${RESET}"
  echo ""
  echo "  No action needed."
elif [[ -z "$MISSING" ]]; then
  echo "  ⚠️  No new keys to add, but ${ORPHANED_COUNT} orphaned key(s) exist."
  echo "  Consider removing them if no longer needed."
else
  MISSING_COUNT=$(echo "$MISSING" | grep -c . || echo "0")
  echo "  ${YELLOW}⚠️  ${MISSING_COUNT} key(s) need to be added to .env${RESET}"
  echo ""
  echo "  Next steps:"
  echo "    1. For each missing key, ask the user to add it to .env manually"
  echo "    2. Run this check again to confirm sync"
  echo "    3. If a key has a safe default, consider adding it to .env.example instead"
fi
echo "${BOLD}═══════════════════════════════════════════════════════════════${RESET}"
echo ""
