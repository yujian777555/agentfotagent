# Phase-1A Protocol — Agent-Assisted Evolutionary Computation on MetaBox-v2

Status: **PROTOCOL DRAFT / NO LIVE-LLM RUN AUTHORIZED**. This is the next source-domain validation gate after Phase-0 R4. It is not a novelty claim or a confirmation that the method works.

## 1. Research question

Can an Agent that diagnoses real evolutionary-search trajectories propose constrained, executable controller revisions that improve black-box optimization performance beyond strong conventional adaptive optimizers and fair non-diagnostic policy-search controls?

This is a prerequisite gate for the larger project. It does not, by itself, establish cross-domain transfer to AES. The previous source-prior→AES pilot is NO_GO_OR_PIVOT and must not be scaled.

## 2. Platform and reproducibility

- Platform: official MetaBox-v2, repository/tag and exact resolved commit recorded in every run.
- Official entry points: https://github.com/MetaEvo/MetaBox/tree/v2.0.0 and https://metaboxdoc.readthedocs.io/en/stable/
- Reference paper: https://arxiv.org/abs/2505.17745
- Do not use an unpinned `main` checkout for results. Record Python, dependency lock, MetaBox commit/version, OS, device, and all configuration hashes.
- First inspect the installed MetaBox API and available baselines. Do not assume a class or config key exists: verify it from the pinned source and run a minimal integration smoke test.

MetaBox-v2 describes 18 problem sets, 1,900+ instances, and broad support for traditional and MetaBBO baselines. This project uses MetaBox as standardized infrastructure, not as a contribution.

## 3. Candidate method hypothesis (not yet a novelty claim)

Prototype a **trajectory-diagnosis-guided controller proposal loop** for a Differential Evolution (DE) optimizer:

1. Collect a bounded, structured summary of actual search trajectories: normalized improvement over a recent window, stagnation length, population diversity/spread, successful-offspring fraction, and consumed function-evaluation budget.
2. Ask the Agent to diagnose a specific failure mode and propose a minimal intervention with an explicit prediction. Example intervention types: choose among supported mutation strategies, alter a bounded `F`/`CR` range, or trigger a constrained restart.
3. Require the Agent to return a strict JSON policy in a typed controller DSL. No arbitrary generated Python, shell commands, or unvalidated code execution.
4. Compile the policy with a deterministic validator; reject unknown fields, illegal actions, out-of-range parameters, and rules that inspect hidden optimum/function identity/test labels.
5. Evaluate the policy through the same MetaBox problem/evaluation path as all baselines. Keep complete lineage: diagnosis → proposed rule → compiled policy hash → run IDs → scores.
6. Use evolutionary selection to retain/promote policy candidates under a fixed evaluation budget. The Agent is a constrained proposal/diagnosis mechanism; it does not replace the evolutionary algorithm or evaluator.

The candidate scientific mechanism is the **evidence-conditioned, typed intervention loop** (diagnosis + falsifiable expected effect + constrained compilation + evolutionary selection), not merely “an LLM chooses an operator.” Before a paper claim, compare it against the closest related LLM-assisted EC and adaptive-operator-selection methods and be willing to abandon this mechanism if the distinction is not defensible.

## 4. Task split and leakage prevention

- Initial suite: BBOB-10D, provided the pinned MetaBox version supports it as documented.
- Split by function/problem identity, not just by random seed: 12 train functions, 6 validation functions, 6 held-out test functions. Stratify by documented function category if the platform exposes category metadata.
- Freeze exact function IDs, instance IDs, seeds, split hashes, and exclusions before Agent proposals are generated.
- Train functions may be used to propose and evolve policies; validation functions may be used for model/policy selection; held-out test functions are used only once for final evaluation.
- Do not put function ID, optimum, hidden benchmark labels, or held-out scores in the Agent-facing trajectory summary.
- If BBOB-10D does not expose the required metadata or split granularity in the pinned MetaBox version, stop and document the mismatch before inventing a split.

A noisy BBOB set or a second dimension may be a secondary generalization check after the main protocol is stable, not a substitute for the frozen primary test.

## 5. Baselines and controls

Inspect the pinned MetaBox implementation and select baselines that actually support the chosen problem suite. At minimum, aim for:

1. A fixed conventional DE baseline using the same allowed action set.
2. A strong self-adaptive DE baseline such as SHADE, if supported by the pinned release.
3. A strong general-purpose optimizer such as CMA-ES, if supported and comparable under the chosen FE budget.
4. A built-in MetaBBO baseline such as GLEET, if it can be run fairly on the same task family and budget.
5. **Random-controller search** over the exact same typed controller DSL.
6. **Agent without trajectory diagnosis**: same model, output schema, and proposal budget, but only a generic task/controller description.
7. **Agent with trajectory diagnosis**: full proposed method.
8. Optional shuffled-diagnosis or shuffled-state/action mapping as a negative control if the control remains semantically valid.

Do not claim a fair comparison if an algorithm uses a different objective-evaluation budget, problem split, or stopping condition. If a named baseline is unavailable, document the exact reason and select a verified substitute before the formal run.

## 6. Metrics and budget

- Use the same objective-evaluation/FE budget across comparable optimizers; log wall time separately.
- Before confirmation, inspect MetaBox's official metrics for the chosen suite and select one primary metric with a clear direction. Also record anytime performance, final objective/normalized regret where valid, success/target-hit rate if meaningful, function evaluations, runtime, and variance across seeds.
- Do not select a metric after looking at held-out results.
- Report per-function and aggregate results, not only the best run.
- Report Agent proposals, rejected proposals, controller hashes, model/version, calls, input/output tokens, estimated/actual cost, and failures.

## 7. Execution stages

### P1A-0: no-LLM integration smoke (authorized)

- Pin MetaBox-v2 and record the exact source commit.
- Run one supported problem and one conventional baseline end-to-end.
- Verify objective direction, FE accounting, trace capture, metric calculation, seed determinism, and output reconstruction.
- Verify at least two fixed typed controllers can be compiled and executed through the actual MetaBox path.
- This is engineering evidence only; do not report it as Agent-assisted EC performance.

### P1A-1: low-cost Agent pilot (requires a model source and explicit budget)

- Use a small, predeclared subset of train functions and seeds.
- Compare fixed baseline, random-controller search, Agent-without-diagnosis, and Agent-with-diagnosis.
- Freeze a small proposal/FE budget before execution. A pilot is for checking whether the method produces legal, distinct policies and a directional signal; it is not confirmatory.
- If a suitable local model is available, record exact model weights/version and inference configuration. Otherwise, request explicit approval for the live API call/token/cost cap before any API calls. Do not substitute the hand-written AES source prior and do not fabricate Agent outputs.

### P1A-2: confirmatory evaluation (only if pilot is informative)

- Freeze protocol, baseline versions, seeds, task split, FE budget, analysis script, exclusion rules, and stop/go criteria before running.
- Evaluate on train/validation as specified; use held-out functions only for final reporting.
- Require reproducible improvement over the strongest applicable baseline and over the no-diagnosis control. If gains disappear on held-out functions, are within noise, or only appear on one function, record NO-GO/PIVOT.

## 8. Go/no-go rules

**GO to Phase-1B transfer only if all are true:**
- the Agent produces legal, behaviorally distinct controller policies from real search traces;
- the full run is reproducible from commit/config/seed/manifest artifacts;
- the proposed method beats the strongest applicable conventional baseline and the no-diagnosis control on the predeclared primary metric across the held-out function set, with uncertainty reported;
- the advantage is not explained by extra function evaluations, different budgets, or hidden test leakage;
- the difference from prior LLM-assisted EC/AOS methods is defensible after related-work review.

Otherwise, keep the negative result and pivot. Do not proceed to cross-domain transfer merely because the pipeline runs.

## 9. Required artifacts

- `docs/PHASE1A_METABOX_PROTOCOL.md` (this protocol, updated only before confirmation begins)
- exact MetaBox commit/version and dependency lock
- `configs/phase1a_*.json` with hashes
- frozen train/validation/test manifest with function IDs and seeds
- typed controller schema/compiler and adversarial schema tests
- baseline adapter and integration tests
- raw trajectories, FE accounting, per-run metrics, and controller lineage
- pilot report and go/no-go decision under `docs/` and `results/phase1a/`

## 10. Approval boundary

No live LLM API calls, cloud GPU jobs, or paid inference are authorized by this document. Before such runs, record the model, call/token cap, maximum cost, retry policy, and stop condition, and obtain explicit user approval. Local no-LLM MetaBox smoke tests and protocol implementation may proceed immediately.
