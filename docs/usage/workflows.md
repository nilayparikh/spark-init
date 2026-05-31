# Workflows

Dynamic workflows are how `.init` handles complex, multi-file, codebase-scale tasks. Instead of one model working through your request sequentially, the system writes an orchestration script that fans out work across dozens of agents — each using the right model for its job, each working in an isolated context, with adversarial verification before results reach you.

---

## When to Use a Workflow

Workflows are for **scale**. If you can describe the task in one sentence and it touches one file, you don't need a workflow.

| Task | Use Workflow? | Why |
|------|---------------|-----|
| "Fix the typo in the README" | No | Single file, trivial |
| "Add a health check to the 27B service" | No | Single file, well-defined |
| "Audit every compose file for missing health checks" | **Yes** | Codebase-wide, needs fan-out |
| "Migrate all image tags from `latest` to pinned versions" | **Yes** | Many files, pattern-based |
| "Research how 3 different projects handle GPU passthrough" | **Yes** | Multi-source research |
| "Add rate limiting to LiteLLM" | Maybe | If it touches 3+ files, yes |
| "Review the PR for security issues" | No (inline) | Well-scoped, one reviewer can handle |

---

## How to Trigger a Workflow

### Method 1: The Keyword (Explicit)

Include `workflow` anywhere in your prompt. The system highlights the word and writes an orchestration script instead of working inline.

```text
Run a workflow to audit every API endpoint for missing auth checks
```

If Claude Code highlights `workflow` when you didn't intend it, press `Alt+W` to ignore.

### Method 2: Task Scope (Implicit)

Describe a task that's clearly large-scale. The system recognizes breadth signals:

```text
Sweep the entire codebase for hardcoded IP addresses and replace them
with environment variable references.
```

### Method 3: Ultracode (Automatic)

Set the system to decide for itself when a workflow is warranted:

```text
/effort ultracode
```

With ultracode on, every substantive task gets a workflow. Use this for long sessions of heavy work. Turn it off with `/effort high` when you return to routine tasks.

---

## What Happens When You Trigger One

### Step 1: The Plan

The system writes a JavaScript orchestration script. You'll see the planned phases before anything runs:

```text
┌─ Workflow: audit-health-checks ──────────────────────────┐
│ Phases:                                                   │
│  1. Discover — Flash agents scan all compose files        │
│  2. Deduplicate — merge overlapping findings              │
│  3. Verify — Pro agents confirm each finding              │
│  4. Report — Flash synthesizes final report               │
│                                                           │
│  Est. cost: ~$0.08                                        │
│                                                           │
│  [Yes, run it]  [View raw script]  [No]                   │
└───────────────────────────────────────────────────────────┘
```

Review the plan. If the phases don't match what you expected, say so — the system adjusts.

### Step 2: Execution

The run starts in the background. Your session stays responsive — you can keep working while agents run. Watch progress:

```bash
/workflows
```

The progress view shows each phase with agent counts, token totals, and elapsed time. Drill into any phase to see what each agent found.

| Key | Action |
|-----|--------|
| `↑` / `↓` | Select a phase or agent |
| `Enter` / `→` | Drill into details |
| `Esc` | Back out one level |
| `p` | Pause or resume the run |
| `x` | Stop the selected agent or whole workflow |
| `s` | Save the workflow as a command for reuse |

### Step 3: The Report

When the run finishes, the result lands in your session. For a code change, you'll see what was changed and why. For an audit, you'll get a findings report with verified issues. For research, you'll get a cited report.

---

## What's Happening Under the Hood

The workflow runtime executes the script in an isolated environment. Here's what a typical 4-phase workflow looks like internally:

```text
Phase 1: DISCOVER (parallel Flash agents)
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Scan     │  │ Scan     │  │ Scan     │
│ compose  │  │ config   │  │ CI       │
│ files    │  │ files    │  │ files    │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │              │              │
     ▼              ▼              ▼
  [all findings collected, deduplicated]

Phase 2: VERIFY (pipeline — Pro agents, one at a time)
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Verify   │ ──▶ │ Verify   │ ──▶ │ Verify   │
│ finding 1│     │ finding 2│     │ finding 3│
└──────────┘     └──────────┘     └──────────┘
  ⚠️ Serialized — DGX handles 1 request at a time

Phase 3: IMPLEMENT (pipeline — Pro agents, one at a time if applicable)
[Each confirmed issue → Pro implements the fix]

Phase 4: REVIEW (parallel Flash agents — adversarial)
┌──────────┐  ┌──────────┐
│ Review   │  │ Review   │
│ change 1 │  │ change 2 │
└────┬─────┘  └────┬─────┘
     │              │
     ▼              ▼
  [verified changes → your session]
```

### Key Behaviors

- **Context isolation** — each agent reads only what it needs. Intermediate errors and file dumps stay trapped in subagent contexts, never flooding your session.
- **Adversarial verification** — reviewers try to **refute** each finding before accepting it. A finding that can't be refuted is confirmed. This catches false positives.
- **Automatic serialization** — Pro and Air agents (local models) are automatically serialized. The system never sends two requests to the same local model simultaneously.
- **Resumable** — if you stop a workflow, you can resume it in the same session. Completed agents return cached results; the rest run fresh.

---

## Cost Expectations

Workflows use more tokens than inline work because they spawn more agents. Here's what to expect:

| Workflow Type | Typical Agents | Est. API Cost |
|---------------|---------------|---------------|
| Light (3–4 files) | 4–6 Flash + 1–2 Pro | ~$0.04–0.08 |
| Medium (10–20 files) | 6–10 Flash + 2–4 Pro + 1 Ultra | ~$0.10–0.20 |
| Heavy (codebase audit) | 10–20 Flash + 5–10 Pro + 1 Ultra | ~$0.20–0.50 |
| Research (web-heavy) | 5–8 Flash + 1 Ultra | ~$0.10–0.25 |

Pro and Air agents cost nothing (local GPU). Flash and Ultra agents cost API tokens. The system minimizes API cost by routing discovery to Flash (12x cheaper than Ultra) and implementation to Pro (free).

**To keep costs low:**
- Use Air instead of Flash for reading many local files (free vs paid)
- Don't trigger a workflow for single-file changes
- Review the plan before approving — if it looks excessive for your task, say so

---

## When NOT to Use a Workflow

Workflows are the wrong tool when:

| Situation | Why | What to Do Instead |
|-----------|-----|--------------------|
| Single file change | Overkill — one Pro agent is enough | Inline prompt |
| Quick question | No code change needed | Inline prompt |
| You're iterating rapidly | Workflow overhead per iteration slows you down | Inline, then workflow for final review |
| The task is ambiguous | The system needs to ask clarifying questions — workflows can't mid-run | Discuss inline first, then trigger the workflow |
| You need to approve each step | Workflows run autonomously. You see the result, not each intermediate decision | Break into separate prompts |

---

## Saving a Workflow for Reuse

If you run a workflow you'll need again (e.g., pre-commit review, release checklist), save it:

1. Run `/workflows`
2. Select the completed run
3. Press `s` to save
4. Choose location:
   - `.claude/workflows/` (project) — shared with your team in git
   - `~/.claude/workflows/` (personal) — available in all your projects

Saved workflows become slash commands: `/my-saved-workflow`. If a project workflow and a personal workflow share a name, the project one wins.

---

## Next Steps

- [Examples](examples.md) — real prompts with expected outcomes and edge cases
- [Prompt Engineering](prompt-engineering.md) — how to write prompts that trigger the right execution mode
- [Home](index.md) — back to the usage overview
