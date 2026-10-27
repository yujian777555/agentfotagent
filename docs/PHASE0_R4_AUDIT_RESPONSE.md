# Phase-0-R4 Corrective Response Matrix

- Repository: https://github.com/yujian777555/agentfotagent
- Work branch: `phase0-r4-fixes` (not merged to main)
- Base: `phase0-r3-fixes@cd07249a1b4675354b01f9d5ac09ab2ffe4d2033`
- Audit: `docs/PHASE0_R3_INDEPENDENT_REVIEW_2026-10-27.md` (REQUEST CHANGES)
- R3 independent tests: 162 passed on `cd07249` (run 40459330792) — does not override counterexamples

## Findings

| ID | Review ID | Fix | Tests | Status |
| --- | --- | --- | --- | --- |
| R4-01 | R3-05 | `_normalize_score_value("success")` requires `isinstance(value, bool)`; no coercion | `test_r4_corrective_fixes.py::test_non_bool_success_rejected` (param 0/1/"true"/None/list/dict/float) | FIXED |
| R4-02 | R3-06 | `validate_score_record_schema`: closed allowed fields (identity + score); unknown/missing/wrong-type rejected | `test_unknown_score_field_rejected`, `test_missing_identity_field_rejected`, artifact tests | FIXED |
| R4-03 | R3-07 | `_pred_key_crate(..., task)` validates crate/surface `location` against `task.setup` (legal locations + expected placement) | missing/wrong-type/unknown/inconsistent location tests + real-episode success | FIXED |
| R4-04 | R3-08 | Probe returns explicit (passed, detail); unexpected exceptions → FAIL; exit code reflects failures; vulnerable-stub self-tests | `test_probe_detects_vulnerable_acceptance_stub`, `test_probe_detects_unexpected_exception_as_fail` | FIXED |

## Validation

```text
python tests/probe_r2_counterexamples.py
  7/7 PASS (R3-01..R3-04 + R4-01..R4-03), exit 0

python -m pytest tests/test_r4_corrective_fixes.py -o addopts='' -q   → 27 passed
python -m pytest tests/test_r3_corrective_fixes.py -o addopts='' -q   → 35 passed
python -m pytest tests -o addopts='' -q -ra                           → 189 passed
```

CI: `.github/workflows/phase0-r4-tests.yml` runs probes + targeted + full suite on `phase0-r4-fixes` and can check out an explicit SHA via `workflow_dispatch`.

## Residual

- Independent CI reproduction of the exact R4 SHA is required before acceptance.
- Phase-0 remains NOT ACCEPTED until that review passes.
