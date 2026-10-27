# Project-Owned Experimental Environment Specification

- Project: Agent-for-Agent (yujian777555/agentfotagent)
- Date: 2026-10-26
- Status: Phase-0 AES scaffold implemented (engineering tests only); no scientific experiments authorized
- Working name: **Agent Evolution Sandbox (AES)**. This is an internal project name, not a novelty claim.
- Implementation root: `src/agentfotagent/` (layout below); tests in `tests/`; configs in `configs/`.

## 1. Decision and boundary

The project must own its experiment harness and its target-domain Agent-evolution environment. NeuroEvoScientist and EvoPareto-Agent are external projects and may be consulted only as prior-art/code-audit references; they are not candidate runtime environments, code dependencies, or sources of experimental results for this repository.

The project does not need to reimplement every underlying optimizer or public benchmark from scratch:
- **Source domain:** use MetaBox-v2 as the standardized numerical/meta-black-box optimization substrate, with pinned version/configuration and our own adapters, experiment protocol, candidate controller, baselines and logs.
- **Target domain:** implement an in-repository, controlled multi-step tool-use environment and Agent phenotype/genotype runtime, designed and audited by this project.
- **External validity:** after the controlled environment passes its validity gates, add a separate adapter to a published Agent benchmark/environment if useful. Such a benchmark is an external validation set, not a substitute for our own target environment.
- **Shared harness:** this repository owns experiment orchestration, seeds, task manifests, model/backend interfaces, scoring, cache namespaces, budget/provenance records, statistical analysis and immutable result manifests.

MetaBox is infrastructure, not a contribution. The in-repository AES is also not automatically a research contribution; it exists to make the proposed method testable and reproducible.

## 2. Scientific question supported by the environment

Can an Agent-derived evolutionary-control mechanism, validated on source-domain optimization tasks, improve evolutionary search over executable Agent configurations in a separate target domain? If that transfer works, does feedback from target-domain evolution add measurable benefit beyond one-way transfer?

This is a hypothesis, not an expected outcome. Generic LLM-based operator selection and generic bidirectional self-improvement are already crowded areas. The environment must make it possible to reject the hypothesis.

## 3. System layout

The first implementation should use a small, explicit package rather than importing code from predecessor repositories:

- src/agentfotagent/interfaces.py: contracts for task environments, Agent backends, phenotype execution and evaluation.
- src/agentfotagent/genome/schema.py: canonical, versioned Agent genome and normalization.
- src/agentfotagent/runtime/: compile a genome into executable runtime behavior.
- src/agentfotagent/environments/tool_world.py: deterministic, sandboxed, multi-step tool-use world.
- src/agentfotagent/tasks/: procedural task generators, task-family identifiers, split manifests and hidden-goal definitions.
- src/agentfotagent/evaluation/: goal-state-based primary score, step/error/cost metrics, fail-closed validation and provenance.
- src/agentfotagent/evolution/: adapters for standard evolutionary algorithms and random search; do not implement a new NSGA-III before the research method is approved.
- src/agentfotagent/metabox_adapter/: thin, version-pinned integration with MetaBox-v2 for the source domain.
- src/agentfotagent/transfer/: reserved for the selected transfer object after its semantics are approved.
- configs/: task splits, model/backend configuration, seed lists, evaluation protocol and baseline settings.
- tests/: behavioral contract tests, evaluator tests, leakage tests, determinism tests and baseline fairness tests.
- results/: append-only run manifests, raw trajectories, checksums and analysis outputs. Never store secrets.

Names can change during implementation, but the boundaries and evidence requirements must remain.

### 3.1 Phase-0 implementation notes (2026-10-26)

The scaffold now exists under `src/agentfotagent/` with the boundaries above.
Frozen engineering decisions for this phase:

- Genome schema `aes-genome-v1`: four genes (planning_mode, memory_policy,
  verification_policy, tool_selection_policy); memory window is fixed at 4 and is
  **not** a gene (avoids budget confounds).
- Environment `aes-tool-world-v1`: public observations are **local only**
  (current location, inventory, visible objects, current dial values, public relay
  status, notes after they are read). Global object maps and hidden goals are not
  in the Agent-visible projection.
- Task generator `aes-task-gen-v1` families:
  - `key_crate` — train/dev: find a key among decoy coins, unlock a crate, place artifact.
  - `dial_set` — train/dev: read gauges + offset card, compute and set three dials.
  - `relay_route` — held-out only: assemble a code from notes, activate relay, set frequency.
- Evaluator `aes-evaluator-v1`: primary success is a predicate over terminal
  environment state only; self-reports in the trace are recorded for audit and ignored.
- Mock backend `mock-engineering-v1` is used by all Phase-0 tests. Mock results are
  engineering evidence only and are never Agent capability evidence.

## 4. Initial Agent genotype and phenotype contract

Start with a deliberately small, auditable genotype. Candidate genes below are design proposals, not yet frozen:

1. planning_mode: direct execution vs explicit plan-first execution.
2. memory_policy: no carry-over vs bounded episodic retrieval from the current episode's permitted observations.
3. verification_policy: no verification vs goal-condition/check-before-finalization.
4. tool_selection_policy: fixed deterministic ranking vs state/goal-conditioned ranking.

The evaluator should hold the maximum interaction limit fixed across methods; do not make budget allocation the contribution or allow the genome to win merely by receiving a larger budget. A gene is admissible only if an intervention test shows that changing it changes the intended runtime behavior on at least one diagnostic task, and a normalization test proves inactive/duplicate values are canonicalized.

The runtime must separate:
- **genotype:** serialized policy choices;
- **phenotype:** compiled prompts, memory policy, action-ranking logic and verification behavior;
- **execution trace:** observations, proposed actions, actual tool calls, state transitions, termination reason and model/backend provenance.

A mock backend is permitted for interface and unit tests only. Mock/synthetic scores must never be described as Agent capability evidence. Actual capability experiments require an approved real backend and a task evaluator with verifiable outcomes.

## 5. Initial target environment: controlled tool-use world

The initial environment should be small and deterministic, not an unbounded imitation of the real world. It should contain:
- a hidden goal specification and explicit success predicate;
- a typed tool API with read-only information tools and state-changing tools;
- multi-step tasks requiring information gathering, planning, action selection and final-state verification;
- invalid-action handling, explicit terminal states and reproducible reset/step semantics;
- procedurally generated task instances with family-level train/development/held-out splits;
- task manifests with generator version, seed, task-family ID and content hash.

Avoid tasks where the answer can be obtained from a single superficial cue. Avoid letting the Agent inspect hidden goal state or evaluator internals. Task-generation parameters and held-out families must be frozen before confirmatory evaluation. Use public, documented task generators and human-readable task definitions so solvability and difficulty can be audited.

The controlled world is for causal diagnosis and repeatable method development. Before claiming broad Agent improvement, add an external validation adapter to an appropriate published interactive-agent benchmark, using its official task/evaluation definitions where possible. Do not merge external test feedback into method development.

## 6. Unified scoring and baseline contract

Primary metric: **verified task success rate** computed from the environment's final state and task-specific success predicate.

Secondary diagnostics:
- number of tool calls / environment steps;
- invalid action rate and repeated-state rate;
- token and API cost, only when measured from actual backend usage;
- completion latency;
- robustness across seeds and held-out task families.

Never substitute a hand-written genome prior, proxy capability score, progress heuristic or cost of failure for task success. Incomplete/invalid runs remain visible and cannot silently fall back to mock results.

Minimum comparison arms, frozen before confirmatory evaluation:
1. fixed hand-designed Agent policy;
2. random search over the exact same normalized genome space;
3. a conventional target-domain evolutionary baseline;
4. a strong target-only adaptive controller tuned only on development tasks;
5. source-domain-derived transfer controller;
6. transfer-disabled ablation;
7. shuffled state/action mapping negative control.

All arms share task manifests, backend/model version, environment version, maximum interaction limit, caching rules and evaluation protocol. The controller may be selected on development tasks only; held-out task families are read once for confirmation. Report multiple seeds and uncertainty, not only best runs.

## 7. Two-domain research protocol

### Stage A — source-domain validation with MetaBox-v2
- Pin the MetaBox-v2 commit/version and source task suite.
- Compare the Agent-assisted evolutionary-control method with standard evolutionary/adaptive baselines, not just random search.
- Separate controller discovery, selection and final source-domain test instances.
- Store source states/actions/rewards and controller artifacts with hashes.
- Do not call a generic LLM operator-selection prompt a contribution.

### Stage B — target-domain evolution in AES
- Evolve the project's own Agent genome/phenotype, with real success predicates.
- Establish genome behavioral validity, task solvability and baseline strength before testing transfer.
- Apply the selected transfer object through an explicit, documented interface; do not silently hand-write a target-specific policy.
- Compare transfer with target-only tuning, fixed controller, random search and shuffled mapping.

### Stage C — optional feedback loop
Only begin if Stage B shows a reproducible transfer benefit. Then test whether target-domain evolutionary traces improve the source-derived controller beyond one-way transfer. Include a no-feedback ablation and a frozen held-out task family. If no incremental benefit appears, remove the feedback-loop claim.

## 8. Phase-0 engineering gates before scientific experiments

The first code phase is an environment scaffold, not an algorithm-performance experiment. It passes only if:

- changing each active gene demonstrably changes its intended runtime behavior;
- task success is computed from the environment's state, not from the Agent's self-report;
- identical seed/configuration reproduces task instances and deterministic environment transitions;
- task split hashes and task-family isolation can be independently reconstructed;
- test/hidden goal state is inaccessible to the runtime Agent;
- cache keys include task, genome/phenotype, backend/model and relevant configuration; held-out evaluation cannot reuse development outputs;
- random search and conventional EA share the exact same evaluation path and effective search space;
- invalid backend responses, missing outputs and environment errors fail closed and remain in the ledger;
- all raw traces and run manifests contain enough provenance to reconstruct scores;
- unit tests use mock backends but label results as engineering-only.

No live LLM calls, GPU benchmark runs or MetaBox meta-training are authorized by this specification. Those require a later, separately reviewed experiment plan.

### 8.1 Phase-0 gate status (engineering tests, 2026-10-26)

| Gate | Status | Evidence |
| --- | --- | --- |
| Gene intervention | PASS | `tests/test_gene_interventions.py` |
| Success from env state | PASS | `tests/test_evaluator_state_based.py` |
| Determinism | PASS | `tests/test_determinism.py` |
| Split / family isolation | PASS | `tests/test_isolation_and_failclosed.py` |
| Hidden-goal leakage | PASS | `tests/test_leakage.py` |
| Cache isolation | PASS | `tests/test_isolation_and_failclosed.py` |
| Baseline fairness | PASS | `tests/test_baseline_fairness.py` |
| Fail-closed errors | PASS | `tests/test_isolation_and_failclosed.py` |
| Provenance reconstruction | PASS | `tests/test_provenance_reconstruction.py` |
| Mock labelled engineering-only | PASS | package docstrings + `engineering_only` flags |

Known limitations of this phase (not gates, but must be visible):
- The mock backend is a scripted policy. It demonstrates gene observability and
  evaluator correctness; it says nothing about LLM-Agent capability.
- External-validation adapter to a published interactive-agent benchmark is not
  implemented (explicitly out of Phase-0 scope).
- Token/API cost metrics are defined in the contract but unmeasured (no live backend).

## 9. Risks and falsification

- **Synthetic-world overfitting:** use task-family holdouts and later external validation; if results do not transfer, narrow claims.
- **Decorative genes:** reject any gene without an observed execution effect.
- **Evaluator leakage:** keep hidden goals and held-out task manifests outside the Agent runtime and freeze hashes.
- **Baseline weakness:** if a simple target-only controller matches transfer, H2 is not supported.
- **Mapping artifact:** if shuffled mappings retain the same benefit, the claimed semantic transfer mechanism is not supported.
- **No source-to-target benefit:** stop or pivot H2 rather than continuing into recursive feedback.
- **No feedback increment:** remove H3; complexity is not evidence.

## 10. Public references informing the boundary

- MetaBox-v2 (NeurIPS 2025 Datasets and Benchmarks Track): https://papers.nips.cc/paper_files/paper/2025/hash/dcb23dcf61a943df050b7b4d94da1b29-Abstract-Datasets_and_Benchmarks_Track.html
- AgentBench (ICLR 2024): https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html

These references support the use of standardized optimization tasks and verifiable interactive-agent evaluation; they do not imply that AES is novel or that the proposed transfer hypothesis will work.


### 8.2 Independent audit status (2026-10-26)

The executor reported 56 passing engineering tests, but independent static source review of commit `987df6dbb21683331968f09acf6160fbbdf005bb` returned **REQUEST CHANGES**. The test count could not be independently rerun in the audit environment. Blocking issues: (1) world tools permit remote unlock/place/dial/relay actions and state teleportation; (2) planning/verification/memory genes are not fully wired into downstream decisions; (3) model-facing task metadata includes deterministic seed/generator information; (4) the search harness drops actual traces and creates incomplete synthetic traces for manifests; (5) malformed evaluator state can pass success predicates. See `docs/PHASE0_INDEPENDENT_AUDIT_2026-10-26.md` for evidence and required regression tests.

No scientific experiments, live APIs, GPU runs or MetaBox meta-training are authorized until the corrective pass is independently accepted.

### 8.3 Phase-0-R1 corrective pass (2026-10-26)

Audit findings F1-F5 and concern C1 were repaired in-repository. Summary:

- **F1 tool preconditions:** unlock/place/set_dial/read_gauge/read_offset_card/activate_relay/set_frequency require interactive locality; unlock releases contained objects at the container location; failed actions do not mutate business state (step counter only).
- **F2 gene semantics:** planning_mode=plan_first stores a plan consumed by phase gates (changing the plan changes the next action); verification_policy=check_before_finalize reads verify_state output and blocks submit until public goal checks pass; memory_policy=bounded_episodic search uses phenotype.recall() only.
- **F3 runtime metadata:** RuntimeTask = {task_id, description, max_steps}; seeds/generator/hashes/split/hidden goals stay on the evaluation-side TaskInstance. Tests assert the exact backend payload.
- **F4 provenance:** BaselineHarness retains actual EpisodeTraces; manifests use those traces and the best record genome hash; reconstruct_from_artifacts rebuilds every score after JSON round-trip.
- **F5 fail-closed evaluator:** missing crate/target/dial/relay entities, empty dial goals, malformed values and unknown goal types return failure.
- **C1 accounting:** runs record candidate_proposals, unique_genomes, cache_hits, actual_episode_executions, task_evaluations. Cache hits are never counted as new episodes.

Response matrix: docs/PHASE0_R1_AUDIT_RESPONSE.md. C2 (held-out family is smoke-test only) is acknowledged as a later-phase limitation, not a Phase-0 code gate.

Awaiting independent re-review. Still no scientific experiments, live APIs, GPU runs or MetaBox meta-training.
