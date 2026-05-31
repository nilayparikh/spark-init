# Examples

Real prompts and what the system does with them. Use these to pattern-match your own tasks.

---

## Case 1: Quick Question (Inline, No Agents)

**Prompt:**
```text
What does the retry_policy section in the LiteLLM config do?
```

**What happens:**

| Step | Who | Action |
|------|-----|--------|
| Classify | Orchestrator (Flash) | Recognizes as a question — no code change |
| Execute | Orchestrator (Flash) | Reads `interfaces/config/litellm/config.yaml`, finds the section, explains it |
| Cost | — | ~$0.001 |

No agents spawned. The orchestrator answers directly from the codebase.

---

## Case 2: Single File Fix (Inline, 1 Pro Agent)

**Prompt:**
```text
The LiteLLM health endpoint returns 401 when require_auth_for_metrics_endpoint
is enabled. Fix it so health checks skip auth but metrics still require it.
Don't change any other behavior.
```

**What happens:**

| Step | Who | Action |
|------|-----|--------|
| Classify | Orchestrator (Flash) | Single file, well-defined fix → spawn Pro |
| Execute | Pro agent | Reads config, finds the `require_auth_for_metrics_endpoint` flag, adds a health endpoint exclusion pattern |
| Verify | Orchestrator (Flash) | Checks the change doesn't break other auth behavior |
| Cost | — | Free (Pro is local) |

**Expected output:** A summary of the change with file:line reference, and a note that health checks now bypass auth while `/metrics` still requires it.

---

## Case 3: Multi-File Feature (Light Workflow)

**Prompt:**
```text
Add request logging to the LiteLLM proxy that captures: model name,
response time, token count, and status code. Log to a new Postgres table
(with migration script). Add a Grafana dashboard panel showing request
volume by model over the last hour.
```

**What happens:**

| Phase | Agents | What They Do |
|-------|--------|--------------|
| Discover | 2 Flash (parallel) | One reads LiteLLM config + proxy setup; one reads Postgres init scripts + Grafana provisioning |
| Implement | 3 Pro (pipeline) | Pro 1: Adds migration script to `data/config/postgres-init/`. Pro 2: Adds logging config to LiteLLM. Pro 3: Adds dashboard panel JSON |
| Verify | 2 Flash (parallel) | One checks the migration is idempotent; one checks the dashboard JSON references the right datasource |
| Cost | — | ~$0.06 (Flash) + free (Pro) = **~$0.06** |

**Expected output:** Three files changed, each with an explanation. The orchestrator summarizes the integration: "Requests now log to a `request_logs` table, the LiteLLM config streams to it, and Grafana panel 'Request Volume by Model' shows the data."

---

## Case 4: Codebase Audit (Full Workflow)

**Prompt:**
```text
Run a workflow to audit every Docker Compose service for missing health
checks. Check all docker-compose*.yml files. For any service without a
health check, report the service name, file, and suggest an appropriate
health check command based on what the service does.
```

**What happens:**

| Phase | Agents | What They Do |
|-------|--------|--------------|
| Discover | 4 Flash (parallel) | Each scans a subset of compose files for service definitions without `healthcheck:` blocks |
| Deduplicate | (inline) | Script merges overlapping findings |
| Verify | 3 Pro (pipeline) | Each verifies a finding — reads the actual file, confirms no healthcheck, validates the suggested command is correct for that service |
| Report | 1 Flash | Synthesizes verified findings into a report |
| Cost | — | ~$0.08 (Flash) + free (Pro) = **~$0.08** |

**Expected output:** A table of services without health checks, each with a suggested `curl` or `pg_isready` command appropriate to the service.

---

## Case 5: Migration (Pipeline Workflow)

**Prompt:**
```text
Migrate all docker.litellm.ai/berriai/litellm:latest image references
to use ghcr.io/nilayparikh/litellm:stable. Scope is all compose files
and docs. Do NOT change CI workflow files — those use their own tagging.
```

**What happens:**

| Phase | Agents | What They Do |
|-------|--------|--------------|
| Discover | 1 Air | Scans entire repo (uses 256K context to read all matching files) for the old image reference |
| Implement | 3 Pro (pipeline) | Each replaces references in its assigned files, one at a time |
| Verify | 2 Flash (parallel) | One checks no old references remain; one checks CI files were NOT touched |
| Cost | — | Free (Air + Pro local) + ~$0.03 (Flash verify) = **~$0.03** |

**Expected output:** List of files changed with old→new reference. Explicit confirmation that CI files were skipped.

---

## Case 6: Research (Web-Enhanced)

**Prompt:**
```text
Research how Claude Code projects handle GPU passthrough in Docker.
Find 3-5 real-world examples from GitHub, blogs, or docs. For each,
summarize the approach and note any pitfalls they ran into.
```

**What happens:**

| Phase | Agents | What They Do |
|-------|--------|--------------|
| Research | 4 Flash (parallel) | Each searches a different angle: GitHub repos, Anthropic docs, NVIDIA docs, community blogs |
| Synthesize | 1 Ultra | Merges findings, removes duplicates, cross-references claims, writes cited report |
| Cost | — | ~$0.10 (Flash WebSearch) + ~$0.15 (Ultra) = **~$0.25** |

**Expected output:** A report with 3-5 examples, each with source URL, approach summary, and pitfalls.

---

## Case 7: Review a PR (Inline with Reviewer Agent)

**Prompt:**
```text
Review the changes in this branch for correctness, security, and
convention compliance. Focus on the observability config changes.
```

**What happens:**

| Step | Who | Action |
|------|-----|--------|
| Discover | Orchestrator (Flash) | `git diff main...HEAD` to identify changed files |
| Review | Reviewer agent (Flash) | Reads each changed file, checks against 5 review dimensions (correctness, security, integration, conventions, docs) |
| Report | Orchestrator (Flash) | Summarizes findings with severity levels |

**Expected output:** Review findings with CRITICAL/HIGH/MEDIUM/LOW severity, each with file:line and suggested fix.

---

## Edge Cases

### Edge Case 1: Ambiguous Scope

**Prompt:**
```text
Fix the config
```

**What happens:** The system can't determine which config or what's wrong. It asks: "Which config? What's the issue you're seeing?"

**Better prompt:**
```text
Fix the timeout setting in interfaces/config/litellm/config.yaml.
It's currently 300 seconds, but the 27B model sometimes takes 400+
seconds to load on cold start.
```

---

### Edge Case 2: Local Model Concurrency

**Scenario:** You have two Pro agents trying to run simultaneously (e.g., two code changes in the same workflow).

**What happens:** The system serializes Pro agents automatically in workflows. You don't need to manage this. But if you manually spawn two Pro agents at once (outside a workflow), the second one fails with a timeout or connection error — both agents hit `localhost:8000` and llama.cpp handles one request at a time.

**How to avoid:** Trust the workflow system. It serializes Pro and Air agents via `pipeline()`. If you're working inline, do one Pro task at a time.

---

### Edge Case 3: Context Window Overflow

**Scenario:** You ask Pro to read a 5000-line file with 100+ functions and refactor everything. Pro's context window is 131K tokens (~100K words).

**What happens:** LiteLLM auto-falls back to `.INIT/Air` (the 35B model, 256K context). But Air has weaker reasoning. The refactoring quality drops.

**How to avoid:** Break large tasks into pieces. "Refactor the auth functions in this file" is better than "Refactor this entire 5000-line file." The system also knows to use Air for large-file reading and Pro for targeted implementation.

---

### Edge Case 4: Task Requires Clarification Mid-Workflow

**Scenario:** You trigger a workflow for a complex migration, and mid-execution, an agent discovers the migration pattern is ambiguous (e.g., the old image tag appears in two different formats).

**What happens:** Workflows can't ask for mid-run clarification. The agent reports the ambiguity, and the workflow either skips the ambiguous item or marks it UNCERTAIN. You see these in the final report.

**How to avoid:** Be precise about patterns in your prompt. If there's ambiguity you know about, describe it upfront: "The old tag appears as both `berriai/litellm:latest` and `litellm:latest` — migrate both."

---

### Edge Case 5: Workflow Runs Out of Token Budget

**Scenario:** You set a token budget (e.g., `+500k`), and a heavy workflow hits the cap mid-execution.

**What happens:** The workflow stops. Completed agents' results are preserved. You see a message: "Token budget reached. N phases completed, M remaining."

**How to handle:** Resume with a higher budget, or narrow the scope. The workflow picks up from where it stopped (cached results for completed agents).

---

### Edge Case 6: Task Is Too Small for a Workflow

**Prompt:**
```text
Run a workflow to fix the typo "recieve" in the README
```

**What happens:** The system recognizes this is trivial and tells you: "This is a single-file typo fix. I'll handle it inline — no workflow needed." It then fixes it with one direct edit.

**Lesson:** You can always ask for a workflow, but the system won't waste resources when a task doesn't need one.

---

### Edge Case 7: Mixed Local + Cloud Models

**Scenario:** A workflow uses Flash (external API) + Pro (local GPU) + Ultra (external API).

**What happens:** Flash agents run in parallel (external APIs handle concurrency). Pro agents serialize automatically. Ultra runs when needed. The orchestrator handles this coordination — you don't need to manage which model runs when.

**Cost note:** Flash is cheap, Pro is free, Ultra is moderate. A mixed workflow like this typically costs $0.10–0.30 in API fees total.

---

## Prompt Cheat Sheet

| You Want To... | Prompt Template |
|----------------|-----------------|
| Fix a bug | `"Fix <problem> in <file>. It started after <context>."` |
| Add a feature | `"Add <feature> to <area>. It should <behavior>. Follow <reference>."` |
| Understand something | `"How does <thing> work? I'm trying to <goal>."` |
| Audit codebase | `"Audit <area> for <issue>. Check every <file type>."` |
| Migrate pattern | `"Migrate <old> to <new> across <scope>. Rules: <rules>."` |
| Review changes | `"Review the changes in <branch/PR>. Focus on <area>."` |
| Research externally | `"Research <topic>. Find N examples. Summarize approach and pitfalls."` |
| Full codebase sweep | `"Run a workflow to sweep <scope> for <issue> and fix each one."` |

---

## Next Steps

- [Prompt Engineering](prompt-engineering.md) — the mechanics of writing effective prompts
- [Workflows](workflows.md) — deep dive on when and how to use multi-agent orchestration
- [Home](index.md) — back to the usage overview
