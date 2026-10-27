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
This result is executor-reported until independently rerun.

## Findings

| ID | Finding | Severity | Fix | Regression tests | Status |
| --- | --- | --- | --- | --- | --- |
| F1 | Tool preconditions permit remote unlock/place/dial/relay and state teleportation | BLOCKER | Locality checks in `tool_world.py`: unlock/place/set_dial/read_gauge/read_offset_card/activate_relay/set_frequency require interactive range; unlock releases contents at the **container** location; failed actions do not mutate business state | `tests/test_tool_preconditions.py` | FIXED |
| F2 | plan/verification/memory genes only altered traces, not decisions | BLOCKER | Plan is stored on the phenotype and consumed for phase gating (changed plan → changed action); verification reads `verify_state` output and blocks submit until public goal checks pass; memory search uses `phenotype.recall()` only (no parallel `searched_rooms`) | `tests/test_gene_semantics.py` | FIXED |
| F3 | PublicTask exposed seed/generator/hash metadata | MAJOR | Split into `RuntimeTask` (task_id, description, max_steps) and evaluation-side `TaskInstance`; backend payload test over the exact serialized object | `tests/test_runtime_payload_isolation.py` | FIXED |
| F4 | Harness discarded real traces and built synthetic incomplete ones | BLOCKER | `BaselineHarness` retains actual `EpisodeTrace` per evaluation; `build_manifest` uses those traces; representative genome = best record (not first); `reconstruct_from_artifacts` reloads serialized artifacts and rebuilds every score | `tests/test_harness_reconstruction.py` | FIXED |
| F5 | Evaluator accepted malformed key-crate / empty dial goals | MAJOR | Fail-closed predicates: require crate and target objects, explicit `unlocked is True`, non-empty dial targets, typed dial values, valid relay object + int frequency; unknown/empty goals and non-mapping state fail closed | `tests/test_evaluator_failclosed.py` | FIXED |
| C1 | Duplicate genomes vs cache without evaluation accounting | Concern | `EvaluationAccounting` records candidate_proposals, unique_genomes, cache_hits, actual_episode_executions, task_evaluations; documented that cache hits are not new episodes | `tests/test_evaluation_accounting.py` | FIXED (accounting only; scientific budget semantics still freeze before research runs) |
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
