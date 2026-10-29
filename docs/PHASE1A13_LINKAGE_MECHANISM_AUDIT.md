# Phase-1A-13 — Mechanism-Level Audit: Family-Consistent Linkage Evolution

- Date: 2026-10-29
- Scope: targeted literature and algorithm-design audit only.
- Not performed: code implementation, live LLM calls, MetaBox runs, AES scientific experiments, GPU runs, or held-out evaluation.
- Evidence labels distinguish primary paper text, official code pages, prior project audits, and unverified hypotheses.

## 1. Decision

The first specific EC-level candidate worth a final novelty check is **Family-Consistent Linkage Evolution (FCLE)**: estimate non-additive interactions between Agent-policy genes from paired evaluations on the same task instances, then let the evolutionary algorithm recombine gene groups only when those interaction effects are repeatable and consistent across training task families.

This is more specific than generic Agent-genome evolution or trace-guided mutation. However, **FCLE is not cleared as novel**. It touches established linkage-learning EAs (GOMEA/CGOMEA), AgentSwift's coverage of workflow/component interactions and value-guided hierarchical search, and AgentSquare's module recombination. Its only potentially defensible distinction is an explicit, task-paired estimate of fitness interaction plus a cross-family stability gate used to construct the linkage model for stochastic Agent-policy evolution. That distinction must survive a focused prior-art audit and empirical falsification before implementation.

Status: **CANDIDATE_FOR_FOCUSED_NOVELTY_REVIEW_ONLY**. Not approved for implementation or experiment.

## 2. Why the generic direct route is closed

The generic method “LLM diagnoses a failed Agent trajectory, mutates a policy module, and uses evolutionary selection/diversity” is already covered by EvoTool (Yang et al., ACL 2026). AgentSquare (ICLR 2025) covers modular Agent search and recombination. AgentSwift (AAAI 2026) searches workflow plus functional components and uses a value model with uncertainty-guided hierarchical MCTS. TTHE and Evoflux cover executable harness/workflow evolution from traces. ToolMaze covers task dependency complexity and tool perturbation/recovery as benchmark dimensions.

FCLE must not be described as:
- a new Agent-genome representation;
- generic module-interaction awareness;
- a new failure-recovery benchmark;
- generic counterfactual evaluation;
- generic linkage learning applied to an Agent;
- a more efficient search method unless an explicit search-efficiency mechanism is validated.

## 3. Primary prior-work comparison

| Work | Verified mechanism | Overlap with FCLE | Evidence / limitation |
|---|---|---|---|
| **EvoTool** (Yang et al., ACL 2026, DOI 10.18653/v1/2026.acl-long.2016) | Four evolvable tool-use prompt modules (Planner, Selector, Caller, Synthesizer); trajectory-grounded blame; targeted mutation of blamed module; diversity-aware population selection. Official code exposes blame/random/fixed/all/none mutation targets and diversity/greedy/top-k/static selection options. | Strong overlap in Agent-policy evolution, modular operators, and execution feedback. FCLE must not claim these as its contribution. | ACL primary paper and official repository/README inspected. The source does not establish that it estimates paired pairwise fitness interaction effects to build linkage groups; this is a bounded observation, not proof no such work exists elsewhere. |
| **AgentSquare** (Shang et al., ICLR 2025) | Planning, Reasoning, Tool Use and Memory module search; module evolution and recombination; in-context performance predictor. | Direct overlap in modular Agent search and recombination. | Primary paper page and official code tree/README inspected. No independent reproduction. |
| **AgentSwift** (Li et al., AAAI 2026, DOI 10.1609/aaai.v40i38.40453) | Hierarchical search jointly over workflows and functional components; value model conditioned on candidate design and task; training data uses pairwise covering arrays to cover workflow/component interactions; uncertainty-guided hierarchical MCTS with recombination, mutation and refinement. | **High risk:** it explicitly covers interactions between workflows/components and co-optimizes Agent components. FCLE cannot claim to be the first interaction-aware Agent search. | Full publisher-hosted paper text inspected. The paper describes interaction coverage for training the value model; this pass did not find an explicit paired counterfactual difference-in-differences estimator used to construct an evolutionary linkage graph. Official implementation was not fully audited. |
| **GOMEA / CGOMEA** (Dushatskiy et al., *Evolutionary Computation*, 2024, DOI 10.1162/evco_a_00338) | EAs explicitly learn and exploit variable linkage; CGOMEA adds conditional-dependency-based solution mating; compared with DSMGA-II on dependency-structured black-box problems. | **Very high algorithmic overlap:** learning variable dependencies and recombining linked subsets is established EC. | Publisher/academic abstracts inspected; not reproduced. |
| **Fitness-based linkage learning for RV-GOMEA** (Olieman et al., *IEEE TEVC*, 2021, DOI 10.1109/TEVC.2020.3039698) | Fitness-based linkage learning inspired by differential grouping, aimed at identifying interacting variables in black-box optimization. | Direct overlap with learning interactions from objective response rather than merely co-occurrence. | Academic repository/publisher abstracts inspected; exact formula-level comparison remains partial. |
| **EvoCF** (Chi et al., ICML 2026, PMLR 306) | Evolves multi-agent collaboration plans through counterfactual plan generation, failure-derived symbolic constraints and memory-grounded evaluation. | Raises novelty risk for generic evolutionary counterfactual variants and failure-derived constraints. | ICML/PMLR primary abstract inspected; not a direct modular-genome linkage method based on current evidence. |
| **CFOE: Self-Evolving Agents Can Repair Failures but Struggle to Generalize from Them** (Zhao et al., arXiv:2610.22984, 2026-10-16) | Finds a repair–generalization gap in failure-only evolution across several self-evolving paradigms and environments; even verified-correct experience may fail to transfer. | Motivates evaluating policy changes on unseen task families, but does not itself establish FCLE novelty. | Recent preprint text inspected; not peer-reviewed evidence in this pass. |
| **Large Language Model Agents Are Not Always Faithful Self-Evolvers** (Zhao et al., ICML 2026, PMLR 306) | Controlled interventions show agents may ignore or misinterpret condensed experience. | Supports testing whether a claimed interaction/lesson changes actual policy behavior rather than trusting a textual diagnosis. | ICML/PMLR primary abstract inspected. |

## 4. Candidate mechanism — FCLE

### 4.1 Research question

When a fixed-backbone LLM Agent is controlled by a structured, executable policy genome, do some policy genes interact non-additively, and can an EC algorithm exploit only interactions that are repeatable across training task families to improve policy search and held-out generalization?

This is narrower than “does evolution improve Agents?” and is falsifiable. It does not presume interactions exist or that FCLE wins.

### 4.2 Interaction estimator

Let g be a normalized parent genome and i,j two policy loci. For a predeclared alternative allele at each locus, form four policies: g, g with i changed, g with j changed, and g with both changed. Evaluate all four on the **same task instances** and frozen task seeds in family k. Let y(g,t,r) be verified terminal-state success for policy g, task t, and repeat r.

Define the family-specific paired interaction estimate on the success-probability scale:

\[
\widehat I_{ij,k} =
\frac{1}{|T_k|}\sum_{t\in T_k}
\left[
(\bar y_{ij,t}-\bar y_{i,t})-(\bar y_{j,t}-\bar y_{0,t})
\right].
\]

Each barred value averages predeclared repeats for the same task-policy pair. The paired contrast is intended to cancel task difficulty shared by the four variants. It does **not** remove all stochasticity from LLM calls; confidence intervals must resample task instances by family and preserve the paired structure.

Do not use step count to manufacture an interaction when primary success is tied. Secondary efficiency metrics can be analyzed separately under the frozen lexicographic fitness contract.

### 4.3 Family-consistency gate

An edge between loci i,j enters the linkage graph only if all predeclared criteria hold:
1. its pooled interaction magnitude exceeds a practical-effect threshold delta;
2. a paired, family-stratified uncertainty interval excludes zero;
3. the interaction sign is consistent in a predeclared proportion of training families;
4. the edge is stable under bootstrap resampling and is not explained by one task or one seed.

If the effect reverses across families, do not average the reversal away and then treat it as a universal dependency. Mark the edge context-sensitive/unresolved and do not use it in a global linkage block in the first version. A future conditional linkage variant would need its own prior-art audit and public, predeclared task-context features.

The threshold, number of families, confidence level and minimum effect must be chosen before results are observed. They are not tuned to make FCLE win.

### 4.4 Evolution operator

The intended EC modification is the **linkage model**, not a new Agent architecture:
1. maintain a population of normalized policy genomes and task-level records;
2. periodically select a predeclared subset of locus pairs for paired interaction probes;
3. build a graph from only reliable family-consistent edges;
4. convert graph components or a linkage tree into gene subsets;
5. use a GOMEA-style gene-pool mixing operation to copy a donor's alleles jointly for one selected subset;
6. accept a trial only under the frozen primary-success-first fitness rule on the designated selection split;
7. log every probe, graph edge, confidence interval, proposed block, acceptance decision, and evaluation cost.

This is a candidate design, not an approved implementation. Since GOMEA already supplies linkage learning and optimal mixing, FCLE's possible contribution is only the **paired, task-family-consistent interaction estimator for stochastic Agent-policy fitness**. If that difference is judged incremental or already covered, reject FCLE rather than renaming GOMEA.

## 5. Main hypothesis and falsification

### H1 — Useful, reproducible policy-locus interactions exist
Evidence needed: meaningful interaction estimates with stable signs across training families, not merely noisy score differences.

**Falsify if:** interactions are near zero; signs are unstable across task samples/families; results depend on one genotype, seed, or task; or the estimated graph does not predict held-out interaction patterns.

### H2 — FCLE improves evolutionary search
Compare, under matched unique-genome evaluations and episodes:
- standard conventional EA with single-locus mutation/crossover;
- AgentSquare-style module recombination where practical;
- a standard GOMEA/learned-linkage baseline using its established linkage model;
- the same FCLE operator with a shuffled/randomized linkage graph;
- an ablation with interaction estimation but no family-consistency gate;
- fixed policy, random unique-genome search, and LLM-only/self-refinement where feasible.

**Falsify if:** FCLE does not outperform standard GOMEA/EA on a predeclared primary outcome, shuffled linkage performs similarly, the stability gate adds no benefit, or the effect disappears on disjoint task families.

### H3 — Gains generalize beyond search tasks
Select on train, freeze on dev, then evaluate once on sealed task families. Report success rates and uncertainty per family, not only pooled averages.

**Falsify if:** train gains do not transfer; family-level variance grows; the method only helps a known task family; or the benefit depends on post-hoc metrics.

## 6. Critical risks

- **Representation:** current aes-genome-v1 has only 16 configurations and is exhaustively enumerable. aes-genome-v2 is not approved. First prove every locus/allele has an observable effect and canonicalize equivalent policies.
- **Fitness saturation:** historical mock results saturate at 100%; mock results cannot estimate real Agent interactions. Do not use mock scores as scientific evidence.
- **Noisy outcomes:** paired task instances reduce task heterogeneity but cannot guarantee common random numbers for API-generated actions. Freeze model/version/decoding and replicate policy-task pairs.
- **Multiple testing:** pairwise tests across many loci inflate false discoveries. Predeclare sparse screening, multiplicity correction or hierarchical shrinkage, and independent confirmation of selected edges.
- **Higher-order interactions:** pairwise linkage may miss three-way interactions. Check residuals on held-out genotype combinations; if pairwise models fail, do not silently add higher-order terms after seeing confirmation results.
- **Evaluation cost:** interaction estimation needs more evaluations than simple mutation. This is not a budget-allocation contribution; report added cost and require a performance/generalization gain that justifies it.
- **Task leakage:** family labels may be used for analysis, but hidden-goal information and held-out outcomes must not enter genotype search or linkage construction.
- **Baseline fidelity:** a weak hand-written baseline is insufficient. Implement or reproduce standard linkage learning faithfully and record the exact source/version.

## 7. Novelty verdict

**HIGH_RISK_NOT_CLEARED**

Evidence supports a specific candidate question, not a novelty claim. The combination is close to established fitness-based linkage learning/GOMEA, AgentSwift's workflow/component interaction coverage and value-guided hierarchical search, AgentSquare's module recombination, EvoTool's targeted modular evolution, and EvoCF's evolutionary counterfactual plan exploration.

Before any implementation, perform one more narrow audit of AgentSwift's interaction model and GOMEA/CGOMEA linkage-estimator equations, and seek literature specifically on interaction/epistasis-aware evolutionary optimization of LLM Agent designs. If FCLE cannot be distinguished by a precise algorithmic rule beyond applying known linkage learning to a new application, issue **NO_GO_FCLE** and search another EC mechanism.

## 8. References

1. Yang, S., Han, C., Ma, X., Li, Y., Ghasemi Madani, M. R., & Hovy, E. (2026). EVOTOOL: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection. *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL 2026)*, 43553–43572. https://doi.org/10.18653/v1/2026.acl-long.2016
2. Shang, Y., Li, Y., Zhao, K., Ma, L., Liu, J., Xu, F., & Li, Y. (2025). AgentSquare: Automatic LLM Agent Search in Modular Design Space. *International Conference on Learning Representations (ICLR 2025)*. https://arxiv.org/abs/2410.06153
3. Li, Y., Li, L., Wu, Z., Liao, Q., Hao, J., Shao, K., & Xu, F. (2026). AgentSwift: Efficient LLM Agent Design via Value-Guided Hierarchical Search. *Proceedings of the AAAI Conference on Artificial Intelligence, 40*(38), 31843–31851. https://doi.org/10.1609/aaai.v40i38.40453
4. Dushatskiy, A., Virgolin, M., Bouter, A., Thierens, D., & Bosman, P. A. N. (2024). Parameterless Gene-Pool Optimal Mixing Evolutionary Algorithms. *Evolutionary Computation, 32*(4), 371–397. https://doi.org/10.1162/evco_a_00338
5. Olieman, C., Bouter, A., & Bosman, P. A. N. (2021). Fitness-based Linkage Learning in the Real-Valued Gene-pool Optimal Mixing Evolutionary Algorithm. *IEEE Transactions on Evolutionary Computation, 25*(2), 358–370. https://doi.org/10.1109/TEVC.2020.3039698
6. Chi, H., Feng, Z., Yu, X., Luo, L., Ong, Y.-S., Tsang, I., Chen, H., Chang, Y., & Yin, H. (2026). EvoCF: Multi-Agent Collaboration via Agentic Memory-Driven Evolutionary Counterfactual Planning. *Proceedings of the 43rd International Conference on Machine Learning*, PMLR 306, 19424–19437. https://proceedings.mlr.press/v306/chi26b.html
7. Zhao, W., Zhang, Y., Zhao, Y., Bai, J., Liang, B., Xu, R., Qin, B., & Liu, T. (2026). Self-Evolving Agents Can Repair Failures but Struggle to Generalize from Them. arXiv:2610.22984. https://arxiv.org/abs/2610.22984
8. Zhao, W., Wang, Y., Zhang, Y., Deng, Y., Zhao, Y., Che, W., Qin, B., & Liu, T. (2026). Large Language Model Agents Are Not Always Faithful Self-Evolvers. *Proceedings of the 43rd International Conference on Machine Learning*, PMLR 306, 162243–162268. https://proceedings.mlr.press/v306/zhao26aw.html
9. Feng, T., Han, P., Dai, Z., & You, J. (2026). Building LLM Agent Systems the Deep Learning Way: From Modular Design to Architecture Search. arXiv:2610.04961. https://arxiv.org/abs/2610.04961

## 9. Evidence boundary

This is a targeted audit, not a systematic review of all EA linkage-learning literature or all 2026 Agent-search papers. No source code was executed, no results were reproduced, and no claim of novelty or empirical superiority is made.
