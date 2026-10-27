# Independent Phase-0-R2 Review — 2026-10-27

## Verdict

**REQUEST CHANGES — Phase-0 remains NOT ACCEPTED.**

- Repository: https://github.com/yujian777555/agentfotagent
- Exact R2 source tree reviewed: ec73906e15c048285cff3bca90a4f1f8bed21da8
- R2 merge commit: 2d5209dfac7b1fd1348ee04ebaf0a3f9bfefef39
- R1 reproduction history preserved: commits fd6c5e42cfd3c95c814419c0f2f21f27a664d5dd and acd9193614980bc41eaba15632e0a3329d2fc101 are ancestors of the merge.
- R2 corrective commits preserved in the merge first-parent history: 9eac76015fb254633ab0f01c169d4d34c99884cc, 8370fc3e469e768bdb4bf856c53db274e62e3f08, 0278eba671aff7797f26fed7676e8277c2fde173, 7424046c25b154e91ef5c3512c8aa0d4d399d8a3.
- No source code was modified by this review. The only changes to the repository after review are documentation/status updates recording the findings.
- No live LLM API, GPU, MetaBox, transfer or scientific baseline experiment was run.

## Independent full-suite reproduction

GitHub Actions run: https://github.com/yujian777555/agentfotagent/actions/runs/40453697835

- Exact source checked out by runner: ec73906e15c048285cff3bca90a4f1f8bed21da8
- Workflow branch: audit/reproduce-phase0-r2-tests
- Workflow commit: 20f99a86c36743a3aab0703e6a563d119e89f710
- Runtime: GitHub-hosted Ubuntu runner, Python 3.11.17
- Command: python -m pytest tests -o addopts='' -q -ra
- Result: **127 passed in 0.43s**, exit status 0
- Artifact: https://github.com/yujian777555/agentfotagent/actions/runs/40453697835/artifacts/12711107094

The run independently confirms that the existing test suite passes on the exact R2 source tree. The same workflow executed adversarial diagnostic probes; those uncovered cases below are not covered by the current tests. A green test suite does not override a reproducible counterexample.

## Findings

### R2-01 / R1-01 — Runtime ID is deterministic and seed-recoverable

**Severity: MAJOR — REQUEST CHANGES**

In src/agentfotagent/tasks/generators.py, runtime_id is calculated as the first 16 hexadecimal characters of SHA-256(content_hash). The content hash is deterministically derived from the public generator's task family, seed, generated setup, hidden goal and description. This hides the metadata lexically but does not make the identifier opaque against a finite seed search.

Adversarial probe on the exact source tree:
- Target task: dial_set, seed 17, split dev
- Runtime ID: rt_7b72f14d92fb4a4c
- Enumerating candidate seeds 0–100 through the public generator recovered seed 17.

The probe ran in the GitHub Actions log above. The current payload test checks that the ID contains no readable family/split/seed substring; it does not test whether the public deterministic generator can recover the seed from the digest. Since task generation is deterministic and the seed domain is small, the ID can serve as a lookup key into precomputed hidden-task metadata.

**Required fix:** use a genuinely opaque per-instance token or a keyed identifier whose secret is not available to the Agent. Keep deterministic evaluation identity/content hashes on the evaluation side. If runtime IDs are random, exclude them from deterministic task-manifest identity/hash calculations or otherwise explicitly separate stable evaluation manifests from runtime tokens. Add a regression probe that enumerates the declared seed domain and demonstrates that the runtime ID cannot be mapped back to family/seed metadata.

### R2-02 / R1-04 — Relay goal schema accepts malformed values

**Severity: MAJOR — REQUEST CHANGES**

In src/agentfotagent/evaluation/evaluator.py, _pred_relay_route checks that code and frequency keys exist and that frequency is an integer (not bool). It does not validate that code is a three-digit string, that frequency is in the generated domain 1–7, or that the frequency is consistent with the code formula. The code field is otherwise unused by the predicate.

Adversarial probe:
- Goal: type=relay_route, code=None, frequency=99
- State: valid relay object, activated=True, relay frequency=99
- Evaluator result: success=True.

This directly contradicts the claim that malformed relay goal schemas fail closed.

**Required fix:** validate code type and exact digit format; validate frequency as a non-bool integer in 1–7; verify code/frequency consistency under the specified formula (or validate all canonical required goal fields consistently). Add regression cases for None, wrong types, malformed digit strings, out-of-range frequency and inconsistent code/frequency pairs.

### R2-03 / R1-04 — key_crate evaluator accepts entity records without required types

**Severity: MAJOR — REQUEST CHANGES**

In _pred_key_crate, the evaluator checks that the statue and crate values are mappings and checks their locations/unlocked flag, but it does not validate their required entity types or require a valid pedestal/surface record.

Adversarial probe on the exact source tree:
- objects.statue = {location: pedestal} (no type)
- objects.crate = {unlocked: true} (no type)
- no pedestal object record
- Evaluator result: success=True.

The predicate therefore accepts a malformed final state even though the project claims fail-closed entity validation.

**Required fix:** require the target artifact and crate records to have the expected types, require the referenced surface object to exist with the expected surface type, and validate the necessary locations/flags. Add missing-type and wrong-type regression tests while preserving valid generated happy paths.

### R2-04 / R1-05 — Artifact reconstruction ignores some recorded score fields

**Severity: MAJOR — REQUEST CHANGES**

In src/agentfotagent/evaluation/provenance.py, reconstruct_from_artifacts enforces trace/score identity correspondence and compares the rebuilt success and steps values. It does not compare all recorded fields, including invalid_actions, repeated_states and termination_reason.

Adversarial probe:
- Original manifest invalid_actions: 0
- Tampered manifest invalid_actions: 999999
- Reconstruct result: accepted, mismatches=[].

Thus trace/score bijection is improved, but the recorded score is not fully reconstructed or validated. An artifact can retain a valid task/genome/final-state identity and success/steps while carrying false diagnostic metrics.

**Required fix:** compare every persisted score field against the rebuilt EpisodeResult, with strict type/missing-field handling. Add tampering tests for success, steps, invalid_actions, repeated_states, termination_reason and final_state_hash; each inconsistent artifact must raise ReconstructionError.

## Status of R1 residual findings

| Original finding | R2 status after independent review |
|---|---|
| R1-01 runtime metadata isolation | PARTIAL — deterministic runtime ID allows seed recovery |
| R1-02 relay verification | No new counterexample found in this pass; existing test suite passes |
| R1-03 missing relay object | No new missing-object bypass found in reviewed tool/evaluator paths; entity schema validation remains incomplete under R2-03 |
| R1-04 fail-closed goal/state validation | PARTIAL — malformed relay goals and malformed key_crate entity records can pass |
| R1-05 trace/score reconstruction | PARTIAL — bijection and run isolation added, but persisted diagnostic metrics can be tampered |
| R1-06 version/provenance identifiers | Version constants and source_commit_sha are present; no blocker found in this pass |

## Required next pass

1. Fix R2-01 through R2-04 and add adversarial regression tests.
2. Run the full suite on the corrected source commit and record exact SHA, runtime and complete output.
3. Update the R2 response matrix, environment spec, planner and status.json.
4. Push without force and verify remote HEAD.
5. Stop for another independent review.

**Stop condition:** Phase-0 is not accepted. No transfer experiment, MetaBox meta-training, live API call, GPU run or scientific baseline comparison is authorized until these issues are fixed and the next independent review accepts the environment.
