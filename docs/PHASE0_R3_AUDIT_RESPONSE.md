# Phase-0-R3 Corrective Response Matrix

- Repository: https://github.com/yujian777555/agentfotagent
- Work branch: `phase0-r3-fixes` (not merged to main)
- Audit baseline (main): `a13e17f92b471dba629c2a69d0d9462d3e117cbf`
- Reviewed R2 source: `ec73906e15c048285cff3bca90a4f1f8bed21da8`
- Audit doc: `docs/PHASE0_R2_INDEPENDENT_REVIEW_2026-10-27.md`
- R2 reproduction: https://github.com/yujian777555/agentfotagent/actions/runs/40453697835 (127 passed on R2)
- Scope: R3-01..R3-04 only. No live LLM API, GPU, MetaBox, transfer or scientific baseline.

## Findings

| ID | Root cause | Fix | Regression tests | Original counterexample | Status |
| --- | --- | --- | --- | --- | --- |
| R3-01 | runtime_id = digest(content_hash)[:16] recoverable by public seed enumeration | Random `secrets.token_hex(12)` presentation token; stable eval identity (task_id/content_hash) kept; `manifest_hash` excludes runtime tokens | `tests/test_r3_corrective_fixes.py` (seed enumeration probe), `tests/test_runtime_payload_isolation.py` | seed 17 recovered from `rt_7b72f14d92fb4a4c` | FIXED |
| R3-02 | `_pred_relay_route` accepted code=None, frequency=99 | Validate code (3 ASCII digits), frequency int 1–7 non-bool, consistency `freq=(digit_sum%7)+1`, relay object type | `tests/test_r3_corrective_fixes.py` (parametrized malformed goals) | goal `{code:None, frequency:99}` | FIXED |
| R3-03 | key_crate predicate skipped entity `type` and pedestal record | Require statue type `artifact`, crate type `crate`, surface object type `surface` | `tests/test_r3_corrective_fixes.py` (missing/wrong types, missing pedestal) | entities without type + no pedestal | FIXED |
| R3-04 | reconstruction compared only success+steps | `compare_score_fields` strict full-field check (success, steps, invalid_actions, repeated_states, termination_reason, final_state_hash) with type validation | `tests/test_r3_corrective_fixes.py` (per-field tamper) | invalid_actions 0→999999 | FIXED |

## Validation (executor)

```text
python tests/probe_r2_counterexamples.py
  PASS R3-01 seed enumeration
  PASS R3-02 malformed relay goal
  PASS R3-03 malformed key_crate entities
  PASS R3-04 tampered invalid_actions

python -m pytest tests/test_r3_corrective_fixes.py -o addopts='' -q
  35 passed

python -m pytest tests -o addopts='' -q -ra
  162 passed
```

Exact source SHA and runtime recorded in `status.json` after push. Mock backend only; engineering evidence is not Agent capability evidence.

## Residual risks

1. Runtime tokens are presentation-only; anyone holding a full evaluation-side manifest can still see family/seed by design (evaluation side).
2. `diagnostic` fields on EpisodeResult are not persisted in manifest scores and therefore are not reconstructed (explicitly unverified).
3. Seed domain used in the enumeration probe is 0–100 as declared in configs; larger domains need the same random-token property (which holds).
4. C2 held-out family remains an engineering smoke test.

## Next step

Push `phase0-r3-fixes` and stop for independent review. Phase-0 remains NOT ACCEPTED.
