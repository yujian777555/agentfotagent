# Phase-1A P0-R1-Corrective-2 Report

- Branch: `phase1a-p0-r1-corrective-2`
- Code commit: `4662564c9e0cc8c43980ba1339b480dab82489d6`
- Smoke run ID: `phase1a-smoke-4662564c9e0c-clean-20261027T173407`
- Manifest records runtime SHA `4662564…`, `worktree_dirty=false`

## A. CI dependencies

- `pyproject.toml` declares `[project.optional-dependencies] test = [pytest, numpy]`
- workflow project-suite installs `pytest numpy` then `.[test]`; runs full `pytest tests`
- metabox-integration also installs numpy; still asserts non-empty collection

## B. Manifest code provenance

- `ensure_clean_worktree()` refuses dirty trees unless `--allow-dirty`
- dirty runs are labeled dirty and never claimed as clean-SHA runs
- new manifest `agentfotagent_git_sha == 4662564c…` matches the commit that produced it

## C. Unique traces, no overwrite

- run_id = `{sha12}-{clean|dirty}-{timestamp}`
- traces in `results/phase1a_smoke/traces/<run_id>/`
- existing manifest/trace paths cause `RuntimeError` (no silent overwrite)
- tests: `test_run_ids_unique_across_calls`, `test_existing_manifest_refuses_overwrite`,
  `test_traces_live_in_run_scoped_dirs_and_old_not_overwritten`,
  `test_manifest_trace_paths_and_hashes_consistent`

## Evidence old artifacts preserved

- `INVALIDATED_manifest_p0_f6_mislabeled.json` present
- `manifest_phase1a-smoke-r1c-20261027.json` present
- flat traces `traces/controlled_*_seed*.json` present
- new run has its own `traces/phase1a-smoke-4662564c9e0c-clean-…/`

## Tests

```text
project  python -m pytest tests -o addopts='' -q -ra  → 210 passed, 1 skip (expected metaevobox)
metabox  python -m pytest tests/test_p0r1_* -q         → 42 passed
smoke    run_smoke.py                                  → clean SHA, FE exact, identity F1/F6/F24
```

Expected skip: `test_p0r1_metabox_fixes.py` importorskip metaevobox in project env only.

## CI

Workflow updated at code commit `4662564`. Both jobs must be green on that SHA
(Actions run is external; not fabricated here).

## Boundary

No LLM API / MetaBBO / AES transfer. Awaiting Planner final acceptance.
