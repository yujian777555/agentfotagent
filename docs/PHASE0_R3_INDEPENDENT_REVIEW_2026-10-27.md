# Independent Phase-0-R3 Review — 2026-10-27

## Verdict

**REQUEST CHANGES — Phase-0 remains NOT ACCEPTED.**

- Repository: https://github.com/yujian777555/agentfotagent
- Main documentation baseline before this review: a13e17f92b471dba629c2a69d0d9462d3e117cbf
- R3 implementation commit: 16031f7e3c18a13f91a2af15eb09575b541f85cd
- R3 candidate tree independently tested: cd07249a1b4675354b01f9d5ac09ab2ffe4d2033
- Candidate branch: `phase0-r3-fixes` (not merged)
- Independent audit branch: `audit/phase0-r3-independent-review`
- Workflow commit: `c361ed2c36cf8dccd6e1deb4a9cd615ed9e7dfe5`
- No source code or tests in `phase0-r3-fixes` were modified by this review. Only an isolated workflow was added on the audit branch.
- No live LLM API, GPU, MetaBox, transfer or scientific baseline experiment was run.

## Independent full-suite reproduction

GitHub Actions: https://github.com/yujian777555/agentfotagent/actions/runs/40459330792

- Exact source checked out: `cd07249a1b4675354b01f9d5ac09ab2ffe4d2033`
- Python: 3.10.22
- Command: `python -m pytest tests -o addopts='' -q -ra`
- Result: **162 passed in 0.87s**, exit status 0
- The workflow checked out the exact candidate SHA, rather than testing its own workflow commit.
- Audit log artifact: https://github.com/yujian777555/agentfotagent/actions/runs/40459330792/artifacts/12713243779

The existing 162-test suite passes on the exact R3 candidate tree. However, additional independent adversarial probes found three residual correctness/schema issues, and the standalone counterexample probe itself has a false-positive defect. A green suite does not override these counterexamples.

## Findings

### R3-05 — Non-boolean persisted success values are accepted

**Severity: MAJOR — REQUEST CHANGES**

In `src/agentfotagent/evaluation/provenance.py`, `_normalize_score_value("success", value)` returns `bool(value)` rather than requiring `isinstance(value, bool)`.

Independent adversarial probe:
1. Generate a valid artifact whose recorded score has `success=True`.
2. Change the persisted value from boolean `true` to integer `1`.
3. Call `reconstruct_from_artifacts` against the original trace/task/evaluator.

The reconstruction **accepts** the artifact. This is a type-tampering case: the stored JSON value is not the schema-defined boolean, but coercion silently normalizes it. The existing wrong-type regression tests cover `steps`, not `success`.

**Required fix:** reject any recorded `success` value that is not an actual boolean before comparison. Add parameterized tests for integer 0/1, strings, null and other non-boolean values, while preserving valid true/false records.

### R3-06 — Unknown extra score fields are silently accepted

**Severity: MODERATE — REQUEST CHANGES**

Independent adversarial probe adds `"unvalidated_metric": 999999` to a persisted score record while leaving all known fields intact. `reconstruct_from_artifacts` accepts it because `compare_score_fields` checks the required known fields but does not reject unknown keys.

This weakens the claim of a strict score schema and can allow downstream consumers to see unvalidated metrics in an artifact.

**Required fix:** define the canonical allowed score-record fields (including identity fields such as `task_id` and `genome_hash`) and reject unknown keys, or explicitly version and validate an extension mechanism. Add a regression test proving an unrecognized score field is rejected.

### R3-07 — key_crate accepts missing entity location fields

**Severity: MAJOR — REQUEST CHANGES**

Independent adversarial probe constructed a final state with:
- statue: `{"type": "artifact", "location": "pedestal"}`
- crate: `{"type": "crate", "unlocked": true}` (no location)
- pedestal: `{"type": "surface"}` (no location)

The evaluator returns **success=True**. The current R3 predicate checks the statue/crate/surface types and statue-to-surface name relation, but does not validate the crate's location or the surface's location. This leaves a malformed world state able to pass the task success predicate.

**Required fix:** validate required location fields against the task's legal world locations and the generator-defined surface placement. Ensure the crate's location is valid and the referenced surface has a valid location/expected setup relationship. Add tests for missing, wrong-type, unknown and inconsistent location values; retain a valid real-episode success test.

### R3-08 — Original R2 counterexample probe has false-positive logic

**Severity: MODERATE — REQUEST CHANGES**

File: `tests/probe_r2_counterexamples.py`.

The helper `probe()` treats every `AssertionError` and every generic `Exception` as PASS. But:
- R3-01 raises `RuntimeError` if seed recovery succeeds, and the generic exception handler marks that attack success as PASS; if no recovery occurs, it raises `AssertionError`, which is also marked PASS.
- R3-04 raises `AssertionError` if the tampered artifact is accepted, and the helper marks that as PASS; if reconstruction rejects it, `ReconstructionError` is marked PASS.

Consequently, the reported standalone “4/4 PASS” is not valid evidence for R3-01 or R3-04. The dedicated pytest cases are better structured and the complete suite passes, but the reusable counterexample probe must be corrected so that vulnerable behavior fails the probe and only expected rejection passes.

**Required fix:** make each probe return an explicit pass/fail result or raise a dedicated unexpected-acceptance exception that is never caught as a pass. Add a self-test or unit tests for the probe harness itself, including a deliberately vulnerable stub proving the harness reports FAIL.

## R3 item status after independent review

| Item | Independent review status |
|---|---|
| R3-01 random runtime token | Implementation appears correct; dedicated test passes. Standalone probe is invalid for this item and must be repaired before reuse. |
| R3-02 relay goal validation | FIXED in reviewed paths; original malformed-goal regression and suite pass. |
| R3-03 key_crate entity validation | PARTIAL — missing crate/surface location fields still permit success. |
| R3-04 score reconstruction | PARTIAL — integer `success` coercion and unknown score fields are accepted. |
| Probe harness | PARTIAL — false positives for R3-01 and R3-04. |

## Required next pass (R4 corrective follow-up)

1. Strictly validate the type of the persisted `success` field.
2. Reject unknown fields in score records or introduce a validated, versioned extension schema.
3. Validate key_crate crate and surface location fields against the actual generated task setup.
4. Correct `tests/probe_r2_counterexamples.py` and test its own pass/fail semantics.
5. Add regression tests for each new counterexample.
6. Rerun the full suite on the corrected source SHA and independently reproduce it.
7. Update the response matrix, environment specification, Planner plan and `status.json`.
8. Stop for independent review; do not merge to `main` or declare Phase-0 accepted.

**Stop condition:** Phase-0 remains NOT ACCEPTED. No transfer experiment, MetaBox meta-training, live API call, GPU run or scientific baseline comparison is authorized until the corrective pass is independently accepted.
