# Phase-1A-17 Executor Handoff — Audit Cross-Domain EC Controller Transfer

You are the Executor for yujian777555/agentfotagent. Use only this repository. Do not mix code, data, or conclusions from openissue, EvoPareto-Agent, CausalEvo-DSH, GLEPPO, or other independent projects.

## Read first
1. status.json
2. docs/PROJECT_CHARTER.md
3. docs/RESEARCH_DECISIONS.md (D-024 onward)
4. docs/PHASE1A15_RESEARCH_OBJECT_COMPARISON.md
5. docs/PHASE1A15_ADJACENT_EC_LITERATURE_MATRIX.md
6. docs/PHASE1A15_DECISION.md
7. docs/PHASE1A16_TYPED_CONTRACT_GP_AUDIT.md
8. docs/PHASE1A16_CANDIDATE_DECISION.md
9. docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md

## Fixed objective
Ultimately apply a genuinely useful LLM-empowered evolutionary-computation method to improve Agent task performance. No novelty, transfer, or performance gain is presumed. AES remains an engineering scaffold; MetaBox is source-domain infrastructure, not a contribution.

## Phase-1A-16 result
Generic typed/contract-aware GP variation is NO-GO as a new-method claim. It overlaps strongly typed GP, grammar-guided GP, semantic GP, GenProg, proof-guided genetic improvement, LLM-seeded many-objective grammar-GP, program synthesis, and safe policy synthesis. Do not revive it by renaming the combination.

## Phase-1A-17 research question
Can one **frozen, explicit evolutionary-control policy** discovered on a numerical optimization source domain be transferred to the target domain of evolutionary search over executable Agent policies, without redesigning the controller after seeing target outcomes?

## Required comparison
Audit primary sources on:
- adaptive operator selection and hyper-heuristics with transfer across tasks/problems;
- multi-task evolutionary algorithms and explicit transfer operators;
- meta-learning of optimizers and learned optimizers across objective families;
- cross-domain transfer of Agent/Harness/search controllers, including Harmony Harness, MaAS, AgentSwift, AEL and adjacent recent works;
- negative transfer, state/action representation alignment and domain randomization.

For every work record exact state, action, controller representation, reward/credit signal, transfer map, what is trained on source/target, and baseline that isolates transfer from target-specific learning.

## Required formalization before any candidate is admitted
Write a frozen tuple:
- source state features S_src;
- target state features S_tgt;
- shared abstract state Z;
- source actions A_src;
- target actions A_tgt;
- fixed mapping phi_s: S_src -> Z, phi_t: S_tgt -> Z;
- fixed action mapping psi_src, psi_tgt or a proof that action labels are semantically shared;
- controller representation and update rule;
- source training tasks, target development tasks, and untouched target test families.

If these mappings require target-specific redesign after observing results, that is not direct transfer. A frozen mapping may be developed using source and development data only; test data must remain sealed.

## Required negative controls
At minimum:
1. target-only strong controller / standard AOS;
2. random controller;
3. source controller with shuffled state-feature mapping;
4. source controller with shuffled action mapping;
5. frozen source controller without target adaptation;
6. equal-budget target-trained controller;
7. standard EA/GP/random valid-genome search over the same target policy space.

Transfer must improve target Agent task performance, not merely source MetaBox score, controller validation score, syntactic validity, or runtime compliance.

## Admission gate
Admit at most one candidate only if:
- there is a precise transferable object and fixed mapping;
- nearest transfer/hyper-heuristic literature does not already cover the mechanism;
- source-to-target benefit is falsifiable and not explained by target training budget;
- negative-transfer behavior is measurable;
- target evaluation can be performed later without leakage;
- the controller has a concrete EC role and not only an LLM-written prompt.

If no candidate survives, record NO-GO and stop candidate generation. Do not run experiments in this phase.

## Hard limits
- No implementation.
- No real LLM API calls.
- No MetaBox runs.
- No AES scientific runs.
- No GPU.
- No held-out/test access.
- If a future phase separately authorizes API use, use deepseek-flash only, never deepseek-v4-pro.

## Required outputs
- docs/PHASE1A17_TRANSFER_LITERATURE_MATRIX.md
- docs/PHASE1A17_STATE_ACTION_ALIGNMENT.md
- docs/PHASE1A17_DECISION.md
- Update status.json and docs/RESEARCH_DECISIONS.md.
