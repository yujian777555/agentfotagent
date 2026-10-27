# Phase-0-R2 Test Reproduction — 2026-10-27

## Full-suite result

**127 passed in 0.43s**, exit status 0.

## Provenance

- Repository: https://github.com/yujian777555/agentfotagent
- Exact source commit checked out: ec73906e15c048285cff3bca90a4f1f8bed21da8
- R2 merge commit: 2d5209dfac7b1fd1348ee04ebaf0a3f9bfefef39
- Workflow branch: audit/reproduce-phase0-r2-tests
- Workflow commit: 20f99a86c36743a3aab0703e6a563d119e89f710
- GitHub Actions run: https://github.com/yujian777555/agentfotagent/actions/runs/40453697835
- Artifact: https://github.com/yujian777555/agentfotagent/actions/runs/40453697835/artifacts/12711107094
- Runtime: GitHub-hosted Ubuntu runner, Python 3.11.17
- Command: python -m pytest tests -o addopts='' -q -ra
- Test output: 127 passed in 0.43s

The workflow checked out the exact source SHA ec73906e15c048285cff3bca90a4f1f8bed21da8 before installing dependencies and running the suite. The workflow branch and its commits are isolated from main.

## Adversarial probes executed against the same source tree

1. Runtime-ID enumeration: a dial_set dev task with seed 17 had runtime ID rt_7b72f14d92fb4a4c; enumerating candidate seeds 0–100 using the public generator recovered seed 17.
2. Malformed relay goal: code=None and frequency=99 with an activated relay at frequency 99 returned success=True.
3. Malformed key_crate state: statue/crate records missing required entity types and no pedestal object returned success=True.
4. Manifest metric tampering: changing recorded invalid_actions from 0 to 999999 was accepted by reconstruct_from_artifacts with mismatches=[].

The latest run log records all four probe outputs. The artifact includes the pytest output and adversarial-probe log.

## Interpretation

The 127-test suite passes, but the probes identify uncovered correctness/integrity failures. These are not failures of the existing test suite; they are reasons the environment is not yet accepted. No implementation source was modified by this reproduction. No live LLM API, GPU, MetaBox, transfer or scientific baseline experiment was run.

See docs/PHASE0_R2_INDEPENDENT_REVIEW_2026-10-27.md for the complete findings and required fixes.
