# Phase-0-R2 Residual Audit Response Matrix

- Repository: https://github.com/yujian777555/agentfotagent
- Review basis: `docs/PHASE0_R1_INDEPENDENT_REVIEW_2026-10-27.md`
- Original R1 reviewed code commit: ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9
- Current R2 source tree independently reviewed: ec73906e15c048285cff3bca90a4f1f8bed21da8
- Review document commit (start baseline): `fb34e6264196e7785281cf8792daa16cdfb09086`
- Corrective pass: Phase-0-R2
- Scope: residual audit findings only. No live LLM API, GPU, MetaBox meta-training, transfer or scientific baseline comparison.

Merged push commit: 2d5209dfac7b1fd1348ee04ebaf0a3f9bfefef39 (R2 fixes + preserved R1 reproduction docs).

## Independent R2 test reproduction

Command: python -m pytest tests -o addopts='' -q -ra.

- Exact source SHA: ec73906e15c048285cff3bca90a4f1f8bed21da8
- Result: **127 passed in 0.43s**
- GitHub Actions: https://github.com/yujian777555/agentfotagent/actions/runs/40453697835
- Probe output artifact: https://github.com/yujian777555/agentfotagent/actions/runs/40453697835/artifacts/12711107094

Mock backend only; engineering evidence is never Agent capability evidence.

## Findings

| ID | Finding | Fix | Regression tests | Status |
| --- | --- | --- | --- | --- |
| R1-01 | Runtime task_id encodes family/split/seed in backend payload | RuntimeTask.runtime_id is a deterministic digest of task content. An adversarial probe recovered seed 17 by enumerating candidate seeds 0–100 with the public generator. It is lexically opaque but not opaque against a known finite seed domain. | tests/test_runtime_payload_isolation.py; add seed-enumeration regression | PARTIAL — REQUEST CHANGES |
| R1-02 | Relay verification accepted any non-null frequency | `_goal_checks_passed` derives expected frequency from `known_frags` note digits and compares equality; wrong-but-non-null frequency fails and submit stays unverified | `tests/test_r1_residual_fixes.py` | FIXED |
| R1-03 | Missing relay object bypassed locality and scoring | `activate_relay` / `set_frequency` require a valid local `relay` object (type/location); evaluator requires `objects["relay"]` with `type=="relay"`; happy-path fixtures include the object | `tests/test_r1_residual_fixes.py`, updated `test_tool_preconditions.py`, `test_evaluator_failclosed.py` | FIXED |
| R1-04 | Incomplete goals / unsafe metrics | Dial targets and required fields are checked, but relay goal values are not fully validated: code=None and frequency=99 can pass when state frequency matches. key_crate also accepts statue/crate mappings without required entity types. | tests/test_r1_residual_fixes.py; add malformed value/entity tests | PARTIAL — REQUEST CHANGES |
| R1-05 | One-way reconstruction; harness run state mixed | Trace/score bijection and run isolation are covered, but reconstruction compares only success and steps after identity matching. Tampering invalid_actions from 0 to 999999 is accepted. | tests/test_r1_reconstruction_isolation.py; add tampering tests for all score fields | PARTIAL — REQUEST CHANGES |
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


## Independent review result — 2026-10-27

**Verdict: REQUEST CHANGES.** The existing 127-test suite passes independently, but diagnostic probes against the exact R2 source tree reveal uncovered failures:

1. Runtime ID seed recovery: rt_7b72f14d92fb4a4c is mapped back to seed 17 by enumerating seeds 0–100 with the public generator.
2. Malformed relay goal: code=None and frequency=99 are accepted as success when the relay state is activated at frequency 99.
3. Malformed key_crate state: statue/crate records without required entity type fields are accepted as success.
4. Artifact integrity: setting a recorded invalid_actions metric from 0 to 999999 does not cause reconstruction to reject the artifact.

Detailed report: docs/PHASE0_R2_INDEPENDENT_REVIEW_2026-10-27.md. Reproduction record: docs/PHASE0_R2_TEST_REPRODUCTION_2026-10-27.md.

R1-01, R1-04 and R1-05 therefore remain PARTIAL, not FIXED. No transfer experiments, MetaBox meta-training, live API calls, GPU runs or scientific baseline comparisons until a corrective pass is independently accepted.

## Phase-0-R3 corrective follow-up

Residual findings R2-01..R2-04 from docs/PHASE0_R2_INDEPENDENT_REVIEW_2026-10-27.md are addressed on branch phase0-r3-fixes. See docs/PHASE0_R3_AUDIT_RESPONSE.md. This R2 matrix is not re-marked ACCEPTED.
