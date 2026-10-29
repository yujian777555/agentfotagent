# Phase-1A-18 Strategic Feasibility Assessment

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Scope: strategic decision only; no candidate implementation, API calls, MetaBox/AES performance runs, GPU use, or held-out access.
- Basis: project charter; decisions D-001 through D-027; Phase-1A-14 to Phase-1A-17 artifacts; targeted inspection of primary publisher/preprint records.
- Status of literature: mixed. EVOTOOL is ACL 2026 peer-reviewed; HarnessLens, HarnessDev, Evo-Bench and Rethinking Harness Evolution are arXiv/preprint-stage in the sources inspected. Their claims are reported as author-reported results, not independent replications.

## 1. Executive decision

**Recommend B: PAUSE the current method-discovery route. Do not continue speculative candidate generation.**

This is not a claim that LLM-empowered EC cannot improve Agents, and not a permanent rejection of the project's broad objective. It means the current project has not identified a sufficiently distinct EC mechanism that is both uncovered by recent work and supported by a concrete failure mode. The project must stop producing new candidate names until new evidence changes that assessment.

No Phase-1A-19 handoff is created because no direct research route survives the required evidence gate.

## 2. Fixed objective and success standard

The objective remains: ultimately apply a genuinely useful LLM-empowered evolutionary-computation method to improve Agent task performance.

A viable method must demonstrate all of the following:
1. A concrete Agent behavior to optimize and a reproducible failure mode.
2. A specific EC update/variation/selection mechanism, not merely a pipeline that calls an LLM and selects the highest score.
3. A defensible difference from current Agent evolution, program synthesis, GP, AOS/hyper-heuristics and LLM-only search.
4. Benefit over strong alternatives under matched evaluation feedback, inference/token budget and wall-clock/evaluation budget.
5. Improvement on disjoint held-out task families, not only the tasks repeatedly used to evolve candidates.
6. An ablation showing the proposed EC mechanism itself causes the benefit.

These are admission criteria, not a claim that every paper must use identical metrics.

## 3. New primary-source audit that changes the decision

### 3.1 EVOTOOL directly occupies the most obvious Agent-targeted EC route

Yang et al., ACL 2026, *EVOTOOL: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection*, uses a gradient-free evolutionary framework to evolve modular tool-use policies. It defines Planner, Selector, Caller and Synthesizer modules; localizes failures from traces; mutates the blamed module using critique; and uses diversity-aware population selection. The ACL publisher page reports results across four benchmarks and two backbones.

Implication: “use EC to evolve Agent tool-use policies with trajectory diagnosis, targeted mutation and diversity” is already directly covered. Rephrasing the blame estimator, changing the module names, or adding generic archive logic is not a defensible new method without a precisely demonstrated missing mechanism.

Primary source: https://aclanthology.org/2026.acl-long.2016/ ; DOI: https://doi.org/10.18653/v1/2026.acl-long.2016

### 3.2 HarnessLens covers selective, behavior-aware verification

The 2026 preprint *Verify Smarter, Evolve Further: Efficient Harness Evolution through Behavior-Aware Verification* (HarnessLens) jointly explores task space and harness components, derives candidate edits from trajectories, and selectively verifies them on behavior-relevant tasks with an attributable-evidence gate. The paper reports 7.6–13.6% average held-out gains across three harnesses and four benchmarks while using less evaluation budget than its compared baselines.

Implication: “evaluate only tasks relevant to a proposed behavior change” and “attribute a change to trajectory evidence” are not open ideas at this level of generality. This is a preprint result and has not been independently reproduced in this project.

Primary source: https://arxiv.org/abs/2608.27311

### 3.3 HarnessDev and Evo-Bench make Agent self-evolution an explicit evaluated capability

HarnessDev evaluates both creation and iterative evolution of executable Agent harnesses, including held-out capability and execution-token cost. Its preprint reports that evolution gains are unstable, transfer only partially to held-out tasks, and depend strongly on the runtime model.

Evo-Bench provides a harness-evolution benchmark spanning Search, Office and General Agent domains. Its preprint reports that performance varies by domain, with particular difficulty on Office tasks requiring specific workflows.

Implication: a new project-owned environment or another Agent-evolution benchmark alone is not a method contribution. A candidate would need a new mechanism and an independently falsifiable advantage, not simply another harness genome or task suite.

Primary sources:
- HarnessDev: https://arxiv.org/abs/2609.01437
- Evo-Bench: https://arxiv.org/abs/2608.09096

### 3.4 Fair evaluation itself is a serious open issue, but not yet this project's algorithmic innovation

*Rethinking the Evaluation of Harness Evolution for Agents* compares harness evolution against parallel sampling, sequential refinement and other search baselines under comparable feedback/inference budgets, then evaluates on disjoint held-out tasks. Its authors report that harness evolution does not consistently beat simple test-time scaling on Terminal-Bench 2.1 and gains only 0.6 average points on a held-out split in one reported comparison.

Implication: matched-budget controls and held-out evaluation are mandatory. However, discovering that existing methods were evaluated unfairly would primarily support an empirical evaluation paper unless a new EC mechanism is also identified.

Primary source: https://arxiv.org/abs/2607.12227

### 3.5 Executable policy evolution is also a broad neighboring field

*Code Evolution for Control: Synthesizing Policies via LLM-Driven Evolutionary Search* evolves executable control policies with LLM-assisted evolutionary search. It is not a direct tool-Agent method, but it weakens any broad novelty claim based only on evolving interpretable executable policies.

Primary source: https://arxiv.org/abs/2601.06845

## 4. Option A — continue direct Agent-targeted EC research

### What it would require

A concrete route would have to define:
- the exact Agent behavior and runtime decision being improved;
- a reproducible failure mode and primary task-success metric;
- an EC operator/selection rule that addresses that failure;
- the mechanism-level difference from EVOTOOL, HarnessLens, HarnessDev, Evo-Bench, generic GP/program synthesis, AOS/hyper-heuristics and LLM-only candidate refinement;
- a reason why standard GP/EA, random valid-genome search, local search, target-specific AOS, LLM-only search and matched-budget test-time scaling do not explain the same benefit;
- primary sources and experiments that could falsify the claimed gap.

### Assessment

**FAIL — no such route is supported by the current evidence.**

The most concrete target object retained in Phase-1A-15 was runtime action-selection policies in stateful tool-use environments. Phase-1A-16 rejected generic typed/contract-aware GP; Phase-1A-14 rejected failure-localized mutation, semantic-local mutation, quality-diversity archives, linkage-aware recombination, adaptive control, architecture search and other candidate families as currently specified. EVOTOOL directly overlaps modular tool-use policy evolution. HarnessLens overlaps behavior-conditioned verification and attribution. HarnessDev/Evo-Bench overlap self-evolving harness evaluation.

It is possible that a narrow unsolved failure exists in a particular environment, but this audit has not established one. Inventing another operator before locating that failure would repeat the project's previous failure mode.

### Why EC is not yet shown to be indispensable

Evolutionary search is a plausible way to optimize discrete, non-differentiable Agent policies. But plausibility is not evidence that it is the necessary or best method for the claimed problem. Current candidate routes have not shown that EC adds value beyond:
- random valid-genome search at the same number of evaluations;
- greedy/local policy edits;
- LLM-only sequential refinement;
- strong target-specific AOS/hyper-heuristic or standard GP;
- parallel sampling and other matched-budget test-time scaling;
- existing Agent/harness evolution systems.

A scientific comparison could establish this, but without a distinct mechanism it would not, by itself, meet the project's intended method-improvement contribution.

## 5. Option B — pause/retire the current route

**PASS as the responsible decision under current evidence.**

“Pause” means:
- do not generate more algorithm candidates from the same generic families;
- do not implement a new acronym or start a pilot to create evidence after the fact;
- do not authorize live LLM calls, MetaBox performance runs, AES scientific runs, GPU jobs or held-out access;
- preserve all prior evidence, including negative results, without claiming that all Agent×EC research is impossible.

It does not require deleting the repository or abandoning the user's broader research ambition. It suspends the current candidate-generation route until new evidence appears.

## 6. Exact reopening conditions

Reopen this project route only if at least one of the following evidence packages is produced:

1. **A source-grounded missing mechanism:** a reproducible failure in an existing Agent policy/harness method, supported by traces and primary-paper/code inspection, for which the proposed EC operation has a mathematical or algorithmic distinction from the nearest method.
2. **A controlled EC-value demonstration:** on a frozen, non-held-out development protocol, EC beats random valid-genome search, local search, LLM-only refinement, strong GP/AOS and matched-budget test-time scaling by a predeclared practically meaningful margin; ablations attribute the gain to the EC mechanism. This is a gate for further review, not permission to access test tasks.
3. **An independently validated benchmark gap:** a task family with objective verifiable success and disjoint task-family test split that current methods systematically fail on, where a specific EC mechanism is motivated before looking at test outcomes.

Any reopening request must state the nearest methods it falsifies, exact outcome metric, minimum meaningful effect, equal-budget rules, seed count/power rationale, failure handling and a held-out protocol. New acronyms, more modules, bigger models or more compute do not count as new evidence.

## 7. Final decision

**PAUSE_CURRENT_AGENT_EC_METHOD_DISCOVERY_ROUTE.**

The broad objective remains scientifically plausible, but the current candidate-generation process has not produced an admissible algorithmic contribution. Continuing by proposing more variants is not justified. No next-phase candidate-generation handoff is created.

## 8. References (strict bibliographic records)

1. Yang, S., Han, C., Ma, X., Li, Y., Ghasemi Madani, M. R., & Hovy, E. (2026). EVOTOOL: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection. *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL 2026), Volume 1: Long Papers*, 43553–43572. https://doi.org/10.18653/v1/2026.acl-long.2016
2. Xu, J., Zhang, Y., Zhang, A., Li, W., Liang, J., & Yang, D. (2026). Verify Smarter, Evolve Further: Efficient Harness Evolution through Behavior-Aware Verification. arXiv:2608.27311. https://arxiv.org/abs/2608.27311
3. Wu, Y., Zhang, J., Shi, J., Lei, X., Gu, Q., et al. (2026). HarnessDev: Can LLMs Create and Evolve Their Own Agent Harness? arXiv:2609.01437. https://arxiv.org/abs/2609.01437
4. Huang, L., Yang, C., Zhou, H., Song, H., Chen, Z., Le, R., Song, Y., Zhao, W. X., & Zhang, T. (2026). Evo-Bench: Can Language Models Improve Agent Harness? arXiv:2608.09096. https://arxiv.org/abs/2608.09096
5. Wang, Y., Zhu, H., Hu, Z., Yuan, Y., Chen, Z., Senthil, S., Hajishirzi, H., Tsvetkov, Y., Dasigi, P., & Xiao, T. (2026). Rethinking the Evaluation of Harness Evolution for Agents. arXiv:2607.12227. https://arxiv.org/abs/2607.12227
6. Guo, P., Li, C., Feng, Y., & Zhang, C. (2026). Code Evolution for Control: Synthesizing Policies via LLM-Driven Evolutionary Search. arXiv:2601.06845. https://arxiv.org/abs/2601.06845
