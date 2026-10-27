# Independent Phase-0-R1 Re-review — 2026-10-27

- Repository: https://github.com/yujian777555/agentfotagent
- Audited main HEAD: 3322a9d8eef80308a50c55f25292d4034d94699f
- Corrective implementation commit: ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9
- Verdict: **REQUEST CHANGES — Phase-0 remains unaccepted**
- Review type: independent static source and regression-test review through the GitHub repository connector.
- Test status: independently reproduced on GitHub Actions run [40441941389](https://github.com/yujian777555/agentfotagent/actions/runs/40441941389): `python -m pytest tests -o addopts='' -q -ra` → **104 passed in 0.24s**, Python 3.11.17 on Ubuntu. The workflow explicitly checked out source commit `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9`; see `docs/PHASE0_R1_TEST_REPRODUCTION_2026-10-27.md`. The original commit itself has no attached check run; this independent run was triggered from an isolated audit branch. Passing existing tests does not resolve the residual static-review findings below.
- No code was modified in the implementation by this review; no live API, GPU, MetaBox or scientific experiment was run.

## What is genuinely improved

1. Normal generated tasks now enforce locality for remote unlock/place/dial/relay operations.
2. Unlocking releases contained objects at the container's actual location.
3. Planning and episodic memory now participate in the mock policy's decision path, rather than merely adding trace events.
4. RuntimeTask is separated from the evaluation-side TaskInstance.
5. The harness retains actual EpisodeTrace objects for normal evaluations, and the fresh-harness JSON round-trip test exercises score reconstruction.
6. Common malformed goal/state cases are rejected by the evaluator.
7. Proposal, unique-genome, cache-hit and actual-episode counters are now recorded.

These are meaningful corrections. They do not yet satisfy every acceptance condition.

## Residual findings

### R1-01 / F3 — Runtime task ID still leaks family, split and seed

**Severity: BLOCKER**

Sources:
- src/agentfotagent/tasks/generators.py: generated task ID is f"{family}/{split}/seed{seed:06d}".
- src/agentfotagent/runtime/mock_backend.py: run_episode sends task.runtime.task_id in runtime_context.
- tests/test_runtime_payload_isolation.py: checks sensitive key names but not the encoded value inside task_id; the seed assertion explicitly permits small seeds (or task.seed < 10).

For the held-out example, the backend receives an identifier such as relay_route/held_out/seed000001. Thus family, split and seed are still disclosed even though they are not separate fields. The test's seed-1 fixture does not detect this.

**Required fix:** use an opaque runtime-facing identifier that does not encode family/split/seed, or omit the identifier from model-facing context. Preserve the evaluator-side ID in the evaluation record. Add tests that parse/reject family names, split labels and seed patterns anywhere in the serialized backend payload.

### R1-02 / F2 — Relay verification treats any non-null frequency as correct

**Severity: MAJOR**

Source: src/agentfotagent/runtime/mock_backend.py, helper _goal_checks_passed.

For relay_route, the helper currently returns true when the relay is activated and relay_frequency is merely non-null. It does not compare the actual frequency with the expected value computed from the three note fragments, although policy.known_frags contains the information needed to calculate it.

An incorrect frequency can therefore pass the verification gene's pre-finalization check. The terminal evaluator may later reject the task, but that does not make the verification behavior correct.

**Required fix:** derive the expected frequency from the observed note fragments and compare it to the public relay state. Add a wrong-but-non-null-frequency regression test proving verification fails and submit remains blocked.

### R1-03 / F1 + F5 — Missing relay object bypasses locality and evaluator object checks

**Severity: MAJOR**

Sources:
- src/agentfotagent/environments/tool_world.py, _tool_activate_relay and _tool_set_frequency.
- src/agentfotagent/evaluation/evaluator.py, _pred_relay_route.
- tests/test_evaluator_failclosed.py, test_happy_paths_still_pass.

The relay handlers enforce locality only inside if relay_obj is not None. If objects["relay"] is absent, locality is skipped while the separate relay-state mapping can still be activated and assigned a frequency.

The evaluator also checks only state["relay"]; it does not require a valid state["objects"]["relay"]. The current relay happy-path test uses the helper's default empty objects mapping and still expects success, so it codifies the incomplete contract.

**Required fix:** missing or malformed relay objects must fail closed in the tool handlers and evaluator. Update the happy-path fixture to include a valid relay object and add explicit missing-object tests for both activation and scoring.

### R1-04 / F5 — Incomplete goal schemas and malformed state metrics are not fully fail-closed

**Severity: MAJOR**

Source: src/agentfotagent/evaluation/evaluator.py.

- _pred_dial_set requires a non-empty target mapping but does not require the complete expected set of dials. A goal containing only alpha can pass if the corresponding state value matches.
- _pred_key_crate only requires crate.unlocked is True when goal.get("crate_unlocked") is truthy. If the required goal flag is missing, a statue on the pedestal can pass without an explicit unlock requirement.
- evaluate catches errors in success_predicate, but converts final_state["step"] to int outside that protection. A mapping with a malformed value such as step="not-an-int" can raise rather than returning a failed result.

**Required fix:** validate each goal type against a complete schema, including required fields and expected dial keys/ranges. Make metric extraction robust to malformed state values and return an explicit failure/error record instead of raising. Add regression tests for partial dial goals, missing crate_unlocked, and invalid step types.

### R1-05 / F4 — Reconstruction does not verify completeness in both directions

**Severity: MAJOR**

Source: src/agentfotagent/evaluation/provenance.py, reconstruct_from_artifacts; src/agentfotagent/evolution/harness.py.

The reconstruction helper checks that each available trace has a corresponding manifest score. It does not check that every manifest score has a trace. Removing a trace while retaining its score can therefore leave mismatches == [] even though not every score was reconstructed. The current test asserts rebuilt count equals trace count, not manifest-score count.

In addition, BaselineHarness keeps trace storage and accounting for the lifetime of the harness. Reusing one harness for a second run can include traces from the earlier run in serialize_run_artifacts, while the second manifest is built only from the second run's records; accounting also remains cumulative.

**Required fix:** enforce exact trace/score correspondence in both directions and validate the manifest episode/score counts. Add tests that remove a trace, add an unmatched score, and run two sequential runs through the same harness. Either reset state per run or create explicitly isolated run-scoped artifacts/accounting.

### R1-06 — Semantic version identifiers were not advanced after code changes

**Severity: MAJOR before scientific experiments**

Sources:
- src/agentfotagent/environments/tool_world.py: TOOL_WORLD_VERSION = "aes-tool-world-v1".
- src/agentfotagent/evolution/harness.py: EVALUATOR_VERSION = "aes-evaluator-v1".
- src/agentfotagent/runtime/mock_backend.py: MOCK_BACKEND_ID = "mock-engineering-v1".

Environment, evaluator and mock-backend behavior changed in Phase-0-R1, but the identifiers used in cache keys and run provenance remain at their pre-correction values. This makes results from different semantics indistinguishable by these fields and weakens cache isolation/reproducibility.

**Required fix:** bump the environment, evaluator and backend/phenotype version identifiers and update configs/evaluation_protocol.json and related protocol metadata. Before scientific experiments, ensure cache keys and run manifests identify the actual semantic version (preferably also recording the source commit SHA).

## Acceptance status by prior audit finding

| Finding | Re-review status | Reason |
|---|---|---|
| F1 tool preconditions | PARTIAL | Normal tasks fixed; missing relay object bypass remains |
| F2 gene semantics | PARTIAL | Plan/memory wired; relay verification has a false-positive condition |
| F3 payload isolation | NOT ACCEPTED | Task ID still encodes family/split/seed |
| F4 provenance reconstruction | PARTIAL | Normal path works; completeness and run isolation are not enforced |
| F5 fail-closed evaluator | NOT ACCEPTED | Missing relay object, partial goals and malformed step remain |
| C1 evaluation accounting | PARTIAL | Basic counters exist; run reuse mixes accounting and traces |
| C2 held-out generalization | ACKNOWLEDGED LIMITATION | relay_route remains an engineering smoke test, not capability evidence |

## Required next pass

1. Fix R1-01 through R1-06 and add targeted regression tests.
2. Bump environment/evaluator/backend version identifiers and update cache/config/provenance metadata.
3. Run python -m pytest tests -q in a reachable environment; record exact commit SHA and output. The previous 104-pass result remains executor-reported.
4. Update docs/PHASE0_R1_AUDIT_RESPONSE.md, planner/latest_plan.md, status.json and the environment spec.
5. Push the corrective commit, verify HEAD == origin/main, and stop for independent review.

**Stop condition:** no transfer experiments, MetaBox meta-training, live LLM API calls, GPU runs or scientific baseline comparisons until the next independent review accepts Phase-0.


## Test reproduction update — 2026-10-27

A GitHub Actions run was created on the isolated branch `audit/reproduce-phase0-r1-tests`. The workflow checkout then detached to the exact corrective source commit `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9` before installing dependencies or running tests.

- Run: https://github.com/yujian777555/agentfotagent/actions/runs/40441941389
- Workflow branch commit: `146710f6e23b86eb1907c5c1c7115ed6d11b6f82`
- Source commit tested: `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9`
- Runtime: Ubuntu GitHub-hosted runner, Python 3.11.17
- Command: `python -m pytest tests -o addopts='' -q -ra`
- Result: **104 passed in 0.24s**, exit status 0
- Artifact: https://github.com/yujian777555/agentfotagent/actions/runs/40441941389/artifacts/12706387658

This independently confirms that the existing 104-test suite passes on the R1 source tree. It does **not** establish that the suite covers all adversarial cases identified in this report. Verdict remains **REQUEST CHANGES** until R1-01 through R1-06 are fixed and reviewed. No live API, GPU, MetaBox, transfer or scientific experiment was run.
