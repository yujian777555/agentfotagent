# Independent Phase-0 AES Audit — 2026-10-26

- Repository: https://github.com/yujian777555/agentfotagent
- Audited source commit: \`987df6dbb21683331968f09acf6160fbbdf005bb\`
- Audit mode: independent static source/test review via the connected GitHub repository
- Verdict: **REQUEST CHANGES — Phase-0 gate not yet accepted**
- Execution status: the executor reports 56/56 tests passing. I could not independently rerun pytest in this audit environment because cloning the repository failed at network resolution; therefore the test count is recorded as executor-reported, not independently reproduced.
- No code was modified in this audit, no API was called, and no scientific experiment was run.

## What looks sound

1. The repository owns the AES implementation; the two unrelated predecessor projects are not imported as runtime dependencies.
2. The normalized four-gene space has 16 canonical genotypes, and both baseline implementations call the same \`BaselineHarness.evaluate_genome\` path.
3. Public observations omit the hidden goal and do not expose the global object map.
4. The primary evaluator mostly scores world state rather than the Agent's self-report.
5. The cache key includes task ID, task content hash, split, genome, backend, config, environment and evaluator versions.
6. The task split configuration separates \`relay_route\` from train/dev at the family-label level.

These are useful scaffold properties, but they do not offset the blocking semantics and provenance gaps below.

## Blocking findings

### F1 — Tool-world preconditions permit state teleportation

**Severity: BLOCKER**

Source: \`src/agentfotagent/environments/tool_world.py\`, methods \`_tool_place\`, \`_tool_unlock\`, \`_tool_set_dial\`, \`_tool_activate_relay\`, and \`_tool_set_frequency\`.

- \`_tool_place\` checks that the object is held and the destination is named in the task's valid destinations, but does not require the destination surface/room to be local to the Agent.
- \`_tool_unlock\` does not require the Agent to be at the locked object's location. When it releases contents, it places them at the **unlocker's current location**, not the container's location.
- \`_tool_set_dial\` does not require the Agent to be at the calibration console.
- \`_tool_activate_relay\` and \`_tool_set_frequency\` do not require the Agent to be at the relay's location.
- Related read tools should also have explicit location/precondition contracts where the task design requires a console/card.

**Why it matters:** a \`key_crate\` episode can take a key in one room, unlock the crate from that room, receive the statue at that room, and place it on the pedestal remotely. It need not visit the vault or return to the hall. Relay activation/frequency can likewise be changed from outside the hub. The current mock policy may voluntarily take extra steps, but the environment does not enforce the claimed task semantics. This makes the evaluator reward invalid shortcuts and weakens the meaning of multi-step tool use.

**Required fix:** define explicit preconditions for each tool and enforce them in the environment. A state-changing action must not mutate state when a precondition fails. Unlocking should require local access to the container and release its contents at the container's actual location. Placing an item should require the destination surface to be at the current location (or require the Agent to move to the destination). Dial/relay tools should require local access to their console/relay. Add adversarial tests that deliberately attempt each shortcut and assert failure with no state mutation beyond the step counter.

### F2 — Planning and verification genes alter the trace but do not yet implement their stated semantics

**Severity: BLOCKER for the gene-behavior gate**

Source: \`src/agentfotagent/runtime/mock_backend.py\` (\`MockPolicy.next_action\`, \`_derive_plan\`) and \`src/agentfotagent/runtime/phenotype.py\`.

- \`planning_mode=plan_first\` emits \`make_plan\` and stores a family-specific plan, but subsequent action selection goes straight back to the hard-coded solver. The stored plan is not read or used to choose the next action. Current tests prove an extra action was emitted, not that planning changes execution decisions.
- \`verification_policy=check_before_finalize\` sets \`verified=True\` before calling \`verify_state\`; the returned summary is not used to decide whether to submit or repair the state. The next policy call can submit regardless of what verification returned. This is an inserted trace event, not a functioning verification policy.
- The memory behavior is partly controlled by a direct branch on the genome in \`MockPolicy._explore_rooms\`, while the phenotype's \`recall()\` is not used to determine the next action. The current test proves memory storage and trace differences, but not an end-to-end memory-mediated decision.

**Required fix:** either wire the declared semantics end to end or narrow the gene names/claims to exactly what is implemented. At minimum:
- plan-first must create a plan that is consumed/validated by later decisions, with a test where a changed plan changes the selected next action;
- verification must inspect the returned public state summary and block finalization or trigger correction when the goal state is not satisfied;
- memory-enabled decisions must use the phenotype's bounded memory interface rather than a separate hidden list that simply branches on the genotype.
Tests must fail if only an extra trace event is added without changing the intended decision logic.

### F3 — PublicTask exposes deterministic task-generation metadata

**Severity: MAJOR leakage risk before any held-out experiment**

Source: \`src/agentfotagent/interfaces.py\`, \`PublicTask\` includes \`seed\`, \`generator_version\`, and \`content_hash\`; task generation is deterministic and its implementation is in the same repository.

The current mock policy receives \`PublicTask\` (though the generic \`AgentBackend.propose\` currently receives only observation/context). If future runtime adapters expose this object, the task seed and generator identity provide unnecessary information that can help reconstruct a held-out instance. The hidden-goal unit tests only inspect observation/tool results; they do not assert that the actual model-facing payload excludes seed metadata.

**Required fix:** separate evaluator-side \`TaskRecord\` metadata from the runtime-facing task description. Keep seeds, hidden hashes, split manifests and generator metadata in the evaluation/provenance layer. The model-facing payload should contain only the task instruction and the observation data it is permitted to see. Add a test over the exact object serialized to a backend, not only \`Observation.content\`.

### F4 — The baseline harness does not preserve reconstructable raw episode traces

**Severity: BLOCKER for the provenance/reconstruction gate**

Source: \`src/agentfotagent/evolution/harness.py\`, \`BaselineHarness.evaluate_genome\` and \`build_manifest\`; \`src/agentfotagent/evaluation/provenance.py\`.

- \`evaluate_genome\` receives \`trace\` from \`run_episode\` but discards it, retaining only \`EpisodeResult\` in the cache and \`SearchRecord\`.
- \`build_manifest\` creates replacement \`EpisodeTrace\` objects with blank \`split\` and a synthetic \`final_state\` containing only \`step\` and \`termination_reason\`; it does not preserve the actual final state or per-step trace.
- \`RunManifest\` stores episode IDs and score summaries, not raw trace contents.
- The existing provenance test reconstructs a direct \`run_episode\` trace; it does not exercise the baseline-harness path that a search run uses.
- The comment says the representative genome hash is the best record's hash, but the implementation uses \`records[0]\`.

**Required fix:** retain/write the actual \`EpisodeTrace\` for every uncached evaluation, preserve split and full final state, and persist a run artifact containing trace references/content hashes plus the manifest. Add an end-to-end test that runs an algorithm through \`BaselineHarness\`, serializes its artifacts, reloads them, reconstructs every score from the exact task manifest and evaluator, and compares results and hashes. Fix the representative-genome selection/comment mismatch.

### F5 — Evaluator does not fail closed on malformed key-crate state

**Severity: MAJOR evaluator robustness issue**

Source: \`src/agentfotagent/evaluation/evaluator.py\`, \`StateBasedEvaluator.success_predicate\`.

For \`key_crate\`, a missing crate object defaults to \`{}\`; \`not bool(crate.get("locked"))\` then evaluates to true. A malformed final state with the target object on the surface but no crate record can therefore pass the crate-unlocked requirement. Also, a malformed \`dial_set\` goal with an empty target map would pass because \`all([])\` is true.

**Required fix:** validate the expected state schema and required entities before scoring. Missing crate/target/dial/relay fields, empty goal definitions, malformed values, or unknown schema must return failure (or an explicit evaluator error recorded as failure), never success. Add regression tests for missing and empty state fields.

## Additional concerns — must resolve before scientific baselines

### C1 — Random search and EA can repeatedly sample the same genome

\`RandomSearch.run\` samples with replacement and creates a \`seen\` set that is never used. \`ConventionalEA\` can also generate duplicate genotypes. Since \`BaselineHarness\` caches scores, repeated genotypes may become cheap cache hits while the algorithms still consume the same nominal candidate-call budget.

This is acceptable as a prototype, but not yet a fair scientific comparison by evaluation effort. Before any research run, define whether budget means candidate proposals, unique genome-task evaluations, or actual uncached environment episodes; report proposal count, unique genomes, cache hits and actual episodes. Add duplicate handling or explicitly normalize/report the effective evaluation cost.

### C2 — Held-out family is an engineering split, not yet confirmatory generalization evidence

The configured held-out set has three \`relay_route\` instances from one known in-repository generator. The family labels are disjoint, which is good, but the generator/logic is visible and the mock policy contains a dedicated \`relay_route\` solver. This proves split plumbing, not transfer/generalization. Do not use these three mock episodes as evidence of cross-family Agent capability. Keep this set as a smoke test; before a scientific claim, freeze a stronger family-level evaluation plan and add external validation after the environment gates pass.

### C3 — Phase-0 tests do not cover the adversarial tool preconditions or the end-to-end harness artifact

The current tests verify several isolated contracts but miss the shortcuts and serialization gaps identified above. The reported 56/56 result must remain labelled executor-reported until it is rerun from the pushed commit in a reproducible environment.

## Required acceptance gate

Phase-0 can be accepted only after:
1. Tool preconditions prevent the remote unlock/place/dial/relay shortcuts.
2. Planning, verification and memory genes implement their declared decision semantics end to end.
3. The model-facing payload excludes task seeds and evaluator-side metadata.
4. Search-run artifacts preserve full traces and can reconstruct all scores end to end.
5. The evaluator fails closed on malformed state/goal structures.
6. New regression tests cover each finding, and the full test suite is rerun on the resulting commit.

Until then, keep the phase status at **REQUEST_CHANGES / AWAITING_FIXES**. Do not start transfer-object experiments, MetaBox meta-training, GPU runs or live LLM calls.
