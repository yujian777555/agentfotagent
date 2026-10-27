# Phase-0-R1 Audit Response Matrix

- Repository: https://github.com/yujian777555/agentfotagent
- Audit basis: `docs/PHASE0_INDEPENDENT_AUDIT_2026-10-26.md` (verdict: REQUEST CHANGES)
- Corrective pass: Phase-0-R1
- Audited commit under repair: `987df6dbb21683331968f09acf6160fbbdf005bb`
- Corrective commit (full pass): `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9`
- Scope of this pass: audit findings only. No live LLM API, GPU, MetaBox meta-training or transfer experiments.

## Test command (executor-run, reproducible)

```text
python -m pytest tests -q
```

Run at: `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9`
Executor-run result: **104 tests collected, all passing** (0 failures, 0 errors).
Mock backend only; engineering evidence is never Agent capability evidence.
This result has now been independently reproduced through GitHub Actions on the exact R1 source commit; see `docs/PHASE0_R1_TEST_REPRODUCTION_2026-10-27.md`.

## Findings

| ID | Finding | Severity | Fix | Regression tests | Status |
| --- | --- | --- | --- | --- | --- |
| F1 | Tool preconditions permit remote unlock/place/dial/relay and state teleportation | BLOCKER | Locality checks cover normal generated tasks, but missing objects[relay] still bypasses activate/set-frequency locality checks | tests/test_tool_preconditions.py (missing-object adversarial case absent) | PARTIAL — REQUEST CHANGES |
| F2 | plan/verification/memory genes only altered traces, not decisions | BLOCKER | Plan and memory now affect decisions; relay verification still accepts any non-null frequency rather than checking the expected frequency derived from notes | tests/test_gene_semantics.py (wrong-frequency case absent) | PARTIAL — REQUEST CHANGES |
| F3 | PublicTask exposed seed/generator/hash metadata | MAJOR | Separate runtime task object exists, but task_id still encodes family/split/seed and is sent to the backend | tests/test_runtime_payload_isolation.py (encoded-value case absent) | PARTIAL — REQUEST CHANGES |
| F4 | Harness discarded real traces and built synthetic incomplete ones | BLOCKER | Actual traces are retained and normal fresh-harness reconstruction works; reconstruction does not detect manifest scores lacking traces, and harness reuse can mix run artifacts/accounting | tests/test_harness_reconstruction.py (tamper/reuse cases absent) | PARTIAL — REQUEST CHANGES |
| F5 | Evaluator accepted malformed key-crate / empty dial goals | MAJOR | Common malformed cases fail closed, but partial dial goals, missing crate_unlocked, missing relay object, and malformed step remain unguarded | tests/test_evaluator_failclosed.py (partial-schema/step cases absent; relay happy path uses empty objects) | PARTIAL — REQUEST CHANGES |
| C1 | Duplicate genomes vs cache without evaluation accounting | Concern | Basic counters distinguish proposals/cache hits/episodes, but accounting and trace storage are harness-lifetime state, not run-scoped when a harness is reused | tests/test_evaluation_accounting.py (reuse case absent) | PARTIAL (freeze budget semantics and test run isolation before research) |
| C2 | Held-out family is engineering smoke test, not generalization evidence | Concern | Accepted limitation. `relay_route` held-out remains a split-plumbing smoke test. No capability claim. Stronger family freeze + external validation stay later-phase items | documented in spec §8.1 / §8.2 | ACKNOWLEDGED (not a Phase-0 code gate) |
| C3 | Missing adversarial precondition and harness-artifact tests | Concern | Added in this pass with F1/F4 regression files | `test_tool_preconditions.py`, `test_harness_reconstruction.py` | FIXED |

## Acceptance gate checklist

| Required gate | Evidence |
| --- | --- |
| 1. Remote unlock/place/dial/relay shortcuts prevented | `test_tool_preconditions.py` |
| 2. Planning, verification, memory drive decisions | `test_gene_semantics.py` |
| 3. Model-facing payload excludes seed/evaluator metadata | `test_runtime_payload_isolation.py` |
| 4. Search-run artifacts preserve full traces; scores rebuild E2E | `test_harness_reconstruction.py` |
| 5. Evaluator fails closed on malformed state/goal | `test_evaluator_failclosed.py` |
| 6. Full suite rerun on resulting commit | recorded in `status.json` and this matrix after push |

## Known limitations after this pass

1. Mock backend remains scripted engineering scaffolding; scores are not capability evidence.
2. `C1` accounting is recorded, but formal budget definitions for scientific comparisons (proposals vs unique evals vs episodes) must still be frozen in a later protocol.
3. Held-out `relay_route` is still one in-repo generator family (C2).
4. No external benchmark adapter, transfer object, live API, GPU or MetaBox work in this pass.

## Stop condition

Executor stops here. Waiting for independent Planner re-review of the corrective commit.


## Independent re-review — 2026-10-27

**Verdict: REQUEST CHANGES.** See docs/PHASE0_R1_INDEPENDENT_REVIEW_2026-10-27.md.

The original fixes are present, but the following acceptance gates remain open:
- F1/F5: missing relay object must fail closed in both tool handlers and evaluator.
- F2: relay verification must compare frequency with the value derived from observed note fragments.
- F3: model-facing task IDs must not encode family, split, or seed; add a value-level payload test.
- F5: require complete goal schemas and handle malformed state metrics without exceptions.
- F4/C1: verify manifest-to-trace completeness in both directions and make accounting/artifacts run-scoped or reset them deterministically.
- Provenance: bump environment/evaluator/backend version identifiers after semantic changes and update config/cache metadata.

The existing suite was independently reproduced: 104 passed in 0.24s on source commit `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9` in GitHub Actions ([run 40441941389](https://github.com/yujian777555/agentfotagent/actions/runs/40441941389)). The original implementation commit has no check run attached; the reproduction ran from an isolated workflow branch and explicitly checked out that exact source SHA. The suite passing does not cover the residual adversarial cases listed above. No scientific experiments are authorized until the next independent review accepts the fixes.
