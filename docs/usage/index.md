# Using .init

`.init` is an AI-augmented software engineering system. You describe what you want — it discovers, plans, implements, and verifies. This page defines the contract: what the system handles, what you provide, and how the two work together.

---

## The Division of Labor

The system doesn't read your mind. It reads your prompt, your codebase, and your project's `CLAUDE.md`. Everything it does flows from what you tell it.

| Responsibility | Yours | The System's |
|----------------|-------|--------------|
| Define **what** to build or fix | ✅ You | — |
| Explain **why** (context, constraints) | ✅ You | — |
| Decide **how** to implement | — | ✅ System |
| Discover which files are involved | — | ✅ System |
| Choose the right model for each step | — | ✅ System |
| Write the actual code | — | ✅ System |
| Verify the changes are correct | — | ✅ System |
| Approve or reject the result | ✅ You | — |
| Set API keys, model paths, profiles | ✅ You | — |
| Keep secrets out of the repo | ✅ You | — |

**The golden rule:** be specific about the outcome, not the implementation. "Add rate limiting to the LiteLLM proxy" is good. "Edit line 42 of config.yaml to add a `rpm` field" is not — you're doing the system's job.

---

## What the System Does Automatically

When you send a prompt, the system goes through a decision process before writing a single line of code:

```text
Your Prompt
     │
     ▼
┌─────────────────────────┐
│ 1. Classify the task    │  ← Trivial? Simple? Multi-file? Audit? Migration?
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ 2. Pick execution mode  │  ← Inline (1 agent) vs Workflow (many agents)
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ 3. Assign models        │  ← Flash for discovery, Pro for code, Ultra for planning
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ 4. Execute              │  ← Discover files → Plan architecture → Implement → Verify
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ 5. Report back to you   │  ← Summary of what changed and why
└─────────────────────────┘
```

You don't need to know which model does what — the system routes automatically. But understanding the fleet helps you write better prompts, so here's a quick reference:

| Model | What It's Best At | Cost |
|-------|-------------------|------|
| **.INIT/Flash** (DeepSeek-V4-Flash) | Finding files, searching patterns, reading docs, web research | ~$0.04 per 100K tokens |
| **.INIT/Pro** (DGX Qwen3.6 27B) | Writing code, refactoring, precise implementation — **the implementer** | Free (local GPU) |
| **.INIT/Ultra** (DeepSeek-V4-Pro) | Architecture decisions, complex planning, multi-file orchestration | ~$0.15 per 100K tokens |
| **.INIT/Air** (DGX Qwen3.6 35B) | Reading very large files, mechanical scans, cross-referencing | Free (local GPU) |

---

## Two Execution Modes

### Inline Mode (default)

For simple tasks — single-file edits, quick questions, well-defined changes. The orchestrator spawns 1–3 agents directly and reports back. Fast, cheap, conversational.

**Best for:** bug fixes, config changes, adding a function, asking about the codebase.

### Workflow Mode (triggered)

For complex tasks — multi-file changes, codebase audits, migrations, research. The system writes an orchestration script that fans out work across many agents, verifies findings, and returns a synthesized result. Takes longer, uses more tokens, catches more.

**Trigger it:** include the word "workflow" in your prompt, or describe a task that's clearly large-scale ("audit every endpoint", "migrate all configs", "review the entire codebase").

**Best for:** security audits, mass migrations, multi-file features, exhaustive reviews.

Read [Workflows](workflows.md) for the full guide.

---

## Your First Five Minutes

```bash
# 1. Start the stack (first time only)
cp .env.example .env
cp .env.secrets.example .env.secrets
# Edit both files with your paths and keys
docker compose --env-file .env --env-file .env.secrets up -d

# 2. Launch Claude Code through the proxy
./claude-code.sh

# 3. Ask a question
# "What does the LiteLLM config do?"
# "Show me how retry policies are set up"
# "Add a health check to the llama.cpp service"

# 4. Run your first workflow
# "Run a workflow to audit the observability config for missing scrape targets"
```

That's it. The system discovers your codebase structure from `CLAUDE.md` and the file map. You don't need to point it at files — describe the task and it finds them.

---

## What a Good Prompt Looks Like

```
❌ BAD:  "Fix the config"
         → Too vague. System doesn't know which config or what's wrong.

❌ BAD:  "Edit observability/config/config.alloy line 47 to add a label"
         → Too specific. You're micromanaging the implementation.

✅ GOOD: "Add a hostname label to all scrape targets in the Alloy config,
         following the existing label conventions. The label should use
         the HOSTNAME env var."
         → Clear outcome, context, and constraints. System handles the how.
```

Read [Prompt Engineering](prompt-engineering.md) for the full guide with examples.

---

## What You Must Provide

The system needs three things to work well:

### 1. A clear description of the outcome

Say what you want, not how to do it. Include any constraints ("must work on ARM64", "don't change the port", "keep backward compatibility with the 27B model").

### 2. Context that matters

If your task depends on something the system can't discover from the codebase — a future plan, a production constraint, a known limitation — say it. The system reads `CLAUDE.md` and your files, but it doesn't know what happened in yesterday's incident call.

### 3. Approval

The system will show you what it plans to do (or what it did). Review it. If something looks wrong, say so — the system iterates. You're the final gate.

---

## What You Must NOT Do

- **Don't hardcode secrets.** The system won't either. Reference env vars, never paste keys.
- **Don't micromanage line numbers.** Describe the outcome. The system handles file discovery.
- **Don't run two Pro tasks at once.** The local GPU model handles one request at a time. The system serializes automatically in workflows, but if you're spawning agents manually, go one at a time.
- **Don't expect the system to know what you didn't say.** It can't guess your preferences, your team's conventions, or your deployment constraints unless you tell it.

---

## Next Steps

- [Prompt Engineering](prompt-engineering.md) — learn to write prompts that get the right model for the job
- [Workflows](workflows.md) — understand when and how to use multi-agent orchestration
- [Examples](examples.md) — real prompts and their outcomes
