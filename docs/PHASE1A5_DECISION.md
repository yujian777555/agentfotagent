# Phase-1A-5 Decision

## Verdict

**`NO_GO_NEW_MECHANISM`** — stop this phase without running the 144-run pilot.

## Why

1. Stage A (3 real deepseek-flash requests) converged on one mechanism:
   progress-adaptive N(t) replacing linear population reduction.
2. Stage B (3 independent adversarial reviews) **unanimously REJECT** it as
   already covered by jSO/AP-SHADE/stagnation-gated variants — a reparameter-
   ization, not a new mechanism.
3. Per pre-registered stop rules: no passing candidate ⇒ no pilot; do not
   force an experiment or re-prompt the model for different answers.

LLM budget used: 6/6 requests (3 propose + 3 critique), `deepseek-flash`
only, thinking disabled, JSON mode. Prompts frozen before calls; no post-hoc
candidate regeneration after seeing pilot results (no pilot ran).

## What remains credible

- The **defect observation** is real and useful: linear N(t) is decoupled from
  progress (F1 converges ~1500 FE while N collapses; F10 still improving at
  N=4). This is documented in `results/phase1a5/lshade_trajectory_summary.txt`.
- The **remedy space is already populated** (adaptive-N literature). A
  contribution would need either a new measurable gap beyond progress-gating,
  or a reproduction/analysis of adaptive-N vs linear-N — honest work, but not
  a new-algorithm claim.

## Closed lines (updated)

- CC-SOC / quality credit — closed (3N2)
- DPR-SHADE state triggers / N+I restarts — closed (4R, 4R2, 4R3)
- Progress-adaptive N(t) as a **novel mechanism** — closed (5)

## Agent contribution evidence

- Stage A produced three non-trivial, evidence-linked candidates converging
  independently — shows the LLM can generate mechanism hypotheses from traces.
- Stage B correctly rejected the renaming risk — the critique loop works.
- **Net claimable contribution: hypothesis generation + adversarial filtering
  process**, not a validated algorithmic improvement. No performance claim.

## Next

Return to broader EC-mechanism search for a master's-level method with a
verified literature gap (e.g., honest reproduction studies of adaptive-N,
or a different mechanism family entirely). Agent stays as hypothesis/diagnosis
tool; any future LLM-in-loop method needs a hand-designed control and a
random-change control before any novelty claim.
