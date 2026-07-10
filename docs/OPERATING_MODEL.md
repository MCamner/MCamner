# Operating model

The MQ stack turns local technical work into structured signal, reviewable action, and reusable knowledge.

```text
endpoint / repo / screenshot / workflow
→ structured signal
→ scored readiness
→ explained risk
→ reviewed action
→ release or policy gate
→ durable technical memory
→ better next action
```

## Principles

1. **Signal before action.** Collect evidence, score the state, and explain risk before changing anything.
2. **Local execution.** Work against real files, repositories, and endpoint signals from the operator's machine.
3. **Human-reviewed automation.** AI can inspect and propose; critical actions remain gated and reversible.
4. **Explicit safety.** Tool execution should be policy-bound, logged, and predictable.
5. **Durable memory.** Decisions, failures, fixes, and release results should improve the next work session.

## Operational loop

```text
terminal
→ mqlaunch
→ mq-agent sweep
→ repo-signal readiness scores
→ review, alerts, and blockers
→ release gates
→ mqobsidian decision record
```

This is designed for environments where endpoints, identity, certificates, client software, and infrastructure must align—not merely look correct in isolation.

[Back to profile](../README.md)
