# Phase-1A-15 — Adjacent EC and Programmatic Policy Literature Matrix

- Date: 2026-10-29
- Scope: mechanism-level audit to identify what is already known before an Agent-targeted EC candidate is proposed.
- Evidence boundary: primary publisher/author pages and paper texts were inspected where available; arXiv works are labeled as preprints. This is a targeted review, not an exhaustive systematic review.
- No implementation or experiments were performed.

## 1. Evolutionary/programmatic policy search

| Work | Policy representation | Update/optimization mechanism | Feedback / constraint handling | Relevance and overlap |
|---|---|---|---|---|
| Meuleau et al. (UAI 1999), *Solving POMDPs by Searching the Space of Finite Policies* | Finite-state automata / finite policies | Branch-and-bound for deterministic policies; gradient ascent for stochastic policies | POMDP objective; restricted finite policy space | Establishes policy-as-automaton search as classic work. A finite-state Agent policy alone is not novel. |
| Amato, Bonet & Zilberstein (AAAI 2010), *Finite-State Controllers Based on Mealy Machines for Centralized and Decentralized POMDPs* | Mealy-machine finite-state controller | Adapt controller-based optimization to richer transition/output structure | POMDP/Dec-POMDP benchmark return | Controller representation and state-dependent action selection predate LLM Agents. |
| Soh & Demiris (GECCO 2011), *Evolving Policies for Multi-Reward POMDPs* | Stochastic finite-state controllers | Two hybrid/memetic multi-objective EAs search nondominated policy sets | Multiple possibly conflicting rewards | Direct evidence that EC can evolve sequential policies under partial observability and multiple objectives. Generic EA policy search is covered. |
| Stanley & Miikkulainen (Evolutionary Computation 2002), *NEAT* | Neural-network topology and weights | Add nodes/connections incrementally; innovation markers support crossover; speciation protects structural innovations | RL fitness | Evolving policy structure plus parameters is established; “co-evolve structure and weights” is not novel. |
| Interpretable Policies for RL by Genetic Programming (EAAI 2018) | Symbolic policy equations | Genetic programming combined with model-based batch RL | Existing state-action trajectories and reward | Directly covers interpretable programmatic policy discovery using GP. |
| Hu et al. (2025), *MLES: Discovering Interpretable Programmatic Policies via Multimodal LLM-assisted Evolutionary Search* | Programmatic policies generated with multimodal LLM assistance | LLM policy generation plus evolutionary optimization and visual failure analysis | Behavioral feedback on control tasks; compared with PPO on two tasks | Directly overlaps “LLM generates policy candidates, EC selects/improves them.” It is a preprint, so novelty implications are high-risk even without peer review. |
| Belzner & Wirsing (Science of Computer Programming 2021), *PSyCo/SNES* | Neural policy parameters | Evolution strategies perturb parameters; a Bayesian estimate of constraint satisfaction adjusts the Lagrangian weight between reward and cost | Episode reward/cost; online Bayesian model checking; confidence target | Safety-aware evolutionary policy synthesis is established. A new method cannot claim “EC plus hard constraints” alone. |
| Cubuktepe et al. (AAAI 2021), *Robust Finite-State Controllers for Uncertain POMDPs* | Finite-state controller | Robust controller optimization under uncertainty | Worst-case/uncertain transition models | Robustness of structured policies is an existing formal-methods topic. |
| Simão, Suilen & Jansen (AAAI 2023), *Safe Policy Improvement for POMDPs via Finite-State Controllers* | FSC plus finite memory | Estimate history MDP from offline data and apply safe policy improvement; constrain changes to data-supported regions | Historical trajectories; high-probability improvement | Safe modification of an existing policy under limited evidence is covered by offline-RL/formal policy work. |
| Larsen & Schmidt (ILP 2022), *Programmatic Policy Extraction by Iterative Local Search* | Typed programmatic policy | Imitation projection, dataset aggregation and local search | Match a strong policy using trajectory examples | Programmatic policy search need not be evolutionary; any claimed EC advantage must beat local search and imitation baselines. |
| Heck et al. (AAAI 2026), *Constrained and Robust Policy Synthesis with Satisfiability-Modulo-Probabilistic-Model-Checking* | Policies with arbitrary structural constraints | SMT plus probabilistic model checking to solve constrained/robust policy synthesis | Formal reward and robustness requirements | Formal constraints and structural policy limits have strong non-EC alternatives; EC must justify why it is necessary. |
| Roupassov-Ruiz & Zuo (2026), *Survival Dynamics of Neural and Programmatic Policies in Evolutionary Reinforcement Learning* | Neural policies versus soft differentiable decision lists | Evolutionary RL compared against learning-only and neural-policy alternatives over 4,000 trials | Survival outcomes and RMST analysis | Recent preprint suggests interpretable programmatic policy representation deserves empirical comparison, but does not establish a new EC operator. |

## 2. Recent direct Agent evolution / policy-adaptation literature

| Work | Core mechanism | Evidence status | Overlap implication |
|---|---|---|---|
| AEL: Evolving Agent Harness in Open-Ended Environments (EMNLP Findings 2026) | Thompson Sampling selects memory-retrieval policy each episode; LLM reflection diagnoses regime/performance changes and adds new policy arms | Peer-reviewed publisher page/abstract | Policy selection plus reflection-driven candidate injection is directly covered. |
| HarnessForge: Joint Harness and Policy Evolution (EMNLP 2026) | Fault-guided Harness tailoring plus Harness-conditioned policy alignment | Peer-reviewed publisher page/abstract; public code repository found | Joint external execution structure and internal reasoning policy optimization is covered. |
| HarnessEvolve (arXiv:2609.00829, 2026) | Ground-truth reference trajectories align failed runs; error patterns are clustered; quality gate filters leakage/prompt bloat; performance gate rejects regressions and uses held-out selection | Preprint | Reference-trajectory credit assignment and anti-regression gating are not clean gaps. |
| Living-Harness (arXiv:2607.26598, 2026) | Converts execution/evaluator evidence into episodic recovery memory and a state graph of repair transitions; reuses it in later tasks | Preprint | Persistent trajectory-to-policy knowledge and graph updates are covered in broad form. |
| Rethinking the Evaluation of Harness Evolution for Agents (arXiv:2607.12227, 2026) | Compares Harness evolution with test-time scaling and simple search under matched feedback/inference budgets; evaluates held-out tasks | Preprint | Evaluation must separate a better method from merely spending more feedback/search; gains may not generalize. |
| GSME, VERSE, UCoE, OpenSkill, RHO, DemoEvolve | Gated semantic QD; optimizer self-evolution; verifier-harness co-evolution; self-built verification; self-preference from trajectory rollouts; demonstrations for sparse feedback | Mix of preprints and prior Phase-1A matrix evidence | Weak feedback, verifier co-evolution and recursive evolver improvement are already active research families. |
| AdaEvolve, ELMER, SeDev, DEI, AgentSwift, MaAS | Adaptive LLM-EA search, semantic mutation strength/local search, semantic code exploration, heterogeneous QD mutation, value-guided hierarchical Agent search, query-conditioned architecture distribution | Mix of peer-reviewed and preprint primary sources | Generic adaptive search, semantic-locality, QD and architecture search are covered. |

## 3. Transfer and hyper-heuristic literature

| Work family | Mechanism | What it rules out |
|---|---|---|
| Adaptive operator selection / hyper-heuristics | Select low-level search operators using reward, success-rate, utility, UCB/bandit, RL, or other credit-assignment rules | A controller that simply selects among mutation/recombination/restart operators is not novel. |
| Multi-task / transfer evolutionary algorithms (e.g., MTEA-AST, 2023) | Adaptive task selection, dimension/representation unification, explicit seed or knowledge transfer | “Transfer evolutionary knowledge across tasks” is a broad established family. A source-domain MetaBox → target-domain Agent claim needs a precisely defined transferable object and mapping, not only two benchmarks. |
| Robust and constrained policy synthesis | SMT, probabilistic model checking, FSC optimization, Bayesian safety confidence, safe policy improvement | Hard safety constraints and robustness need not be handled by a new EC mechanism; compare against formal synthesis and safe-policy baselines. |

## 4. Mechanism-level gaps not yet established

The review does **not** establish a novelty gap for any of these statements:
- “Use EC to evolve an Agent policy.”
- “Use LLMs to generate candidate programs/policies.”
- “Use execution failures to guide mutations.”
- “Use a finite-state controller for tool actions.”
- “Make policy search interpretable.”
- “Use hard constraints or formal verification.”
- “Transfer search knowledge from one task family to another.”
- “Use a held-out set, paired seeds, or matched budgets.”

The only remaining research task is to inspect the exact intersection of **typed/contract-aware evolutionary variation for executable stateful tool-use policies**, compare it against grammar-guided GP, semantic GP, program synthesis, and policy search, and decide whether a new operator/selection rule is actually missing. The current evidence says this intersection is **unresolved**, not novel.

## 5. References

1. Meuleau, N., Kim, K.-E., Kaelbling, L. P., & Cassandra, A. R. (1999). Solving POMDPs by Searching the Space of Finite Policies. *UAI 1999*. https://www.cassandra.org/arc/papers/uai99.pdf
2. Amato, C., Bonet, B., & Zilberstein, S. (2010). Finite-State Controllers Based on Mealy Machines for Centralized and Decentralized POMDPs. *AAAI 2010*, 1052–1058. https://doi.org/10.1609/aaai.v24i1.7748
3. Soh, H., & Demiris, Y. (2011). Evolving Policies for Multi-Reward Partially Observable Markov Decision Processes (MR-POMDPs). *GECCO 2011*. https://groups.csail.mit.edu/EVO-DesignOpt/gecco2011Proceedings/proceedings/p713.pdf
4. Stanley, K. O., & Miikkulainen, R. (2002). Evolving Neural Networks through Augmenting Topologies. *Evolutionary Computation, 10*(2), 99–127. https://doi.org/10.1162/106365602320169811
5. Interpretable Policies for Reinforcement Learning by Genetic Programming. (2018). *Engineering Applications of Artificial Intelligence, 76*, 158–169. https://doi.org/10.1016/j.engappai.2018.09.007
6. Belzner, L., & Wirsing, M. (2021). Synthesizing Safe Policies under Probabilistic Constraints with Reinforcement Learning and Bayesian Model Checking. *Science of Computer Programming, 206*, 102620. https://doi.org/10.1016/j.scico.2021.102620
7. Cubuktepe, M., Jansen, N., Junges, S., Marandi, A., Suilen, M., & Topcu, U. (2021). Robust Finite-State Controllers for Uncertain POMDPs. *AAAI 2021*, 11792–11800. https://doi.org/10.1609/aaai.v35i13.17401
8. Larsen, R., & Schmidt, M. N. (2022). Programmatic Policy Extraction by Iterative Local Search. *ILP 2021*, LNCS 13191, 156–166. https://doi.org/10.1007/978-3-030-97454-1_11
9. Simão, T. D., Suilen, M., & Jansen, N. (2023). Safe Policy Improvement for POMDPs via Finite-State Controllers. *AAAI 2023*, 15109–15117. https://doi.org/10.1609/aaai.v37i12.26763
10. Hu, Q., Tong, X., Yuan, M., Liu, F., Lu, Z., & Zhang, Q. (2025). Discovering Interpretable Programmatic Policies via Multimodal LLM-assisted Evolutionary Search. arXiv:2508.05433. https://arxiv.org/abs/2508.05433. **Preprint.**
11. Heck, L., Macák, F., Češka, M., & Junges, S. (2026). Constrained and Robust Policy Synthesis with Satisfiability-Modulo-Probabilistic-Model-Checking. *AAAI 2026*, 36253–36261. https://doi.org/10.1609/aaai.v40i43.40944
12. Roupassov-Ruiz, A., & Zuo, Y. (2026). Survival Dynamics of Neural and Programmatic Policies in Evolutionary Reinforcement Learning. arXiv:2601.04365. https://arxiv.org/abs/2601.04365. **Preprint.**
13. Xu, W., Han, J., Guo, M., Mei, K., Zhu, X., Zhang, H., & Metaxas, D. N. (2026). AEL: Evolving Agent Harness in Open-Ended Environments. *Findings of EMNLP 2026*, 27857–27885. https://aclanthology.org/2026.findings-emnlp.1316/
14. Chen, M., Lv, C., Zhang, G., Chang, H., & Zhou, S. (2026). HarnessForge: Joint Harness and Policy Evolution for Adaptive Agent Systems. *EMNLP 2026*. https://aclanthology.org/2026.emnlp-main.1893/
15. Jiang, W., et al. (2026). HarnessEvolve: Learning from Reference Trajectories for Reliable Agent Self-Evolution. arXiv:2609.00829. https://arxiv.org/abs/2609.00829. **Preprint.**
16. Wang, Y., et al. (2026). Rethinking the Evaluation of Harness Evolution for Agents. arXiv:2607.12227. https://arxiv.org/abs/2607.12227. **Preprint.**
17. Du, Y., et al. (2026). Living-Harness Is an Interactive-Agent Evolver. arXiv:2607.26598. https://arxiv.org/abs/2607.26598. **Preprint.**
18. Multi-tasking evolutionary algorithm based on adaptive seed transfer for combinatorial problem. (2023). *Applied Soft Computing, 147*, 110780. https://doi.org/10.1016/j.asoc.2023.110780
