# Phase-1A-14 Prior-Work Matrix — Agent-Targeted LLM/EC Mechanisms

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Scope: mechanism-level literature audit and candidate screening only.
- Not performed: implementation, API calls, MetaBox runs, AES scientific runs, GPU runs, or held-out access.
- Evidence codes: **P** = peer-reviewed primary paper/publisher record inspected; **A** = arXiv/preprint primary text inspected; **S** = survey taxonomy/abstract inspected; **C** = existing project audit. “Inspected” does not mean independently reproduced.

## 1. Executive conclusion

**No new algorithm candidate survives Phase-1A-14's current novelty screen.** The objective remains fixed: apply a genuinely useful LLM-empowered evolutionary-computation method to improve Agent task performance. This is not a project-level NO-GO; it is a refusal to invent novelty by recombining known components.

The newest evidence makes several generic ideas unsafe to claim:
- failure diagnosis + deterministic crediting + semantic quality-diversity archive is already directly described by GSME;
- semantic locality / controllable mutation strength is directly addressed by ELMER and SeDev, and motivated by a trajectory-analysis study;
- hierarchical adaptation of exploration intensity, island scheduling, and meta-guidance is addressed by AdaEvolve; adaptive operator selection is also covered by LAOS/LMCOEA in prior project audits;
- heterogeneous LLM mutation populations plus QD are covered by DEI;
- workflow/component interaction coverage and hierarchical Agent search are covered by AgentSwift; query-conditioned architecture distributions by MaAS;
- generic prompt, module, workflow, harness, and full-code evolution are extensively covered in the ADAS taxonomy and primary works.

## 2. Four-axis taxonomy used

Following Madžar & Mekterović's 2026 ADAS preprint, each work is compared by:
1. **Target object** — prompt, compound-system parameters, workflow topology, modular Agent, executable harness, full code, or the EA itself.
2. **Search/update rule** — mutation/recombination, QD archive, MCTS, bandit/AOS, learned controller, policy-gradient/RL, or structured semantic exploration.
3. **Representation** — text, module/typed DSL, graph, code, genotype, or population/archive.
4. **Feedback and selection** — scalar task score, paired verifier score, critique, trajectory diagnosis, surrogate, novelty, or transfer reward.

The ADAS survey is a preprint and not peer reviewed in the inspected version. It is used as a taxonomy, not as primary evidence for any individual method.

## 3. Mechanism matrix

| Work | Target and representation | Core update / selection mechanism | Feedback and generalization | Overlap / decision | Evidence |
|---|---|---|---|---|---|
| **EvoPrompt / Promptbreeder** | Text prompt / mutation prompt | EA variation, tournament selection; Promptbreeder also evolves the mutation prompt | Task fitness on development data | Generic “LLM + EA evolves prompts” is covered | P; prior Phase-1A-12 audit |
| **EoH / LLaMEA** | Heuristic text plus executable algorithm code/class | LLM proposes or mutates algorithms; fitness-based evolutionary selection | Executable benchmark performance | Generic LLM proposes executable candidates and EA selects them is covered | P/C |
| **AgentSquare** | Modular Agent cell (planning, reasoning, tool use, memory) and code | Module search, mutation/recombination, surrogate-guided search | In-context performance predictor; multiple Agent settings | Expanded Agent genome / module recombination is not novel alone | P/C |
| **EvoTool** | Tool-use policy modules: Planner, Selector, Caller, Synthesizer | Trajectory blame attribution; mutate blamed module; diversity-aware selection | Execution trajectory and task performance | Direct overlap with trace-guided targeted Agent policy evolution | P/C |
| **AgentSwift** | Workflow plus functional components | Value model, interaction-covering training data, uncertainty-guided hierarchical MCTS; mutation/recombination/refinement | Task-conditioned predicted value and execution results | Interaction-aware workflow/component search already covered; exact formula-level comparison is not complete | P |
| **MaAS** | Query-conditioned probabilistic Agent architecture / supernet | Optimize architecture distribution; sample query-specific systems | Task reward minus resource use; cross-dataset/backbone transfer | Query-conditioned Agent architecture distribution and transfer are covered | P |
| **MASS / TPGO / MASPOB** | Joint prompt and workflow/topology parameters | Staged coordinate optimization, textual-gradient/co-evolution, graph-encoded prompt bandits | Validation score, influence proxy, scalar reward or node-level critique | “Jointly evolve prompts and topology” is not a distinct contribution | P/S |
| **AFlow / GPTSwarm / Workflow-R1 / SWIFT** | Executable workflow graph, graph edges, or workflow generator | LLM-guided MCTS; REINFORCE; RL over workflow subsequences; amortized structural transfer | Execution reward; cross-query transfer | Generic workflow evolution or amortization is covered | P/S |
| **TTHE / Evoflux** | Executable harness or typed tool-workflow graph | Trace-feedback program/harness evolution, workflow edits, adaptive redesign | Execution feasibility and downstream outcome | Generic executable harness/workflow evolution is covered; some exact method details still require full source audit | A/C |
| **GSME: Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity** | Runtime harness patches; categorical archive keyed by WHERE × WHY pathology | LLM diagnoses/proposes patches; validity gate, activation gate, paired 2-sigma credit gate; quality-biased champion extension plus cross-cell recombination | Deterministic per-task scoring; sealed-test crediting; reported results across seven domains | Directly covers semantic pathology archive + deterministic mutation crediting + QD + held-out generalization | A |
| **AdaEvolve** | Populations/islands of LLM-generated programs and search policy | One accumulated-improvement signal drives local exploration intensity, bandit resource routing across islands, and meta-guidance after stalls | Fitness trajectory; broad program/algorithm optimization | Generic adaptive search intensity, stagnation-triggered guidance, or hierarchical adaptive LLM-EA is covered | A |
| **ELMER** | Natural-language policy description compiled to typed executable program | Fine-tuned model performs conditional semantic mutation at low/medium/high strength, compilation, and reverse translation | Execution fitness and behavioral-displacement calibration | Generic controllable semantic mutation strength / behavior-space step control is covered | A |
| **SeDev** | LLM-generated code / semantic neighborhood | Structured prompt guidance explores semantically adjacent solutions; feedback synthesis aggregates unit-test results | Unit tests and code-generation benchmark | Generic semantic-local exploration plus synthesized execution feedback is covered | P |
| **What Makes an LLM a Good Optimizer?** | LLM-guided EA trajectories across 15 LLMs and 8 tasks | Empirical trajectory analysis, not a new search algorithm | Finds local refinement near high-performing semantic regions correlates with stronger optimization; novelty alone is not predictive | Motivates hypotheses, but does not by itself provide a new EC method; any semantic-locality candidate overlaps ELMER/SeDev | P |
| **DEI** | Distributed QD population; heterogeneous LLMs as mutation operators | Heterogeneous LLM nodes evolve in parallel and share champions asynchronously | QD score, archive coverage and held-out generality | Generic multi-model mutation diversity + QD is covered | A |
| **EvolRepair** | Program-repair candidate population grouped by semantic behavior/fix family | Semantic mutation, grouping and recombination of complementary repair hypotheses | Test execution and structured failure feedback | Semantic families + recombination + failure-guided search is adjacent prior art, though its target is program repair | A |
| **EvoCF** | Multi-agent collaboration plans | Counterfactual plan generation, failure-derived constraints and memory-grounded evaluation | Outcome feedback and symbolic constraints | Generic evolutionary counterfactual plan mutation is covered | P |
| **Darwin Gödel Machine / MOSS / EvoMAS** | Full Agent code or whole multi-agent system | Open-ended QD, recursive source rewriting, or evolutionary team generation | Empirical benchmark feedback | Full-code self-evolution and multi-agent evolutionary generation are covered | P/A/S |
| **Beyond Prompts / PRISM** | Tool-Agent harness surfaces: prompts, middleware, or joint edits | Failure-surface routing, constrained edits, Pareto search | Execution/benchmark feedback and held-out evaluation | Generic failure-surface routing and joint prompt/middleware evolution are covered | P |
| **AgenticEvolve** | Evolutionary-program candidate plus experiment design process | Persistent LLM agent designs/runs experiments between evaluations | Candidate performance and experiment feedback | Generic “LLM Agent conducts experiments to guide evolutionary search” is a high-risk novelty claim | A |
| **FCLE (Phase-1A-13)** | Agent-policy genome with pairwise linkage graph | Four-point interaction estimator plus GOMEA-style linked-subset mixing | Paired task-level success; family consistency | Rejected: estimator overlaps fitness-based linkage/Differential Grouping; mixing overlaps GOMEA; AgentSwift further overlaps interaction-aware search | C + primary paper audit |
| **Phase-1A-10 generic agent-assisted design** | Proposed mechanism candidates from task cards/traces | LLM proposals, prefilter, blind review; performance experiments withheld | 0 candidates passed independent novelty review; random group had higher structural-validity rate than trace group | Existing evidence does not support an Agent design advantage; do not resurrect without a different mechanism | C |

## 4. Candidate-family screen

| Candidate family considered | Nearest covered mechanisms | Current verdict | Why |
|---|---|---|---|
| Trace diagnosis → targeted module mutation → EA selection | EvoTool; GSME; PRISM; TTHE/Evoflux | **NO_GO_GENERIC** | Core loop and relevant selection/crediting patterns are already covered |
| Semantic-local mutation / trust-region variation | ELMER; SeDev; optimizer-trajectory study; AdaEvolve | **NO_GO_AS_STATED** | Local refinement, mutation-strength conditioning, and search adaptation have direct precedents |
| Semantic pathology QD archive | GSME; DGM; DEI; EvolRepair | **NO_GO_GENERIC** | Archive descriptors, semantic families, cross-cell recombination, and heterogeneous search are established |
| Pairwise policy-gene interaction / linkage | Differential Grouping; fitness-based linkage learning; GOMEA/CGOMEA; AgentSwift | **NO_GO_FCLE** | Estimator and linked mixing are not sufficiently distinct |
| LLM-driven adaptive operator/search controller | LAOS; LMCOEA; AdaEvolve; Phase-1A-3/4 prior audits | **NO_GO_GENERIC** | Adaptive operator selection, stagnation adaptation and hierarchical search intensity are crowded |
| Query/task-conditioned Agent architecture selection | MaAS; Learn-to-Configure; SWIFT; AgentSwift | **NO_GO_GENERIC** | Conditional configuration and amortized transfer are established |
| Robustness/held-out generalization as sole innovation | GSME; MaAS; SWIFT; standard robust/multitask optimization | **NOT_A_METHOD_BY_ITSELF** | Generalization is a required evaluation property, not a distinct EC mechanism |
| Better fitness/tie-breaking/paired significance alone | GSME; standard statistical selection and evaluation contracts | **NOT_A_METHOD_BY_ITSELF** | Necessary evaluation discipline, not an algorithm contribution |
| Verifier-free/sparse-feedback evolution | GSME explicitly states verifier dependence as a limitation; many preference/critique/surrogate approaches exist | **OPEN QUESTION, NOT A CANDIDATE YET** | Requires a precise new estimator and an independent way to falsify it; not enough to replace success labels with an LLM judge |

## 5. What the evidence actually says

The survey and recent primary work identify real scientific weaknesses:
- candidate evaluation is expensive and noisy;
- benchmark optimization can overfit or exploit a proxy;
- task-level credit assignment is difficult;
- cross-task/model transfer remains uncertain;
- the field lacks a characterization of when an LLM-as-optimizer beats random search;
- GSME remains dependent on a reliable per-task verifier and dense repeated scoring;
- trajectory analysis shows that semantic novelty is not equivalent to useful progress.

These are **problem statements**, not innovations. Every candidate must name a concrete EC update/selection rule that addresses one of them and be compared with the nearest existing mechanism. The project must not present a generic combination of these known ingredients as new.

## 6. References and evidence boundary

1. Madžar, M., & Mekterović, I. (2026). *Automated Design of Agentic Systems: A Survey of Algorithms for Searching, Optimizing, and Evolving LLM Agents, Workflows, and Prompts*. Preprints.org, v1. https://www.preprints.org/manuscript/202606.0238. **Unreviewed preprint; taxonomy only.**
2. Luo, X., Wang, F., Hu, C., Xue, D., & Deng, Y. (2026). *Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity*. arXiv:2607.13683. https://arxiv.org/abs/2607.13683. **Preprint; full primary text inspected, not independently reproduced.**
3. Zhang, X., Chen, X., Portet, F., & Peyrard, M. (2026). What Makes an LLM a Good Optimizer? A Trajectory Analysis of LLM-Guided Evolutionary Search. *Findings of the Association for Computational Linguistics: ACL 2026*, 24987–25011. https://doi.org/10.18653/v1/2026.findings-acl.1252.
4. Siper, M., Khalifa, A., & Togelius, J. (2026). *ELMER: Evolutionary Language Model that Explores and Refines*. arXiv:2608.10196. https://arxiv.org/abs/2608.10196. **Preprint; abstract and primary page inspected.**
5. Yang, R., Liu, J., Zeng, J., Wang, J., Jiang, J., An, B., Cai, Y., & Zhao, M. (2026). SeDev: Structured Semantic Exploration for LLM-Driven Code Generation. *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics*, 35485–35512. https://doi.org/10.18653/v1/2026.acl-long.1641.
6. Cemri, M., Agrawal, S., Gupta, A., Liu, S., Cheng, A., Mang, Q., Naren, A., Erdogan, L. E., Sen, K., Zaharia, M., Dimakis, A. G., & Stoica, I. (2026). *AdaEvolve: Adaptive LLM Driven Zeroth-Order Optimization*. arXiv:2602.20133. https://arxiv.org/abs/2602.20133. **Preprint; primary text inspected.**
7. Donaghy, J., & Rastogi, S. (2026). *DEI: Diversity in Evolutionary Inference for Quality-Diversity Search*. arXiv:2605.27130. https://arxiv.org/abs/2605.27130. **Preprint; primary text inspected.**
8. Yue, L., Bhandari, K. R., Ko, C.-Y., Patel, D. C., Lin, S., Zhou, N., Gao, J., Chen, P.-Y., & Pan, S. (2026). From Static Templates to Dynamic Runtime Graphs: A Survey of Workflow Optimization for LLM Agents. *Findings of the Association for Computational Linguistics: EMNLP 2026*, 29630–29658. https://aclanthology.org/2026.findings-emnlp.1393/.
9. Olieman, C., Bouter, A., & Bosman, P. A. N. (2021). Fitness-based Linkage Learning in the Real-Valued Gene-pool Optimal Mixing Evolutionary Algorithm. *IEEE Transactions on Evolutionary Computation, 25*(2), 358–370. https://doi.org/10.1109/TEVC.2020.3039698.
10. Dushatskiy, A., Virgolin, M., Bouter, A., Thierens, D., & Bosman, P. A. N. (2024). Parameterless Gene-Pool Optimal Mixing Evolutionary Algorithms. *Evolutionary Computation, 32*(4), 371–397. https://doi.org/10.1162/evco_a_00338.
11. Li, Y., Li, L., Wu, Z., Liao, Q., Hao, J., Shao, K., & Xu, F. (2026). AgentSwift: Efficient LLM Agent Design via Value-Guided Hierarchical Search. *Proceedings of the AAAI Conference on Artificial Intelligence, 40*(38), 31843–31851. https://doi.org/10.1609/aaai.v40i38.40453.
12. Zhang, G., Niu, L., Fang, J., Wang, K., Bai, L., & Wang, X. (2025). Multi-agent Architecture Search via Agentic Supernet. *Proceedings of the 42nd International Conference on Machine Learning*, PMLR 267, 75834–75852. https://proceedings.mlr.press/v267/zhang25bi.html.
13. Zhang, J., et al. (2026). Beyond Prompts: Measuring and Optimizing LLM Tool-Agent Harnesses. *Findings of the Association for Computational Linguistics: EMNLP 2026*. https://aclanthology.org/2026.findings-emnlp.1455/.
14. Hu, Y., Zhang, Y., Trager, M., et al. (2026). *EvoMAS: Evolutionary Generation of Multi-Agent Systems*. arXiv:2602.06511. https://arxiv.org/abs/2602.06511. **Preprint.**
15. Cemri et al. and the prior project audits also cover adaptive LLM-EA search; see the separate Phase-1A-12 and Phase-1A-13 reports for LAOS/LMCOEA/AdaEvolve overlap details.

This matrix is a targeted mechanism audit, not a systematic review of every paper in ADAS. No candidate has been reproduced, and no novelty or performance claim is made.


## 7. Additional primary-source findings from the verifier / weak-feedback branch

These papers were located after the initial matrix draft. They close off several apparently open candidate families.

| Work | Mechanism and evidence | Effect on candidate search |
|---|---|---|
| **VERSE: Verified Self-Evolving Optimizer for Agent Harnesses** (Wang et al., arXiv:2610.02616, 2026) | Evolves both the executor harness and the optimizer's own prompts/tools/hooks; includes draft execution, failure replay, single-step perturbation and a training audit. Primary text inspected. | Generic meta-optimization of the harness optimizer, plus verification-aware outer/inner loops, is already covered. |
| **OpenSkill: Open-World Self-Evolution for LLM Agents** (Yan et al., arXiv:2606.06741, 2026) | Acquires knowledge and verification anchors from public resources; refines skills against self-built virtual tasks without target-task supervision. Primary text inspected. | “No gold verifier” or supervision-free self-evolution is not a clean gap by itself. |
| **UCoE: Verifier-Harness Co-Evolution** (Xu et al., arXiv:2610.17609, 2026) | Evolves executable verifier programs alongside harness state; tests verifier candidates on response contrasts and selects by weakest-family discrimination (“driving capacity”). Primary text inspected; preprint. | Generic co-evolution of verifier and Agent harness is covered. |
| **Retrospective Harness Optimization (RHO)** (Pan et al., arXiv, June 2026) | Selects a diverse coreset of past trajectories, re-solves tasks, uses self-validation/self-consistency and pairwise self-preference to choose harness updates without external grading. Primary publication page/abstract inspected; full method not audited here. | Generic verifier-free, past-trajectory self-preference optimization is covered. |
| **DemoEvolve** (Che et al., arXiv:2605.24539, 2026) | Uses competent demonstrations to guide harness-level diagnosis/editing under sparse, noisy feedback in long-horizon games. Primary text inspected; preprint. | Generic demonstration-bootstrapped harness evolution for sparse feedback is covered. |
| **Q-Evolve: Self-evolving LLM agents with in-distribution Optimization** (Zhang et al., ICML 2026, PMLR 306) | Learns an in-distribution critic from expert and agent trajectories, derives process rewards, and updates the task policy with behavior-proximal optimization. Primary PMLR page inspected. This is RL/policy optimization, not a direct EC method. | Sparse-reward stepwise credit assignment is already active in RL literature; it cannot be claimed as a novel EC contribution merely by using intermediate feedback. |
| **Harness Updating Is Not Harness Benefit** (Lin et al., EMNLP 2026) | Separates the ability to create useful harness updates from the executor's ability to activate/follow them; reports that benefit is non-monotonic with base-model capability. Primary publisher page inspected. | “A good edit may not improve the Agent” is already recognized; activation/faithfulness alone is not a novel mechanism. |
| **HSI: Hierarchical Self-Improvement** (2026 preprint, arXiv:2608.08466) | Hierarchy of task harness, evolver and meta-evolver; explicitly studies feedback-fidelity and backbone-capability bounds. Secondary paper page/abstract inspected. | Generic three-level recursive harness/evolver improvement is covered. |
| **Verifier-Harness co-evolution and RHO** | Both target open-ended tasks where direct labels/verifiers are weak, with explicit verifier/self-preference mechanisms. | The apparent verifier-free gap must be narrowed to a precise estimator that differs from UCoE, OpenSkill, RHO, DemoEvolve and related preference/critique methods; no such estimator is currently proposed. |

## 8. Updated decision after this supplement

The weak-feedback/verifier-light direction is **not yet a candidate**. UCoE, OpenSkill, RHO and DemoEvolve already cover major approaches to evolving with learned, self-built, preference-based, or demonstration-grounded feedback. The fact that these approaches have limitations is not evidence that a proposed EC replacement is novel.

No candidate is approved for implementation. The next phase should not start experiments. It should either:
1. derive a mathematically explicit feedback/selection mechanism that differs from these methods and has a falsifiable advantage, or
2. conclude that the current generic Agent-harness search space is too crowded and pivot to a narrower application setting only if a defensible mechanism gap is found.

## 9. Additional references

16. Wang, Z., Ge, Y., Wang, Z., Wang, H., Xu, Y., Frandsen, J., Fu, S., Wilson, A. C., & Reddy, C. K. (2026). *VERSE: Verified Self-Evolving Optimizer for Agent Harnesses*. arXiv:2610.02616. https://arxiv.org/abs/2610.02616. **Preprint; primary text inspected.**
17. Yan, Z., Song, D., Zhang, H., Liang, W., Zhang, Y., Dai, Y., He, L., Yu, P. S., Xu, R., Li, X., & Sun, L. (2026). *OpenSkill: Open-World Self-Evolution for LLM Agents*. arXiv:2606.06741. https://arxiv.org/abs/2606.06741. **Preprint; primary text inspected.**
18. Xu, T., Zhang, Y., Wu, Y., Nguyen, J., Dai, S., Moeinizade, S., Shao, Z., Wu, Q., et al. (2026). *Verifier-Harness Co-Evolution for Training-Free Self-Improvement on Open-Ended Tasks*. arXiv:2610.17609. https://arxiv.org/abs/2610.17609. **Preprint; primary text inspected via author-facing paper page.**
19. Che, L., Yang, Y., Lin, P., Wang, C., Wang, X., & Su, J. (2026). *DemoEvolve: Overcoming Sparse Feedback in Agentic Harness Evolution with Demonstrations*. arXiv:2605.24539. https://arxiv.org/abs/2605.24539. **Preprint; primary text inspected.**
20. Zhang, Y., Fang, M., Chen, Z., & Pechenizkiy, M. (2026). Self-evolving LLM agents with in-distribution Optimization. *Proceedings of the 43rd International Conference on Machine Learning*, PMLR 306, 155348–155365. https://proceedings.mlr.press/v306/zhang26au.html.
21. Pan, W., Liu, S., Lin, C.-Y., Zeng, J., Tang, X., Zhou, X., Lu, Y., & Jia, X. (2026). *Retrospective Harness Optimization: Improving LLM Agents via Self-Preference over Trajectory Rollouts*. arXiv preprint. https://www.microsoft.com/en-us/research/publication/retrospective-harness-optimization-improving-llm-agents-via-self-preference-over-trajectory-rollouts/.
22. Lin, M., Wu, J., Wang, Z., Shi, Z., Sang, Y., et al. (2026). *Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents*. Findings of EMNLP 2026. https://github.com/A-EVO-Lab/a-evolve/tree/release/harness-evolution. **Publisher/author publication page inspected.**
23. *Hierarchical Self-Improvement: A Framework for Task-Specific Evolvable Agent Harnesses*. (2026). arXiv:2608.08466. https://arxiv.org/abs/2608.08466. **Secondary page/abstract inspected; exact author metadata still requires primary-page confirmation.**
