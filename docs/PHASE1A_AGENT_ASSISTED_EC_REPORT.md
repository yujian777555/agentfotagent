# Phase-1A Agent-Assisted EC Report

- Branch: `phase1a-agent-assisted-ec-experiment`
- Code SHA at train run: `1fc40335619e51693ba048b8accdd0ab8e6a8479`
- Train manifest: `results/agent_assisted_ec/manifest_a2-1fc40335619e-clean-20261028T111308.json`
- Validation: `results/agent_assisted_ec/validation_a2.json`
- Model: `deepseek-flash` · proposals 9 requests / 12 budget (3 legal distinct mechanisms)

## Frozen negative result (P1A-1D/E)

LLM-direct per-generation F/CR control: `REJECTED_FOR_CURRENT_PROTOCOL`.
Not re-run this phase.

## Agent proposals (from real train trajectories)

| id | diagnosis (abridged) | mechanism (abridged) |
|---|---|---|
| agent_mech_1 | premature convergence under rand/1 | stag≥5→rand/2; stag≥20→current-to-best; div<30→inject; succ<0.15→F=0.8 |
| agent_mech_2 | low diversity, lack of progress | stag≥5→inject; div≤30→rand/2 |
| agent_mech_3 | persistent stagnation (stag up to 160) | stag≥5→rand/2; div≤30→inject_diversity |

3/3 statically valid, executable on multi-operator DE (rand/1, current-to-best/1,
rand/2, best/1 + inject_diversity). Fail-closed DSL (tests in
`tests/test_agent_assisted_ec.py`).

## Train results (split_v2 train F1/F10/F20 × seeds 11/22, 300 FE, lower better)

Median: agent_mech_3 **1.4e3** · random_mech_3 1.4e3 · det_heuristic 2.3e3 ·
fixed_classic 3.5e5 · official 3.8e5 · SHADE 6.7e5 · shuffled 2.6e5

**agent_mech_3 paired W-L-T (train):**

| opponent | W-L-T |
|---|---|
| official_meta_de | **6-0** |
| SHADE | **6-0** |
| fixed_classic_de | **5-1** |
| shuffled_map | **5-1** |
| random_mech_3 | 4-2 |
| deterministic_heuristic | **3-3** |

Ablations: removing diversity rule from mech_1 changes nothing on these runs
(threshold 30 rarely met); mech_3's `inject_diversity` (div≤30) drives the F20
wins. Shuffled map loses to mech_3 (5-1) on train.

## Validation (split_v2 val F13/F16/F22 × seeds 11/22)

| comparison | W-L-T | verdict |
|---|---|---|
| agent_mech_3 vs fixed_classic | **4-0-2** | positive |
| agent_mech_3 vs deterministic heuristic | **1-3-2** | **loses** |
| agent_mech_3 vs random_mech | **2-2-2** | **tie** |

F22 all arms identical (86.565…): function saturates at this budget.

## Hypotheses

- **H1** (mechanism improves over fixed DE and deterministic heuristics):
  train: partial (3-3 vs det). **validation: NOT supported** (1-3 vs det).
- **H2** (reproducible benefit on independent validation): **NOT supported**.

## Decision

**`NO_BENEFIT` on validation. Do NOT proceed to Phase-1B.**

Evidence-based reading:
1. Agent can propose legal, executable, state-conditioned mechanisms (positive).
2. train gains vs official/SHADE/fixed are real but **not better than a simple
   deterministic stagnation heuristic** on validation.
3. random_mech ties agent on validation → cannot claim Agent *discovery*.
4. Same budget, FE exact, function identity verified; not a budget artifact.

Next (not executed here): harden mechanisms (e.g. diversity thresholds
calibrated to observable scales), add seeds/functions before any Phase-1B,
or stop H1/H2 if validation keeps failing. Do not retune on val/test to
manufacture wins.

## Budget & integrity

- API: 9 requests, 16461/4048 tokens, 0 failures, cost not returned by API.
- FE exact on all controlled runs (`independent_fes == fes == 300`).
- P1A-1B..E artifacts untouched.
- No MetaBBO meta-training, no AES transfer, no test-split access.
