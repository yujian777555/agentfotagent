# Phase-1A-17 — Cross-Domain Evolutionary-Controller Transfer Literature Matrix

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Scope: primary-source literature audit and transfer-object feasibility; no implementation or experiments.
- Fixed target: a genuinely useful LLM-empowered EC method must improve Agent task performance. A transfer claim is optional and must be falsifiable.
- Evidence caveat: sources differ in maturity. Peer-reviewed papers, arXiv preprints, abstracts and secondary reviews are labeled separately. Not finding an exact paper is not proof of novelty.

## 1. Decision summary

**No transferable controller candidate is admitted. H2 is NOT_READY and NO_GO_AS_CURRENTLY_SPECIFIED.**

This is not a project-level NO-GO. The current MetaBox-to-AES controller-transfer plan cannot proceed because:
1. Earlier phases have not produced an approved source-domain controller with a defensible update/selection rule. Phase-1A-14's shortlist has zero surviving candidates; Phase-1A-10's Agent-assisted design experiment had zero blind-review PASS candidates.
2. The only plausible common state variables are generic search summaries (relative progress, stagnation, diversity, operator credit). These are standard AOS/hyper-heuristic signals, not a novel transfer representation.
3. Source and target actions do not share a fixed semantic identity. MetaBox numerical DE actions include strategy, F/CR, p-best, archive and restart choices; AES actions include structured policy-gene mutation, module recombination, policy-level selection and task-family evaluation. A mapping is many-to-many and domain-specific.
4. Transfer in evolutionary algorithms and genetic-programming hyper-heuristics is already a substantial literature; 2025 reviews classify instance, feature/representation and parameter transfer across dozens of methods. Agent-side general/target-specific component transfer and cross-domain meta-improvement are also covered by recent work.
5. A bespoke target adapter could make a controller executable, but without a fixed semantic mapping it would demonstrate re-engineering, not direct controller transfer.

## 2. Mechanism-level comparison

| Work | Transferable object | State/representation | Update or transfer mechanism | Target domain and evidence | Implication |
|---|---|---|---|---|---|
| Xavier & de Castro (published online 2025; journal volume 2026), *On the use of transfer learning in nature-inspired algorithms: a systematic review* | Multiple forms: instances, features/representations, parameters | Across 47 primary studies | Taxonomy of instance transfer, feature/representation transfer and parameter transfer; highlights what/when/how to transfer and negative-transfer risk | Secondary review, not a new method or direct Agent study | Transfer in EC is established; a generic “transfer a controller” framing needs a more specific mechanism and controls. https://doi.org/10.1007/s10462-025-11404-6 |
| Lv & Liu (2023 preprint / later journal article), *Multitasking Evolutionary Algorithm Based on Adaptive Seed Transfer for Combinatorial Problem* (MTEA-AST) | Candidate seeds / solutions across optimization tasks | Discrete solution encodings; dimensions may differ | Dimension unification, task similarity estimation, adaptive source-task selection and seed correction to suppress negative transfer | Four combinatorial optimization tasks; primary paper/preprint | Shows cross-domain mapping, similarity-aware transfer and negative-transfer mitigation already exist, though transferred object is solutions, not a high-level Agent controller. https://arxiv.org/abs/2308.12647 |
| Hu et al. (2025), *A classifier-assisted evolutionary algorithm with knowledge transfer for expensive multitasking problems* | High-quality samples / classifier training information | Task-oriented sample representations with PCA-based subspace alignment | Classifier-assisted CMA-ES plus transfer of samples between tasks | Expensive multi-task optimization; peer-reviewed journal article | Representation alignment plus transfer is established. https://doi.org/10.1007/s40747-025-01908-7 |
| Scheepers & Pillay, *A structure-based genetic programming generation constructive hyper-heuristic with transfer learning for combinatorial optimisation* (published 2025) | Evolved constructive heuristics / GP knowledge | Structured GP programs across scheduling, bin packing and vehicle routing | Structure-based GP with transfer learning, compared with canonical GP and non-transfer variant | Three combinatorial domains; publisher abstract reports gains over canonical GP and the no-transfer variant | Transfer of evolved heuristics across problem domains is directly studied. The abstract does not establish transfer to a different kind of controller or Agent runtime. https://doi.org/10.1007/s10710-025-09528-3 |
| Russell & Pillay (2023), *A Selection Hyper-Heuristic for Transfer Learning in Genetic Programming* | GP model/knowledge used by a selection hyper-heuristic | Genetic-programming symbolic-regression tasks | Transfer learning integrated with a selection hyper-heuristic; exact implementation should be checked from the full paper before claiming a detailed operator-level comparison | Primary conference paper; ACM metadata available | Directly crowds generic “transfer + hyper-heuristic + GP”; full-text access was limited in this pass. https://doi.org/10.1145/3583133.3590686 |
| Zhang et al. (2026), *Hyperagents* | Meta-level improvement procedure, persistent memory and agent-generation knowledge | A self-referential editable program containing task and meta agents | Meta-agent itself is editable; accumulated meta-level improvements reportedly transfer across domains | Cross-domain Agent self-improvement; arXiv primary paper | Generic cross-domain transfer of an improvement procedure is already claimed in Agent self-improvement. It does not use the same frozen MetaBox controller, but weakens a broad “transfer meta-strategy” novelty claim. https://arxiv.org/abs/2603.19461 |
| Yu et al. (2026), *Harmony Harness: Multi-Objective Self-Evolution of Agent Harnesses* | General-purpose harness mechanisms separated from benchmark-specific adaptations | Factorized harness components; multi-objective repository-scale harness representation | Decomposition-based evolutionary search, factorized general/task-specific evolution and dynamic composition | SecRepoBench and BaxBench; arXiv preprint at audit date | Directly covers separating transferable general mechanisms from target-specific adaptation in Agent evolution. A modular adapter alone is not novel. https://arxiv.org/abs/2610.15150 |
| Shang et al. (2026), *MESH-Harness: Self-Improving Agent Harnesses via Bandit-Guided Compositional Evolution* | Modular harness implementations and combinations | Shared module representations and role-specific pools | Full-covariance LinUCB, mixed-start coordinate ascent, trace-guided local edits and recombination | Multiple Agent task families; arXiv preprint | Covers adaptive module selection and compositional evolution within Agent harnesses; a controller that selects target modules/operators is crowded. https://arxiv.org/abs/2610.05300 |
| Lee et al. (2026), *Meta-Harness: End-to-End Optimization of Model Harnesses* | Executable harness code and prior execution experience | Source code, candidate scores and execution traces | Agentic proposer accesses all prior candidates and traces; outer-loop search over harness code | Text classification, retrieval/math reasoning, TerminalBench-2; arXiv primary paper | Cross-task/model reuse of a discovered harness and trace-informed search are established, although not the proposed numerical-EC-controller transfer. https://arxiv.org/abs/2603.28052 |
| DyACE (2026 preprint), *Dynamic Algorithm Co-evolution for Online Automated Heuristic Design with Large Language Model* | Search operators/algorithms and trajectory-derived verbal gradients | Online search-trajectory features; changing combinatorial search state | Look-ahead rollouts ground an LLM meta-controller; phase-specific interventions modify algorithms online | JSSP, TSP, CVRP. The paper explicitly leaves cross-domain transfer of verbal gradients as future work | A dynamic search controller is close prior art. Its stated transfer future work does not validate MetaBox-to-Agent transfer; nevertheless, it shows the exact issue remains unresolved even between related optimization domains. https://arxiv.org/html/2603.13344v1 |

## 3. What this literature does and does not establish

Established:
- Transfer of individuals, seeds, representations, parameters, learned heuristics and meta-level procedures is a broad EC/ML research family.
- Task similarity, representation alignment, deciding what/when to transfer and negative transfer are recognized central problems.
- Agent-side transfer of general mechanisms versus task-specific adaptation is now directly addressed by Harmony Harness.
- Agent-side adaptive modular selection and compositional evolution are addressed by MESH-Harness.
- Cross-domain meta-level self-improvement is addressed by Hyperagents.

Not established by the sources inspected:
- That a fixed controller trained on MetaBox numerical optimization will improve evolution over the project's structured Agent-policy genome.
- That a valid source/target state-action homomorphism exists for these particular environments.
- That such transfer is impossible in principle.
- That the precise intersection has no prior work. The audit was targeted, not exhaustive.

## 4. Why the current H2 claim is not admissible

The exact novelty cannot be “transfer EC knowledge from MetaBox to AES.” This describes a destination, not a mechanism. A viable claim would need a frozen controller representation, an exact state abstraction, fixed action semantics, a defined transfer/training protocol and a novel mechanism for handling mismatch or negative transfer. No such mechanism has been identified, and no source controller passed the prior method/novelty gates.

## 5. Required references

1. Xavier, R., & de Castro, L. N. (2025; journal volume 2026). On the use of transfer learning in nature-inspired algorithms: a systematic review. *Artificial Intelligence Review, 59*, Article 22. https://doi.org/10.1007/s10462-025-11404-6
2. Lv, H., & Liu, R. (2023). Multitasking Evolutionary Algorithm Based on Adaptive Seed Transfer for Combinatorial Problem. arXiv:2308.12647. https://arxiv.org/abs/2308.12647
3. Hu, M., Ren, Z., Cao, Z., Guo, Y., Sun, H., Zhou, H., et al. (2025). A classifier-assisted evolutionary algorithm with knowledge transfer for expensive multitasking problems. *Complex & Intelligent Systems*. https://doi.org/10.1007/s40747-025-01908-7
4. Scheepers, D., & Pillay, N. (2025). A structure-based genetic programming generation constructive hyper-heuristic with transfer learning for combinatorial optimisation. *Genetic Programming and Evolvable Machines*. https://doi.org/10.1007/s10710-025-09528-3
5. Russell, R., & Pillay, N. (2023). A Selection Hyper-Heuristic for Transfer Learning in Genetic Programming. *GECCO 2023 Companion*. https://doi.org/10.1145/3583133.3590686
6. Zhang, J., Zhao, B., Yang, W., Foerster, J., Clune, J., Jiang, M., Devlin, S., & Shavrina, T. (2026). Hyperagents. arXiv:2603.19461. https://arxiv.org/abs/2603.19461
7. Yu, W., Miculicich, L., Mishra, B. D., Chen, J., Li, S., Fredrikson, M., Pfister, T., & Le, L. T. (2026). Harmony Harness: Multi-Objective Self-Evolution of Agent Harnesses. arXiv:2610.15150. https://arxiv.org/abs/2610.15150
8. Shang, Z., Huo, Y., Gong, M., Yan, A., Qu, Z., Dong, J., Low, B. K. H., Wu, C., & Dai, Z. (2026). MESH-Harness: Self-Improving Agent Harnesses via Bandit-Guided Compositional Evolution. arXiv:2610.05300. https://arxiv.org/abs/2610.05300
9. Lee, Y., Nair, R., Zhang, Q., Lee, K., Khattab, O., & Finn, C. (2026). Meta-Harness: End-to-End Optimization of Model Harnesses. arXiv:2603.28052. https://arxiv.org/abs/2603.28052
10. Dynamic Algorithm Co-evolution for Online Automated Heuristic Design with Large Language Model (DyACE). (2026). arXiv:2603.13344. https://arxiv.org/html/2603.13344v1
