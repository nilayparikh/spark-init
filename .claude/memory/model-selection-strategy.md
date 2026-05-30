---
name: model-selection-strategy
description: When to use .INIT/Pro vs .INIT/Flash models and how to apply fanout strategy with subagents
metadata:
  type: user
---

## Model Selection Strategy

### `.INIT/Flash`
- Fast decoding speed, thinking model with vision support
- **Use for:** large context work, summarization, file segregation, broad searches, parallel fanout where speed matters
- Spawn Flash agents when you need coverage over many files quickly

### `.INIT/Pro`
- High intelligence, deep reasoning thinking model
- **Use for:** architecture decisions, complex refactors, debugging subtle bugs, design reviews
- Use Pro when correctness and depth matter more than speed

### Fanout Strategy

When orchestrating multiple subagents, match the model to the phase:

| Phase | Model | Why |
|-------|-------|-----|
| **Discover** | Flash | Scan wide, read many files, surface candidates — speed over depth |
| **Deep analysis** | Pro | Architectural review, implementation design, reasoning through trade-offs |
| **Verify** | Flash | Parallel checks across discovered findings — many independent validations |
| **Synthesize** | Pro | Combine findings into coherent plan or implementation |

**Rule of thumb:** Fan out Flash for breadth, escalate to Pro for depth.

### Practical Patterns

**Multi-stage workflow:**
1. Launch Flash agents to explore codebase and gather context
2. Feed Flash findings to a Pro agent for design/architecture decisions
3. Launch Flash agents again to verify Pro's conclusions against the code

**Parallel fanout:**
- Use Flash for 5+ parallel agents scanning different directories/files
- Reserve Pro for 1-3 agents doing deep reasoning on the same problem

**Cost-aware:**
- Default to Flash unless the task genuinely requires deeper reasoning
- Upgrade to Pro when a Flash agent hits a wall or produces uncertain results
