# Phase-1A-4R2 Decision

## Pre-registered rule applied

> 若 NI_state 优于 baseline，但不优于精确匹配的 NI_random_matched：
> 只保留 N+I 重启算子候选，关闭状态触发创新主张。

Evidence: NI_state beats baseline 8-1 (clear), but vs **exactly matched**
NI_random_matched only **5-4**, losing on F1 and F20 (winning only F10).
Not a stable timing advantage.

## Verdict

**Retain N+I restart operator as a candidate. Close state-trigger novelty
claims (`NO_GO` for "state timing is the contribution").**

- N+I vs baseline: 8-1 → restarts help (both state and random).
- State vs matched-random: 5-4 mixed → **timing value unproven**; F10-only
  signal is not enough with 3 seeds.
- Memory reset M: closed (4R).
- Stall detector: closed (0 independent fires across 112 events).

## Scope of allowed next work

- Honest empirical line: **restart-style N+I vs linear N(t) / L-SHADE** on
  longer budgets or harder functions, with matched-random as mandatory control.
- If that shows gains, Agent may later propose restart *policies* — but the
  timing/state story is not the novelty.
- No 2000-FE formal run; no Phase-1B; no threshold tuning on these results.

## Evidence

- code `8abc8b6f0169…` · failed first run preserved (`a4r2-1aa651ffda3f…`)
- results `results/phase1a4r2/manifest_a4r2-8abc8b6f0169-clean-20261028T163406.json`
- tests `tests/test_phase1a4r2.py` 4 passed (exact-count contract)
