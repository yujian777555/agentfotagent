# Phase-1A-3R Experiment Gate

## Gate checklist

| # | condition | status | evidence |
|---|---|---|---|
| 1 | CC-SOC math free of unexplained equivalence | **FAIL** | baseline subtraction ≡ bucket UCB (max_diff 0.0) |
| 2 | synthetic experiment distinguishes method from nearest baseline | **PASS (as detector)** | detected exact equivalence |
| 3 | confound advantage not from budget/leakage | N/A | subtraction has no advantage |
| 4 | literature does not fully cover mechanism | **FAIL at current formula** | bucketed UCB = contextual AOS (`ALREADY_COVERED` risk); subtraction invalidated |
| 5 | Agent contribution identifiable or dropped | not reached | gate failed earlier |
| 6 | formal protocol frozen | drafted only | not admitted |

**Result: METHOD_REVISION_REQUIRED.** Formal experiment is **NOT** authorized.

## Decision

1. **Drop** “baseline subtraction” as any novelty. Current CC-SOC formulation
   is `CC_SOC_CURRENT_FORMULATION_INSUFFICIENT`.
2. **Two lawful paths** (choose before any formal run):
   - **Path R (replication/empirical):** study bucketed vs global AOS honestly
     as an empirical question (Scenario-B-like problems). No new-algorithm claim.
   - **Path N (new method):** implement quality-residualized + propensity-logged
     ε-greedy credit and **prove decision-ordering differences** vs raw UCB on
     constructed cases; then re-run this synthetic battery including an
     endogenous-assignment Scenario C. Only if that passes, literature-check
     again and freeze a formal protocol.
3. **NO_GO** on launching the previously drafted 2000-FE formal run with the
   current CC-SOC definition.

## If Path N is chosen — pre-registration skeleton (do not run yet)

- MetaBox BBOB-10D; train F1,2,4,6,7,10 / val F13,16,22 / test F19–21 after freeze;
  sealed [5,9,14,17,24] never touched in development.
- 2000 FE, NP=20, dim=10, 10 seeds; identical budgets.
- Arms: MetaBox DE, Fixed Classic, SHADE, PSM, raw UCB AOS, bucket UCB AOS,
  **N-CC-SOC (quality+propensity)**, shuffled-bucket control, oracle-ablation.
- Primary: regret W-L-T vs best baseline on ≥4/6 train functions.
- NO_BENEFIT: ≤3/6 vs SHADE or shuffled ≡ N-CC-SOC or quality/propensity
  ablations match (then mechanism reduces to known components).

## Next concrete step (budgeted)

Path N synthetic endogenous-assignment battery + one-page math proof of
ordering difference (estimated effort: 1 code session, **0 LLM requests**).
If that fails: record `NO_GO` and pivot to Path R empirical paper or stop.
