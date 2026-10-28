# Phase-1A-3N Synthetic Results

Run SHA: branch `phase1a-phase3n-endogenous-credit`; data
`results/phase1a3n/endogenous_battery.json` (420 runs = 6 scenarios ×
7 estimators × 10 seeds). Zero LLM; zero MetaBox; zero test split.

## Mean regret (↓) / opt-ID (↑) — highlights

| scenario | bucket_ucb | quality_residual | ipw | dr | raw_ucb | oracle |
|---|---|---|---|---|---|---|
| A no confound | 23.7 / .57 | 23.8 / .57 | **8.0** / .80 | 30 / .48 | 19.7 / .64 | 0 / 1 |
| B state | 22.2 / .48 | 22.7 / .47 | **15.8** / .60 | 23.6 / .48 | 20 / .55 | 0 / 1 |
| **C endogenous q** | 14.29 / .40 | **13.96 / .41** | 18.3 / .15 | 15.0 / .37 | 12.8 / .44 | 0 / 1 |
| D near tie | 1.19 / .33 | 1.19 / .34 | 1.08 / .36 | 1.20 / .33 | 1.21 / .33 | 0 / 1 |
| E no support | 32.0 / .61 | 32.3 / .60 | **13.4** / .81 | 25.6 / .65 | 25.1 / .69 | 0 / 1 |
| F drift | 36.8 / .57 | 38.6 / .55 | 26.1 / .69 | **21.4 / .74** | 30.2 / .64 | 0 / 1 |

## Paired W-L-T vs bucket_ucb (10 seeds)

| scenario | quality_residual | ipw | dr |
|---|---|---|---|
| A | 4-6-0 | **10-0** | 2-7-1 |
| B | 3-7 | **10-0** | 1-9 |
| **C** | **7-3** | 0-10 | 3-7 |
| D | 5-5 | **10-0** | 4-6 |
| E | 4-6 | **10-0** | **10-0** |
| F | 0-10 | **10-0** | **10-0** |

## Gate evaluation

| gate | verdict | evidence |
|---|---|---|
| C improvement with statistical support | **WEAK PASS** | quality_residual 7-3 (p≈0.17 binom) and mean ↓2.3% only |
| No unacceptable loss on A | **BORDERLINE** | quality_residual 4-6, mean equal; IPW 10-0 better |
| Support-set rejection on E | **FAIL** | `refused=0`; estimators chose freely; e=0 cells not forced through refusal path |
| Repeatable correct-direction ranking diff | **WEAK** | C direction correct for quality_residual; effect small |

## Mechanism checks

1. **Different ranking from bucket UCB?** Yes for quality_residual on C
   (7-3) and for IPW/DR on B/E/F. Not equivalent overall.
2. **Closer to true optimal?** quality_residual slightly on C; IPW strongly on
   A/B/D/E (unexpected — variance/clip effects dominate); DR on F (drift).
3. **Why:** quality residual removes q-mix inside buckets; IPW's high variance
   hurts C where propensity correlates with q; DR's LOO outcome model adapts
   to drift (F).
4. **Ablations not yet run** (shuffle q / e, drop residual): listed as required
   follow-up before any novelty claim.
5. **No-support handling not exercised** — design gap (see protocol limits).

## Honest summary

The only scenario that motivates quality residualization (C) shows a **small,
only weakly supported** gain. IPW/DR win elsewhere for variance/drift reasons
unrelated to the quality-confound story. **No method robustly dominates.**
