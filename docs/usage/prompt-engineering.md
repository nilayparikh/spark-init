# Prompt Engineering

How to write prompts that make the system route work to the right model, pick the right execution mode, and produce exactly what you need — first try.

---

## The Core Principle

The system reads your prompt and classifies the task. Everything flows from that classification. Write prompts that make the classification obvious.

```text
Your words  →  Task classification  →  Model routing  →  Result
```

If your prompt is ambiguous about scope, the system might use a single Pro agent when it should have spun up a workflow. If your prompt sounds trivial, you get a quick inline response when you wanted a thorough audit.

---

## Signal Words

Certain words and phrases push the system toward specific execution paths. Use them deliberately.

### Trigger a Workflow

Include any of these to signal "this is big enough for multi-agent orchestration":

| Signal | Effect |
|--------|--------|
| `workflow` | Explicit trigger — the system writes an orchestration script |
| `audit` | Implies exhaustive checking across many files |
| `sweep` | Codebase-wide scanning and fixing |
| `migrate` | Pattern-based changes across many files |
| `review the entire` | Full-codebase review with adversarial verification |
| `every endpoint / every file / all configs` | Signals breadth — system should fan out |

```text
✅ "Run a workflow to audit every Docker Compose service for missing health checks"
✅ "Sweep the codebase for hardcoded port numbers and replace with env vars"
✅ "Migrate all YAML configs from 2-space to 4-space indentation"
```

### Stay Inline

Use these patterns for tasks that should NOT trigger a workflow:

| Signal | Effect |
|--------|--------|
| `fix the bug in <file>` | Single file, well-defined |
| `add a <function> to <file>` | Scoped implementation |
| `what does <config> do?` | Question, not a change |
| `rename <X> to <Y> in <file>` | Mechanical, single location |

```text
✅ "Fix the retry count bug in interfaces/config/litellm/config.yaml"
✅ "What does the context_window_fallbacks setting do?"
✅ "Add a --verbose flag to the claude-code.sh launcher"
```

---

## How to Describe Scope

The system needs to know **how big** the task is. Be explicit about breadth.

### Scope Signals

| You Say | System Thinks |
|---------|---------------|
| "Check the LiteLLM config..." | Single file — inline Pro agent |
| "Review all provider configs..." | ~5 files — light workflow, Flash + Pro |
| "Audit every compose file..." | ~10 files — full workflow, Flash fan-out |
| "Scan the entire repo for..." | Hundreds of files — sweep workflow, Flash + AIR |

### Be Specific About Boundaries

```text
❌ "Review the configs"
   → Which configs? All of them? One directory? One provider?

✅ "Review the LiteLLM provider configs in interfaces/config/litellm/providers/
   for missing timeout settings"
   → Clear boundary. System knows exactly where to look.

✅ "Review every YAML file under observability/config/ for deprecated Grafana
   settings"
   → Scope is a directory. System can fan out Flash agents across files.
```

---

## How to Provide Context

The system reads your codebase, but it doesn't know everything you know. Add context that matters.

### What to Include

| Context Type | Example |
|--------------|---------|
| **Why this matters** | "We're seeing 401 errors in production after 30s of idle time" |
| **What must stay the same** | "Don't change any port numbers — they're hardcoded in our CI pipeline" |
| **What can change** | "The file structure can be reorganized as needed" |
| **Constraints** | "Must work on ARM64. The DGX doesn't have x86 emulation." |
| **Precedent** | "Follow the pattern used in the NVIDIA provider config" |
| **Known issues** | "The 27B model sometimes OOMs with context > 100K tokens" |

### What NOT to Include

| Don't Say | Why |
|-----------|-----|
| "Edit line 47 to..." | The system discovers files. You're overriding that. |
| "Use a for loop with..." | Trust the implementer. You're constraining the solution. |
| "First read X, then read Y, then..." | The system decides discovery order. |

```text
❌ "Open observability/config/config.alloy, go to line 120, and change
   the scrape interval from 15s to 30s"

✅ "Double the scrape interval in the Alloy config. We're hitting rate
   limits on the metrics endpoint and don't need 15s granularity."
```

---

## How to Constrain Cost

If you're mindful of API costs (Flash and Ultra are metered; Pro and Air are free), you can steer the system.

### Cost-Aware Prompts

| Concern | How to Signal |
|---------|---------------|
| "Keep it cheap" | "Use local models where possible. Only reach for Ultra if the architecture is genuinely complex." |
| "Cost doesn't matter" | "Use whatever models give the best result." (This is the default for workflows.) |
| "Quick answer only" | "Quick check — don't do a full audit. Just scan the main files." |
| "Budget cap" | "I want to stay under ~$0.10 in API costs for this." |

### Default Cost Behavior

The system is already cost-optimized by default:

| Phase | Model | Cost |
|-------|-------|------|
| Discovery (finding files) | Flash | Cheap (~$0.04) |
| Implementation (writing code) | Pro | Free |
| Architecture (planning) | Ultra | Moderate (~$0.15) |
| Mechanical scanning | Air | Free |

You only need to intervene if you want to override these defaults.

---

## Prompt Patterns (Quick Reference)

### Pattern 1: Fix Something

```text
"Fix <problem> in <location>. <context about why it broke>.
 <constraints on the fix>."
```

**Example:** "Fix the 401 error on the LiteLLM health endpoint. It started after we added the `require_auth_for_metrics_endpoint` flag. Don't disable auth — the fix should preserve authentication but allow health checks."

### Pattern 2: Add a Feature

```text
"Add <feature> to <area>. It should <behavior>.
 Follow the pattern in <reference file>. <constraints>."
```

**Example:** "Add a retry budget to the LiteLLM router config. It should cap total retries at 5 per minute per model. Follow the pattern in the existing `retry_policy` section. Must work with the DGX provider — it's the only one with timeout issues."

### Pattern 3: Understand Something

```text
"How does <system/feature> work? I'm trying to <goal>."
```

**Example:** "How does LiteLLM's context_window_fallbacks work? I'm trying to understand if the 27B model auto-falls-back to the 35B when it runs out of context."

### Pattern 4: Audit / Review

```text
"Audit <area> for <issue>. Check every <file type>. Report <what you want>."
```

**Example:** "Audit all Docker Compose files for services that don't have health checks. Check every docker-compose*.yml in the repo. Report the service name, file, and a suggested health check command."

### Pattern 5: Migrate / Sweep

```text
"Migrate <pattern> to <new pattern> across <scope>. <rules for the migration>."
```

**Example:** "Migrate all `docker.litellm.ai/berriai/litellm:latest` image references to use a pinned version tag. Scope is all compose files and docs. Skip the CI workflow files — those use a different pattern."

---

## Common Mistakes

### Mistake 1: Too Vague

```text
❌ "Make it better"
✅ "Reduce the LiteLLM proxy cold start time. It currently takes 30s on first
   request after docker compose up."
```

### Mistake 2: Too Prescriptive

```text
❌ "In interfaces/docker-compose.interface.yml, after line 85, add:
     -e LITELLM_LOG_LEVEL=DEBUG"
✅ "Enable debug logging for the LiteLLM service."
```

### Mistake 3: Missing the "Why"

```text
❌ "Change the retry count from 3 to 5"
✅ "Change the retry count from 3 to 5. We're seeing transient timeout errors
   on the DGX model under load, and 3 retries isn't enough to ride out
   the GPU warm-up period."
```

The "why" helps the system verify that the fix actually solves your problem.

### Mistake 4: Asking for Discovery in the Wrong Mode

```text
❌ "Search the entire codebase for every reference to 'port 8000' and tell
   me what you find"
   → This triggers an inline response, one model reading sequentially.

✅ "Run a workflow to find every reference to port 8000 across the entire
   codebase"
   → This fans out Flash agents in parallel, much faster for broad search.
```

---

## Next Steps

- [Workflows](workflows.md) — what happens when you trigger multi-agent orchestration
- [Examples](examples.md) — concrete prompts and their outcomes, including edge cases
- [Home](index.md) — back to the usage overview
