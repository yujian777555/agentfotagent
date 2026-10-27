# Phase-1A P0 Planner Review — 2026-10-27

## Verdict

**ACCEPTED AS A REAL-PLATFORM ENGINEERING SMOKE ONLY. REQUEST CHANGES FOR FULL P0 CLOSURE. P1A-1 IS BLOCKED.**

Reviewed Executor candidate: `phase1a-metabox-smoke@f571b52ba73f6cfcf51901a2af72f4b980699bc7`.

The core MetaBox integration evidence is credible and useful: the official DE path executes, the reported and independently wrapped FE counts agree at 1,500, the same seed reproduces the same curve, and changing the initial F setting changes outcomes. These results establish an engineering smoke, not an adaptive-controller result or Agent capability improvement.

The report claims 198 tests passed and one skipped locally. No GitHub Actions run was found for this feature branch, so this Planner review has inspected source and artifacts but has not independently reproduced the Windows runtime tests.

## Confirmed positives

1. **Source identity:** the cited upstream commit `5565a281ce4e03efc1f6a41230507d5b66637ace` contains `pyproject.toml` declaring `metaevobox==2.0.2`. The package-version/source-version pairing is plausible and internally consistent.
2. **Real optimizer path:** the smoke uses the upstream BBOB problem factory and DE episode rather than a local fake optimizer.
3. **Evaluation accounting:** all four reported runs have `independent_fes == reported_fes == 1500`.
4. **Determinism:** the artifact records identical curves, final costs and FE counts on repeated seed-33 runs for each fixed configuration.
5. **Scope discipline:** no LLM API was called; the report labels this as engineering-only and records the unsupported operator hooks instead of claiming scientific gains.

## Required corrections before any Agent pilot

### P0-R1-01 — Controller action names promise range behavior, implementation applies a scalar

In `experiments/metabox/adapter.py::_apply_action`, `set_F_range` sets `cfg.F` to the midpoint of `low/high`; `set_CR_range` similarly sets scalar `cfg.Cr` to the midpoint. Upstream DE reads scalar `config.F` and `config.Cr`. Therefore the tested arms are effectively fixed F=0.5 and F=0.9, not sampling or adapting within F ranges.

**Required:** either rename/version these actions as scalar actions (for example `set_F` and `set_CR`) and make the schema/report explicit, or implement genuine range semantics in a controlled optimizer loop and test the values actually consumed by DE. Do not silently retain the misleading range names.

### P0-R1-02 — The optimizer never feeds live trajectory state back into the controller

`run_optimizer` calls `controller.select_action` once, before the episode, with a constant initial state (`stagnation_steps=0`, `population_diversity=1`, `budget_fraction=0`, etc.). No generation/individual hook updates these features or asks for another action. The two controller runs therefore do not test trajectory-conditioned adaptation.

**Required:** before P1A-1, add an explicit and testable controller hook at a documented cadence (generation-level is a reasonable first version), compute features from observable search traces, and record every state/action event. Add tests proving that a crafted trace causes a rule to fire during the actual optimizer episode, not only in a standalone DSL unit test.

### P0-R1-03 — Mutation-strategy and restart actions are silently ineffective

The adapter writes `cfg.mutation_strategy` and `cfg.restart_max_fraction`, but the cited upstream DE implementation uses a fixed rand/1-style mutation expression and never reads either field. The schema can validate these actions, but validation does not make them operational.

**Required:** until an explicit controlled DE implementation supports and tests these actions, reject them at runtime with a clear unsupported-action error. Before Agent pilot, either implement the mutation/restart hooks in a project-owned controlled optimizer with documented upstream provenance, or remove those actions from the pilot action space. Add end-to-end tests for each action retained.

Upstream source reviewed: https://github.com/MetaEvo/MetaBox/blob/5565a281ce4e03efc1f6a41230507d5b66637ace/src/baseline/bbo/de.py

### P0-R1-04 — Frozen function split is not stratified

The current split is sequential: train F1–F12, validation F13–F18, test F19–F24. The pinned MetaBox BBOB implementation documents an easy/difficult grouping with difficult IDs `{1,2,3,5,15,16,17,21}`. Under the current split, the difficult counts are 4/12 train, 3/6 validation, and 1/6 test. Standard BBOB family groups are also distributed unevenly. The current split can confound controller performance with task-family distribution.

No Agent proposal or confirmatory run has occurred, so the split can be corrected now without contaminating results. Do not silently rewrite the old manifest.

**Required:** publish a versioned `split_v2` before Agent calls, preserving the v1 split and hash in the audit trail. A concrete stratified candidate that balances the MetaBox easy/difficult grouping and spans the five standard BBOB families is:

- train: `[1,2,4,6,7,10,11,12,15,18,20,21]`
- validation: `[3,8,13,16,22,23]`
- held-out test: `[5,9,14,17,19,24]`

Counts are 12/6/6; each split spans all five BBOB families, and the MetaBox difficult-set counts are 4/2/2. Verify the category mapping against the pinned source, write the exact family/difficulty labels into the manifest, and hash the complete manifest. This is a proposed split, not yet accepted until the Executor verifies it against the pinned environment.

### P0-R1-05 — Environment lock is a metadata record, not a complete dependency lock

`experiments/metabox/LOCK.json` records the MetaBox version/SHA and install commands but not the resolved transitive dependency versions or wheel/source artifact hashes.

**Required before formal runs:** record a complete resolved environment (for example, a committed `uv.lock` where supported, or a deterministic `pip freeze` plus package artifact hashes), and verify the installed `metaevobox` distribution metadata and source identity. Preserve the current lock record for provenance.

### P0-R1-06 — Add CI evidence for the actual MetaBox smoke

The reported 198-pass/1-skip result is a local Windows result. No Actions run is associated with `phase1a-metabox-smoke` at the reviewed SHA.

**Required:** add a branch/PR workflow that installs the pinned MetaBox runtime in an isolated environment, runs the MetaBox integration tests and the project suite, records the exact tested SHA, and uploads or retains the smoke manifest. If the full MetaBox dependency stack cannot be installed reliably on the CI runner, state that limitation and keep the Windows run as a separately identified environment test; do not present the local result as CI reproduction.

## Acceptance boundary

- **Accepted now:** real MetaBox/DE integration smoke, 1,500-FE accounting, same-seed determinism, and static scalar-parameter effect.
- **Not established:** live trajectory-conditioned control, mutation/restart effectiveness, adaptive F/CR ranges, Agent-generated policies, MetaBBO training, transfer benefit, scientific novelty, or paper readiness.
- **P1A-1 status:** **BLOCKED** until P0-R1-01 through P0-R1-04 are resolved and P0-R1-05/06 are either completed or explicitly dispositioned with reproducibility evidence.
- **API/GPU:** none authorized by this review. No live LLM calls or paid inference until a separate explicit budget approval.

## Next task

Execute `Phase-1A P0-R1`: correct action semantics, wire and test real trace-conditioned controller hooks (or explicitly narrow the action space), publish and verify split_v2, complete the dependency lock, and add exact-SHA CI. Stop for Planner re-review. Do not start Agent pilot, MetaBBO meta-training, or AES transfer before acceptance.
