# Phase-1A P0-R1 Review Response

- Branch: `phase1a-p0-r1` (from main `c232a30587e462a5a85e09266c1bbed0e882772b`)
- Migrated from: `phase1a-metabox-smoke@f571b52` (preserved as audit record)
- Review basis: `docs/PHASE1A_P0_PLANNER_REVIEW_2026-10-27.md`

## Fixes

| ID | Issue | Fix | Tests | Status |
|---|---|---|---|---|
| P0-R1-00 | `difficulty='all'` ignored user lists → always F1 | `load_function` uses `difficulty=None` + explicit user lists; wrapper `function_id` derived from class name `F{id}`; mismatch raises | `test_requested_id_matches_loaded_class`, `test_all_function_ids_load_correctly`, `test_distinct_ids_are_distinct_functions` | FIXED |
| P0-R1-01 | `set_F_range` applied midpoint scalar | DSL **v2** scalar actions `set_F` / `set_CR`; range names rejected | `test_dsl_v2_scalar_actions`, `test_range_actions_rejected_in_dsl_v2` | FIXED |
| P0-R1-02 | Controller called once with constant state | `controlled_de.run_controlled_de` computes live features per generation, calls controller every generation, logs state/action/effect | `test_controlled_de_live_trajectory_triggers_rule`, `test_applied_F_CR_match_controller_actions`, `test_recorded_actions_match_effects` | FIXED |
| P0-R1-03 | mutation/restart silently ignored | Official DE path raises `UnsupportedActionError`; controlled DE also rejects until implemented | `test_unsupported_actions_rejected_by_official_de` | FIXED (fail-closed) |
| P0-R1-04 | Sequential split not stratified | `split_v2` train/val/held = `[1,2,4,6,7,10,11,12,15,18,20,21]` / `[3,8,13,16,22,23]` / `[5,9,14,17,19,24]`; families+difficulty in manifest; difficult counts 4/2/2 | `test_split_v2_*` | FIXED |
| P0-R1-05 | Lock incomplete | `requirements-freeze.txt` full resolved deps + LOCK.json install provenance | files committed | FIXED |
| P0-R1-06 | No CI | `.github/workflows/phase1a-metabox.yml` windows-latest, pinned metaevobox, records SHA, uploads manifest | workflow | ADDED |

## Artifacts

- Old F6-labeled results **invalidated**: preserved as
  `results/phase1a_smoke/INVALIDATED_manifest_p0_f6_mislabeled.json`.
- New run: `results/phase1a_smoke/manifest_phase1a-smoke-r1-20261027.json`
  (run_id `phase1a-smoke-r1-20261027`).
- Identity check in new manifest: requested 1/6/24 → class F1/F6/F24.

## Test evidence (executor)

```text
D:/metabox-env/Scripts/python.exe -m pytest tests/ -o addopts='' -q
  → 208 passed (Windows, Python 3.11.15)

python tests (project py 3.10): DSL + skip metaevobox
```

## Trajectory-driven controller

**Verified:** `controlled_de` runs generation-level hooks; stagnation rule can
switch F mid-run; applied F/CR history matches logged effects; same seed
reproduces cost curve and action sequence. Official DE remains the unmodified
baseline (controller applied only as start-time config for that path).

## Residual

- Controlled DE implements rand/1/bin only; mutation_strategy/restart remain
  rejected (fail-closed) until a later operator implementation.
- CI result not yet observed at report time (workflow added; needs push).
- No LLM API / MetaBBO training / AES transfer.

## Stop

Awaiting Planner re-review. P1A-1 still blocked until acceptance.
