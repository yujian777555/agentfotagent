# Phase-1A-4R3 Decision

## Pre-registered rules applied

- **Random matching contract failed** (0/120; k_state≈270 vs ~48 feasible slots)
  → **实验无效 for the timing question** per rule 7.
- Observed NI_state vs L-SHADE = **3-107-10** (0/12 functions won) → even
  setting aside matching, N+I at this trigger rate does **not** beat L-SHADE.
- Literature (4R3 audit): restart+SHADE **ALREADY_COVERED** (R-SHADE/RL-SHADE);
  ARRDE covers dynamic-N+restart. No novelty claim possible.

## Verdict

**`NO_GO` — stop the N+I restart-operator line on L-SHADE.**

Reasons:
1. Random-matched comparison unexecutable at observed event rates.
2. State-triggered N+I actively harmful (3-107) — over-triggering with
   near-zero effective shrinks (8/280) = immigrant noise.
3. Mechanism family already covered by R-SHADE/RL-SHADE/ARRDE.

## Closed

- N+I restart as a claimed improvement on L-SHADE (current definition).
- State-timing contribution (already closed in 4R2).
- Memory-reset / stall-detector claims (closed in 4R).
- CC-SOC / quality-credit line (closed in 3N2).

## Open (if project continues)

- Honest **reproduction** of R-SHADE/RL-SHADE on MetaBox (no novelty claim).
- Or move to a different EC mechanism with verified literature gap.
- Agent contribution to date: **none validated** (0 LLM across 3N2/4/4R/4R2/4R3).

## Evidence

- code `2f13d24beb27…` · results `results/phase1a4r3/manifest_a4r3-2f13d24beb27-clean-20261028T193948.json`
- tests `tests/test_phase1a4r3.py` 4 passed · suite green
- 600 runs · 10k FE · FE exact · 0 LLM · train-only
