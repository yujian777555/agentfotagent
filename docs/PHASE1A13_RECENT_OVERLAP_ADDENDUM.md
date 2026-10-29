# Phase-1A-13 Addendum — Additional Novelty Collisions and Revised Verdict

- Date: 2026-10-29
- Applies to: docs/PHASE1A13_LINKAGE_MECHANISM_AUDIT.md
- Scope: literature audit only. No implementation, API call, GPU run, or scientific evaluation.

## 1. Critical correction: FCLE's estimator is close to established Differential Grouping

The full accepted manuscript for Olieman, Bouter & Bosman, “Fitness-based Linkage Learning in the Real-Valued Gene-pool Optimal Mixing Evolutionary Algorithm” (IEEE TEVC 2021; DOI 10.1109/TEVC.2020.3039698) was inspected after the initial audit. It explicitly defines fitness-based interaction detection by evaluating four points formed from two values for each of two variables and comparing the effect of changing one variable under different settings of the other. This is the same core difference-in-differences logic proposed for FCLE.

Thus, the estimator itself is **not a novel algorithmic contribution**. Repeating it over Agent task instances, estimating confidence intervals, and filtering interactions by sign consistency across task families may be a useful adaptation to noisy/multi-task fitness, but is not enough by itself to claim a new EC method.

Further relevant EC prior art:
- Dushatskiy et al. (2024), GOMEA/CGOMEA: explicit linkage learning and linked-subset mixing, including conditional dependencies.
- Guijt et al. (GECCO 2022), “Solving Multi-Structured Problems by Introducing Linkage Kernels into GOMEA,” DOI 10.1145/3512290.3528828: learns a different linkage structure for each solution/local neighborhood to handle multiple dependency structures. This further reduces novelty of a generic “task/family-specific linkage” claim.
- Multi-objective GOMEA already learns separate linkage models in objective-space clusters; simply preserving multiple linkage models is not new.

## 2. Additional Agent-search overlaps discovered

| Work | Primary-source finding | Consequence for this project |
|---|---|---|
| **AgentSwift** (AAAI 2026) | Full paper says the training data for its value model uses pairwise covering arrays to cover interactions between workflows and components, and search co-optimizes workflows/components with uncertainty-guided hierarchical MCTS. | A generic “model Agent component interactions, then guide search” claim is already directly overlapped. FCLE would need to show something more specific than interaction coverage. https://doi.org/10.1609/aaai.v40i38.40453 |
| **MaAS: Multi-agent Architecture Search via Agentic Supernet** (ICML 2025) | Optimizes a probabilistic/continuous distribution of Agent architectures and samples query-dependent systems, with cross-dataset and cross-backbone transfer. | A generic task-conditioned architecture distribution or per-query Agent policy is already covered. https://proceedings.mlr.press/v267/zhang25bi.html |
| **Beyond Prompts: Measuring and Optimizing LLM Tool-Agent Harnesses** (Findings of EMNLP 2026) | PRISM routes failures to prompt, tool-boundary middleware, or joint edits, with Pareto search and constraints on edit patterns; reports held-out lift and a conservative reliability metric. | Failure-surface routing, joint policy/middleware edits, Pareto search and held-out reliability are now more directly covered than in the previous audit. Do not propose them generically. https://aclanthology.org/2026.findings-emnlp.1455/ |
| **AgenticEvolve** (arXiv:2610.31326, 2026-10-22) | Persistent LLM agents design and run experiments between evolutionary-program evaluations; compares against an otherwise identical no-analysis variant. | Generic “Agent analyzes candidates and conducts experiments to improve evolutionary search” is also a high-risk claim for Track A. Preprint only; not reproduced here. https://arxiv.org/abs/2610.31326 |
| **Code Evolution for Control** (arXiv:2601.06845) | Uses LLM-driven evolutionary search to synthesize executable control policies. | Executable policy synthesis by LLM+EA is not sufficient novelty. https://arxiv.org/abs/2601.06845 |
| **SEVerA: Verified Synthesis of Self-Evolving Agents** (arXiv:2603.25111) | Uses formally guarded model calls, verification, and subsequent learning to synthesize self-evolving agents with hard behavioral contracts. | Formal contracts plus generic Agent synthesis are also an active line; an evaluator/tool precondition alone is not a method contribution. https://arxiv.org/abs/2603.25111 |
| **HASP: Harnessing LLM Agents with Skill Programs** (EMNLP 2026) | Turns lessons into executable program functions that intervene at failure-prone states; validated functions can be evolved for self-improvement. | Executable guardrails or failure-triggered policy interventions alone are not a safe novelty claim. https://aclanthology.org/2026.emnlp-main.2086/ |

The recent “Automated Design of Agentic Systems” survey (2026 preprint) also categorizes 33 methods by target object, search strategy, representation and feedback. A future novelty audit should use its taxonomy to check coverage systematically rather than search only by the word “evolution.” https://www.preprints.org/manuscript/202606.0238

## 3. Revised FCLE decision

**Decision: NO_GO_FCLE_AS_CURRENTLY_SPECIFIED.**

Reasoning:
1. Its central pairwise interaction estimator is a direct adaptation of Differential Grouping / fitness-based linkage learning.
2. Its linked-subset variation is GOMEA-style optimal mixing.
3. Its family-consistency gate is a reasonable robustness safeguard, but currently looks like statistical filtering on top of established linkage learning rather than a sufficiently distinct EC mechanism.
4. AgentSwift already covers workflow/component interaction coverage and task-conditioned performance prediction; AgentSquare and MaAS cover modular/recombined and query-conditioned Agent search; LK-GOMEA covers multiple/local linkage structures.
5. The expected gain is plausible but unproven. A literature gap cannot be inferred from not seeing the exact same acronym or combination in the papers checked.

FCLE should not be implemented as the thesis method unless a future audit derives a more substantive, mathematically specified innovation—for example, a new linkage estimator with a principled treatment of noisy, task-family-shifted black-box outcomes, plus evidence that it differs from and improves over Differential Grouping, LK-GOMEA, AgentSwift and standard evolutionary baselines. Merely adding bootstrap confidence intervals or a family-consistency threshold is insufficient.

## 4. What remains useful

- The existing AES can remain an engineering scaffold; its current 16-genome mock pilot is not scientific evidence.
- The genome-v2, task-difficulty, and fitness/baseline contracts remain readiness documents only.
- Agent improvement remains the project's fixed target. The project is **not** globally rejected.
- No live API calls, MetaBox performance runs, AES scientific experiments, GPU hours, or held-out access are authorized.

## 5. Next search boundary

Do not generate another list of Agent modules or another generic evolutionary Agent architecture. Search for a specific EC mechanism that is not merely:
- prompt/module/harness evolution;
- blame-guided mutation or failure-surface routing;
- value-model/MCTS or query-conditioned architecture search;
- generic linkage learning or optimal mixing;
- counterfactual plan mutation;
- budget allocation;
- generic LLM-agent experimentation.

The next review should compare the remaining candidates against the 2026 ADAS survey taxonomy and the newly identified EMNLP 2026 harness paper before deciding whether a researchable gap exists.
