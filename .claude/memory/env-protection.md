---
name: env-protection
description: Trivy-based secret scanning and .env protection strategy
metadata:
  type: reference
---

Security scanning uses a single unified Trivy hook instead of the old multi-hook system.

**How it works:**
- **PostToolUse hook** (`trivy-scan.sh`) — runs on every Edit/Write, scans the
  modified file for secrets and misconfigurations using Trivy.
- **CI workflow** (`.github/workflows/trivy.yml`) — full repository scan on every
  push/PR + daily scheduled scan.
- **Config** (`trivy-secret.yaml`) — custom rules for OpenAI/LiteLLM keys and
  DB connection strings.
- **Strategy** (`trivy.yaml`) — documents scanner choices and severity levels.

**What gets scanned:**
- `secret` scanner — hardcoded API keys, passwords, tokens (CRITICAL + HIGH)
- `misconfig` scanner — Dockerfile, kubernetes, terraform patterns (CRITICAL + HIGH)
- Overall severity filter: CRITICAL, HIGH, MEDIUM

**What gets skipped:**
- `.env` and `.env.example` (expected to contain secrets/placeholders)
- `.git/`, `.claude/hooks/`, `node_modules/`
- Empty files

**Compare .env sync:**
- `! .claude/hooks/compare-env.sh` — compares key names between `.env` and
  `.env.example` (never shows values). Run at session end.

**Why:** Simplified from 3 separate hooks (protect-env, scan-secrets, run-linter)
to one Trivy invocation. Same coverage, less complexity.

**How to apply:**
- At session end, run `! .claude/hooks/compare-env.sh` to check sync.
- If a user needs to check a .env value, ask them to run it themselves
  (e.g., `grep LITELLM_MASTER_KEY .env`).
- False positives → add allow-rules to `trivy-secret.yaml`.
