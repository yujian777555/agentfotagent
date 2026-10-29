# Phase-1A-18 Follow-up — EVOTOOL Blame-to-Intervention Alignment Audit

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Status: **PRELIMINARY_SOURCE_GROUNDED_LEAD; NOT_REOPENED**
- Scope: read-only paper/source/replay-data audit. No project code was changed for an experiment; no live LLM request, MetaBox/AES scientific run, GPU job, or held-out task access occurred.

## 1. Why this follow-up was conducted

Phase-1A-18 paused the current Agent×EC method-discovery route because no candidate had survived the recent prior-work gates. Rather than invent another algorithm name, this follow-up inspected one primary Agent-evolution method and its released generation-by-generation record to ask a narrower question:

**Does the module identified as responsible for a failure also tend to be the module whose mutation produces a useful evolutionary improvement?**

This is a source-grounded failure-mode audit, not a new method proposal and not permission to resume experiments.

## 2. Frozen source snapshot

### Paper

Yang, S., Han, C., Ma, X., Li, Y., Ghasemi Madani, M. R., & Hovy, E. (2026). EVOTOOL: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection. *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL 2026), Volume 1: Long Papers*, 43553–43572. https://doi.org/10.18653/v1/2026.acl-long.2016

The paper describes four policy modules (Planner, Selector, Caller, Synthesizer). The Blamer assigns module-level responsibility from a trajectory; the Mutator edits the selected module; diversity-aware selection preserves candidates that win on at least one selection instance. See the [ACL paper](https://aclanthology.org/2026.acl-long.2016/) and [PDF](https://aclanthology.org/2026.acl-long.2016.pdf), especially the method description and Algorithm 1.

### Official code and run record

- Official repository: https://github.com/SYang2000/ACL_2026_EvoTool
- Frozen repository HEAD: **6a82719ea6e22cf23f963078e2527094e50b47f6**
- CASE_STUDY.md blob SHA: **5b7b7cd0a3c3a4d2d6a716233b3bc1cbfb98e049**
- SPEC.md blob SHA: **421acafa9a8439a8ed6efb5e2e0edf6f2146f11c**
- src/evolve/loop.py blob SHA: **036a3d3f9c1ad14ad08b72ebd51dd27ef61c5515**
- src/evolve/blame.py blob SHA: **788a60987380e5394044c817e4e3d81aefa1d081**
- src/evolve/mutate.py blob SHA: **d3b2c9f04c139ddce69975de2ab36d9c55527741**
- src/evolve/select.py blob SHA: **f514568a286f90192cb463ac16012dee47f2c74f**
- docs/static/replay_data.js blob SHA: **977344677c2f9b3d9d99f14c20942bf5f91348ce**

The replay is explicitly a **reference testbed run**, not the paper's headline experiment: Qwen3-4B, BFCL curated demo subset with 150 instances (90 train / 30 selection / 30 test), seed 42, and 90 generations. The paper's reported benchmark results use Qwen3-8B and full benchmark settings. These two evidence levels must not be conflated.

## 3. Mechanism reconstructed from the source

The released implementation follows this sequence:

1. Roll out a parent on a small training mini-batch.
2. Select the single lowest-reward episode in that batch as the representative failure.
3. Ask the Blamer to choose exactly one of Planner, Selector, Caller, or Synthesizer. The LLM's valid module choice is used directly; rule-based blame is only a parse-failure fallback.
4. Ask the Mutator to edit only that module. The child differs from its parent in one module.
5. Admit the child only if its mean reward on the current mini-batch is strictly greater than the parent's.
6. Re-evaluate the population on the fixed selection set, retain instance-wise winners, and sample parents according to their selection-set win frequencies. The final deployed policy is the population member with the highest mean reward on that selection set.

This is a coherent targeted-mutation design, but it creates a measurable distinction between **blame frequency** and **successful intervention utility**. A module may be implicated in a bad trajectory without a prompt edit to that module being the most effective evolutionary action.

## 4. Independent aggregation of the released 90-generation replay

The replay records were parsed and aggregated without executing the Agent, calling a model, or changing the upstream repository.

| Blamed module | Proposed mutations | Accepted mutations | Acceptance rate | Generations where the best selection score increased |
|---|---:|---:|---:|---:|
| Caller | 53 | 5 | 9.4% | 0 |
| Planner | 29 | 20 | 69.0% | 3 |
| Selector | 4 | 2 | 50.0% | 0 |
| Synthesizer | 4 | 0 | 0.0% | 0 |
| **Total** | **90** | **27** | **30.0%** | **3** |

The three increases in the replay's best selection score occur on Planner-targeted generations. The final recorded best selection score is 0.5149. The case study reports 50% held-out success on its 30-instance demo test subset; this is a small, single-seed reference run, not an independent replication of the paper.

Two descriptive differences stand out:

- Caller was selected for 53/90 proposals, yet only 5/53 Caller edits were accepted and none coincided with an increase in the replay's best selection score.
- Planner was selected for 29/90 proposals, 20/29 edits were accepted, and all three selection-score increases occurred on Planner-targeted generations.

This is a **blame-to-intervention mismatch signal** in one run. It does **not** establish that the Blamer was wrong: causal responsibility, editability, mutator quality, task distribution, and the fitness effect of a local edit are different quantities. The current data cannot isolate those explanations.

## 5. What this finding does and does not justify

### Supported

- The released reference run provides a concrete, inspectable example where module-blame frequency is poorly aligned with the observed utility of edits to that module.
- EVOTOOL's source uses a single-module mutation and a greedy parent-child gate on the current mini-batch; its population selection then uses a repeatedly consulted selection set.
- A more useful target-selection signal would need to distinguish diagnosis from the expected benefit of an intervention, rather than assume that the most-blamed module is automatically the best mutation target.

### Not supported

- It does not show that EVOTOOL generally fails, or that the same pattern holds across seeds, backbones, benchmarks, or task families.
- It does not prove a new EC mechanism exists.
- It does not justify simply scheduling modules by historical acceptance rate. That is closely related to established Adaptive Operator Selection (AOS) and credit-assignment methods.
- It does not justify reusing the selection/test split, accessing held-out results, or running a new experiment without a separate approval gate.

## 6. Prior-art gate and current decision

A simple rule such as “mutate modules that had higher past acceptance rates” is not a defensible novelty claim. LAOS already studies LLM-driven Adaptive Operator Selection with operator credit assignment and replay; LLM4EO studies LLM-assisted operator-level meta-evolution; classical AOS and credit assignment are mature areas. See:

1. Zhang, Y., & Yi, G. (2025). LAOS: Large Language Model-Driven Adaptive Operator Selection for Evolutionary Algorithms. *Proceedings of the Genetic and Evolutionary Computation Conference (GECCO 2025)*, 517–526. https://doi.org/10.1145/3712256.3726450
2. Liao, R., Qiu, J., Chen, X., & Li, X. (2026). Online Operator Design in Evolutionary Optimization for Flexible Job Shop Scheduling via Large Language Models. arXiv:2511.16485v3. https://arxiv.org/abs/2511.16485

The exact overlap between these methods and an intervention-utility signal at the **Agent-module** level is not fully resolved here. In particular, the LAOS full text and official code were not independently inspected in this pass. Therefore:

**Decision: keep PAUSE_CURRENT_AGENT_EC_METHOD_DISCOVERY_ROUTE. Do not create a Phase-1A-19 candidate-generation handoff.** This is one preliminary lead that earns a narrow prior-art audit, not a reopening of method development.

## 7. Next gate

1. Inspect LAOS primary text and official implementation if obtainable; compare its credit assignment and action-selection equations with the proposed distinction between blame and intervention utility.
2. Compare against LLM4EO, classical AOS, and existing causal/counterfactual credit-assignment work. Record the exact target object, signal, update equation, baselines, and any genuine mechanism-level difference.
3. If the only surviving change is acceptance-rate scheduling, classify it as already known/minor variant and close this lead.
4. Only if a specific uncovered mechanism survives that audit may a development-only protocol be drafted. Any experiment still requires a separately approved scope and budget.

### Hard limits retained

- No live LLM API requests.
- No MetaBox performance experiments.
- No AES scientific performance runs.
- No GPU jobs.
- No held-out/test task access.
- No modifications to openissue, EvoPareto-Agent, or any other repository.
