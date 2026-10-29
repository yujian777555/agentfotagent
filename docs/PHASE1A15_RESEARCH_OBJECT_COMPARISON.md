# Phase-1A-15 — Research Object Comparison

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Branch: phase1a-phase11-unified-agent-ec-roadmap
- Status: completed as a literature/design audit only; no experiment authorized.
- Inputs: project charter, Phase-1A-14 decision/matrix, Phase-1A-15 handoff, targeted primary-source search.

## 1. Decision in one paragraph

The fixed goal remains to apply a genuinely useful LLM-empowered evolutionary-computation (EC) method to improving Agent task performance. This phase compares five possible research objects rather than inventing algorithm names. **Object 2 — a programmatic runtime action-selection policy for a stateful tool-use Agent — is the best problem formulation to audit next, but it is not yet a novel method candidate.** Finite-state controllers, programmatic policies, genetic programming for RL, evolutionary policy search, safe policy synthesis, and LLM-assisted evolutionary policy discovery all have prior art. No candidate is admitted in Phase-1A-15. The next phase must audit typed/contract-aware evolutionary program synthesis and policy variation at mechanism level; if no distinct update/selection rule survives, stop this route without experiments.

## 2. Comparison of five research objects

| Object | Decision variables | Objective and feedback | EC role | Closest literature | Assessment |
|---|---|---|---|---|---|
| **1. Static Agent prompt/module/Harness** | Prompt text, memory/retrieval rules, tools, workflow graph, module code | Verified task success, cost, robustness; execution traces and failures | Mutation/recombination and survivor selection over system configurations | EoH, LLaMEA, AgentSquare, EvoTool, GSME, AEL, HarnessForge, HarnessEvolve, Living-Harness, AgentSwift, MaAS | **Crowded.** This is the most direct target but generic Harness evolution, blame-guided edits, policy selection, and joint harness/policy evolution are established. Do not choose without a new update rule. |
| **2. Programmatic runtime action policy in a stateful tool environment** | A typed program or finite-state controller mapping symbolic observations and internal state to allowed tool actions and memory-state updates | Goal-state success; tool errors/steps/cost; hard action-contract violations as non-negotiable constraints | EC searches a structured policy space; grammar/type/contract-aware variation could make the search explicit and reproducible | Finite-state controllers for POMDPs; evolutionary policies for multi-reward POMDPs; genetic programming for RL; NEAT/neuroevolution; MLES; SNES/PSyCo; safe policy improvement for FSCs | **Best next problem formulation, not yet a method.** The policy-search problem is established. A distinct EC operator or selection rule must be demonstrated; simply using GP/EA on tool tasks is application novelty only. |
| **3. Reusable controller selecting among Agent policies** | Context-to-policy mapping, selection scores, routing thresholds, controller parameters | Per-episode/task outcome, context, recent policy performance | Bandit/AOS/hyper-heuristic selects policies and may add candidates | AEL uses Thompson Sampling to select retrieval policies and reflection to add arms; LAOS, LMCOEA, AdaEvolve and hyper-heuristics cover adaptive selection | **Crowded.** Replacing Thompson Sampling with an EA or contextual controller is not sufficient. Delayed-credit or task-regime structure would need a mechanism-level difference. |
| **4. EC mechanism that improves later Agent policy search** | Mutation/crossover/selection/search-control operator or an LLM-generated optimizer program | Source-domain optimization feedback, later Agent task performance | EC is both the method and the object being improved | EoH, LLaMEA, LLM4EO, LAOS, LMCOEA, AdaEvolve, AgentSwift, ELMER, SeDev, MLES | **Crowded at the generic level.** “LLM proposes a mechanism, EA selects it” has been explored. Cross-domain transfer remains a hypothesis, not a contribution. |
| **5. Joint evolution of Agent policy and evaluator/verifier** | Policy genome plus executable verifier, judge, or task-specific test suite | Task outcomes, verifier discrimination, false positives/negatives, independent oracle feedback | Co-evolution can search both behavior and measurement | UCoE, GSME, OpenSkill, RHO, DemoEvolve and related weak-feedback work | **High risk.** Verifier-harness co-evolution and self-built feedback exist. Without an independent external oracle, co-evolution risks rewarding evaluator exploitation. |

## 3. Why object 2 is the next audit target

This choice is based on the research object, not on a claim of novelty.

1. **Direct target alignment:** the evolved object is the Agent's decision policy during task execution, rather than an optimizer on a separate numerical benchmark only.
2. **EC can be explicit:** the phenotype can be a versioned typed policy program or finite-state controller; the search operators, parent selection, survivor selection, and complexity constraints are inspectable.
3. **Reproducible feedback is possible:** the project's controlled AES tool world can score goal states and count contract violations, but it remains an engineering scaffold until independently validated.
4. **Strong falsification is possible:** compare the proposed EC mechanism against standard GP/EA, random valid-program search, LLM-only proposals, and simple hand-coded rules with matched unique-candidate counts and evaluation budgets.
5. **The main novelty risk is severe:** policy evolution, genetic programming, finite-state controllers, and LLM-assisted evolutionary policy search are established. The research contribution cannot be “apply evolution to tool-agent policies.”

## 4. The transfer hypothesis is not itself a research object

The charter's source-to-target idea (MetaBox → AES) remains optional and unvalidated. A controller learned on BBOB-like numerical optimization does not automatically transfer to a discrete program/policy space. Its state features, action semantics, credit signal, and update cadence must be aligned explicitly.

A transfer claim must eventually compare:
- target-only standard EC;
- target-only controller search/training;
- source-trained controller transferred with a frozen mapping;
- random or shuffled state/action mapping;
- an equal-budget target-specific controller;
- held-out task families untouched during controller selection.

If a shared state/action abstraction cannot be defined without target-specific redesign, the purported “same controller transfer” claim fails. An adapter that rewrites the controller into a different policy is not evidence of direct transfer.

## 5. Gate for admitting a method

No method enters implementation unless all conditions pass:
- a mathematical or executable update/selection rule is stated;
- nearest methods are compared at mechanism level, including programmatic policy search and constrained program synthesis, not only Agent/Harness papers;
- EC has a necessary role and is not explained equally well by random valid candidates or exhaustive search;
- the mechanism has a preregisterable negative control;
- the policy and evaluator are separated so the candidate cannot improve by exploiting the scoring function;
- a held-out task-family protocol and matched-budget baseline plan are feasible;
- any hard safety constraints are enforced independently of fitness.

## 6. Phase-1A-15 outcome

**NO_GO_NEW_METHOD_CANDIDATE.** Object 2 is retained as the single next literature-audit target, not as an approved novelty claim. No code, live API, MetaBox run, AES scientific run, GPU run, or test/held-out access occurred.

## 7. Primary references used in this comparison

- Meuleau, N., Kim, K.-E., Kaelbling, L. P., & Cassandra, A. R. (1999). Solving POMDPs by Searching the Space of Finite Policies. *Proceedings of UAI 1999*. https://www.cassandra.org/arc/papers/uai99.pdf
- Soh, H., & Demiris, Y. (2011). Evolving Policies for Multi-Reward Partially Observable Markov Decision Processes (MR-POMDPs). *GECCO 2011*. https://groups.csail.mit.edu/EVO-DesignOpt/gecco2011Proceedings/proceedings/p713.pdf
- Stanley, K. O., & Miikkulainen, R. (2002). Evolving Neural Networks through Augmenting Topologies. *Evolutionary Computation, 10*(2), 99–127. https://doi.org/10.1162/106365602320169811
- GPRL (2018). Interpretable Policies for Reinforcement Learning by Genetic Programming. *Engineering Applications of Artificial Intelligence, 76*, 158–169. https://doi.org/10.1016/j.engappai.2018.09.007
- Belzner, L., & Wirsing, M. (2021). Synthesizing Safe Policies under Probabilistic Constraints with Reinforcement Learning and Bayesian Model Checking. *Science of Computer Programming, 206*, 102620. https://doi.org/10.1016/j.scico.2021.102620
- Larsen, R., & Schmidt, M. N. (2022). Programmatic Policy Extraction by Iterative Local Search. *Inductive Logic Programming*, LNCS 13191, 156–166. https://doi.org/10.1007/978-3-030-97454-1_11
- Simão, T. D., Suilen, M., & Jansen, N. (2023). Safe Policy Improvement for POMDPs via Finite-State Controllers. *AAAI 2023*, 37(12), 15109–15117. https://doi.org/10.1609/aaai.v37i12.26763
- Hu, Q., Tong, X., Yuan, M., Liu, F., Lu, Z., & Zhang, Q. (2025). Discovering Interpretable Programmatic Policies via Multimodal LLM-assisted Evolutionary Search. arXiv:2508.05433. https://arxiv.org/abs/2508.05433. **Preprint; not treated as peer-reviewed evidence.**
- Heck, L., Macák, F., Češka, M., & Junges, S. (2026). Constrained and Robust Policy Synthesis with Satisfiability-Modulo-Probabilistic-Model-Checking. *AAAI 2026*, 40(43), 36253–36261. https://doi.org/10.1609/aaai.v40i43.40944
- Xu, W., et al. (2026). AEL: Evolving Agent Harness in Open-Ended Environments. *Findings of EMNLP 2026*, 27857–27885. https://aclanthology.org/2026.findings-emnlp.1316/
- Chen, M., et al. (2026). HarnessForge: Joint Harness and Policy Evolution for Adaptive Agent Systems. *EMNLP 2026*. https://aclanthology.org/2026.emnlp-main.1893/
