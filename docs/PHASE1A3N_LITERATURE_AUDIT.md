# Phase-1A-3N Literature Audit (targeted continuation)

Scope: parent-quality correction and propensity/DR credit in evolutionary
operator selection. Continues `PHASE1A3R_TARGETED_LITERATURE_AUDIT.md`.

## Checks performed

| question | finding | evidence |
|---|---|---|
| state-conditioned AOS / contextual bandits in EC | covered in essence; bucketed UCB is standard contextual bandit | PARTIAL (Fialho-line + survey-level) |
| parent-quality residualization in AOS | **not found** in searched EC-AOS titles/abstracts | SECONDARY — absence unproven |
| logged propensity / IPW / DR in EC AOS | **not found** under those names in EC-AOS | SECONDARY — causal bandits (Dudik et al., Kallus etc.) cover the math in ML |
| LLM-driven AOS credit (LAOS) | abstract only; credit formula unverified | SECONDARY |

## Overlap risk

The DR estimator we implement is standard causal-bandit machinery
(outcome model + IPW, cross-fit). Applying it to EC operator credit may be
novel *as an application*, not as an estimator. Any paper claiming “new
estimator” would be wrong. An honest framing would be **empirical evaluation
of off-policy credit estimators inside AOS**, which is Path R-adjacent.

## Conclusion

Even if Path N2 shows gains, the mathematical core is not new. Combine with
weak synthetic support → supports `NO_GO` for new-algorithm claim;
empirical study remains viable.

**Grade warning:** full method texts of the nearest state-aware AOS papers
were not obtained this session; re-verify before any write-up that uses the
phrase “no prior work”.
