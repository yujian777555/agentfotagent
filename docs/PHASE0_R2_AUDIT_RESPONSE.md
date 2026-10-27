# Phase-0-R2 Residual Audit Response Matrix

- Repository: https://github.com/yujian777555/agentfotagent
- Review basis: `docs/PHASE0_R1_INDEPENDENT_REVIEW_2026-10-27.md`
- Reviewed code commit: `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9`
- Review document commit (start baseline): `fb34e6264196e7785281cf8792daa16cdfb09086`
- Corrective pass: Phase-0-R2
- Scope: residual audit findings only. No live LLM API, GPU, MetaBox meta-training, transfer or scientific baseline comparison.

Merged push commit: 2d5209dfac7b1fd1348ee04ebaf0a3f9bfefef39 (R2 fixes + preserved R1 reproduction docs).

## Test command (executor-run)

```text
python -m pytest tests -q
```

See `status.json` for the exact corrective commit SHA, collected/passed counts and
run environment. Mock backend only; engineering evidence is never Agent
capability evidence.

## Findings

| ID | Finding | Fix | Regression tests | Status |
| --- | --- | --- | --- | --- |
| R1-01 | Runtime task_id encodes family/split/seed in backend payload | `RuntimeTask.runtime_id` is opaque (`rt_` + 16-hex digest of content hash). Evaluation keeps `task_id`. Payload tests assert full JSON string values (family/split/seed patterns) and removed the small-seed escape hatch | `tests/test_runtime_payload_isolation.py` | FIXED |
| R1-02 | Relay verification accepted any non-null frequency | `_goal_checks_passed` derives expected frequency from `known_frags` note digits and compares equality; wrong-but-non-null frequency fails and submit stays unverified | `tests/test_r1_residual_fixes.py` | FIXED |
| R1-03 | Missing relay object bypassed locality and scoring | `activate_relay` / `set_frequency` require a valid local `relay` object (type/location); evaluator requires `objects["relay"]` with `type=="relay"`; happy-path fixtures include the object | `tests/test_r1_residual_fixes.py`, updated `test_tool_preconditions.py`, `test_evaluator_failclosed.py` | FIXED |
| R1-04 | Incomplete goals / unsafe metrics | dial_set requires full `{alpha,beta,gamma}` and in-range ints; key_crate requires `crate_unlocked is True` (missing key fails); relay goal requires `code` + `frequency`; `step` type-checked safely; evaluate never raises on garbage | `tests/test_r1_residual_fixes.py` | FIXED |
| R1-05 | One-way reconstruction; harness run state mixed | `reconstruct_from_artifacts` enforces exact trace↔score bijection and raises `ReconstructionError`; cache stores traces so cache hits still contribute real traces; `begin_run` resets trace_store/accounting/seen genomes | `tests/test_r1_reconstruction_isolation.py` | FIXED |
| R1-06 | Stale v1 semantic versions | `aes-tool-world-v2`, `aes-evaluator-v2`, `mock-engineering-v2`, `aes-task-gen-v2`; `configs/evaluation_protocol.json` synced; run manifests record `source_commit_sha` | `test_manifest_records_source_and_versions` | FIXED |

## Acceptance checklist from re-review

| Required | Evidence |
| --- | --- |
| Opaque runtime IDs / no family-split-seed leak | `test_runtime_payload_isolation.py` |
| Relay verification compares expected frequency | `test_r1_residual_fixes.py` |
| Missing relay object fail-closed (tools + evaluator) | `test_r1_residual_fixes.py` |
| Complete goal schemas + safe metrics | `test_r1_residual_fixes.py` |
| Bidirectional reconstruction + run isolation | `test_r1_reconstruction_isolation.py` |
| Version bumps + commit SHA in manifests | harness/provenance + `evaluation_protocol.json` |

## Known limitations (unchanged / acknowledged)

1. Mock backend is scripted engineering scaffolding; scores are not capability evidence.
2. C2: `relay_route` held-out remains an engineering smoke test.
3. Formal scientific budget semantics (proposals vs unique evaluations vs episodes) still require a later protocol freeze.
4. No external benchmark adapter, transfer object, live API, GPU or MetaBox work in this pass.

## Stop condition

Executor stops here. Waiting for independent Planner re-review of the Phase-0-R2
corrective commit. No transfer experiments, MetaBox meta-training, live LLM API
calls, GPU runs or scientific baseline comparisons until Phase-0 is accepted.
