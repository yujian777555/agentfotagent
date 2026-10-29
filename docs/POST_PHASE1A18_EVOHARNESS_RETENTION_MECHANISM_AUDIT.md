# Post-Phase-1A-18 Evidence Audit: Harness Expansion, Delegation Drift, and Evolutionary Retention

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Branch: research/evoharness-retention-mechanism-audit
- Baseline branch: phase1a-phase11-unified-agent-ec-roadmap
- Scope: source-grounded literature and mechanism audit only
- Status: RESEARCH SIGNAL FOUND; NO NOVEL METHOD ADMITTED
- Safety boundary: no runtime code changes, no live LLM/API calls, no MetaBox/AES scientific runs, no GPU use, no held-out/test access.

## 1. Purpose

Phase-1A-18 paused the current method-discovery route because no specific uncovered failure mode plus EC-specific mechanism survived the earlier gates. This note does not reopen speculative candidate generation. It records a concrete, source-grounded empirical signal from recent primary papers and defines what must be verified before any candidate can be admitted.

The long-term project objective remains unchanged: use a genuinely useful LLM-empowered evolutionary-computation (EC) method to improve Agent task performance. Prior work is a starting point for improvement, not an automatic reason to stop. However, a known problem or a new combination of known components is not sufficient evidence of novelty.

## 2. Primary-source evidence

### 2.1 EVOTOOL: a strong direct baseline for evolving tool-use policies

Source: Yang et al., *EvoTool: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection*, ACL 2026.
- Publisher: https://aclanthology.org/2026.acl-long.2016/
- Full paper: https://arxiv.org/html/2603.04900v1

Mechanism reconstructed from the paper:
1. The policy is decomposed into Planner, Selector, Caller, and Synthesizer specifications; backbone weights remain frozen.
2. A Blamer LLM receives a trajectory and structured diagnostic events, assigns blame scores to modules, and selects the highest-scoring module.
3. A Mutator LLM edits only the selected module using trajectory-grounded critique; other modules remain fixed.
4. A child enters the population only if it outperforms its parent on the current mini-batch.
5. On a selection set, a candidate survives if it is the instance-wise best on at least one task. Parent sampling probability is proportional to its instance-wise win frequency.

Research implication: the generic ideas “evolve modular Agent policies,” “use trajectory-based blame,” “mutate the blamed module,” and “preserve specialists through instance-wise wins” are directly covered. They cannot be claimed as this project's new contribution.

Scope question left open: the paper's described selection mechanism is evaluated on its benchmark setup; this audit has not established that EVOTOOL studies the specific non-stationary setting where the externally supplied capability pool itself expands stage by stage. Do not infer that it cannot handle this setting; verify the paper and implementation before making that claim. The paper says code will be released after acceptance, so a public reference implementation was not confirmed in this audit.

### 2.2 EVOHARNESSBENCH: a concrete failure mode under changing capability pools

Source: Ke et al., *EVOHARNESSBENCH: Can Your Agents Keep Pace with an Evolving Harness?*, arXiv:2609.04280.
- Paper: https://arxiv.org/abs/2609.04280
- Full text: https://arxiv.org/html/2609.04280v3
- Project page: https://mas-orchestra.salesforceresearch.ai/evoharness/

The benchmark models non-stationarity in the externally supplied harness, not only in the task stream. It covers expanding tools, reusable skills, and specialist-agent pools, with cumulative stages and both deployment and self-evolving adaptation evaluations.

Relevant observations reported by the authors:
- Harness expansion can degrade performance on previously solvable tasks even when the underlying model weights and task-relevant capability remain available.
- Retention and adaptation are not aligned automatically: preserving old performance does not guarantee better adaptation to new capabilities, and vice versa.
- In the expanding-agent analysis, forgotten tasks show more delegation drift than retained tasks. The paper reports that, without adaptation, drift rises from 13% to 25% in the cited comparison.
- The authors' analysis says the dominant failure is not simply that the Agent starts calling newly added irrelevant specialists. Forgotten tasks more often stop invoking specialists that were part of previously successful executions.
- Across methods, high specialist recall can come with more distractor delegation, while conservative methods can reduce distractors at the expense of recall. The paper concludes that selective routing under a growing pool remains difficult.

Research implication: this is a concrete, measurable behavior—not merely a general request for higher success rate:
> When the available specialist-agent pool expands, does the evolved policy preserve previously successful required-agent coverage while adapting to tasks that need newly introduced specialists?

This observation is already reported by the benchmark paper. Repeating the observation is not novel. A contribution would need a new mechanism that addresses the observed failure and beats existing methods.

### 2.3 HarnessLens: selective verification and regression checks are already close prior art

Source: Xu et al., *Verify Smarter, Evolve Further: Efficient Harness Evolution through Behavior-Aware Verification*, arXiv:2608.27311.
- Paper: https://arxiv.org/abs/2608.27311
- Code: https://github.com/jhxu5214/HarnessLens

The paper describes task/component exploration, trajectory-derived candidate changes, selective verification on behavior-relevant tasks, and an attributable-evidence gate. It also says candidate modifications should be checked for regressions.

Research implication: the following are not defensible as standalone novelties:
- evaluating only tasks related to the changed behavior;
- retaining a change only when the target behavior improves;
- checking whether old behavior regresses;
- attaching trajectory evidence to a proposed change;
- making verification more budget-aware.

A future method must differ from these mechanisms in a precise, testable way. The exact implementation and evaluation code still need inspection; paper-level claims are not independent replication.

### 2.4 Evaluation controls: search must beat simple alternatives under matched budgets

Source: *Rethinking the Evaluation of Harness Evolution for Agents*.
- Project-reported source: https://arxiv.org/abs/2607.12227

The paper argues that harness-evolution studies need simple task-level search and test-time-scaling baselines under matched feedback/inference budgets, and must evaluate on disjoint held-out tasks. Its reported results warn that automated harness evolution does not consistently outperform simple alternatives.

Research implication: any future EC mechanism must be compared with at least:
- the original method without the proposed change;
- simple random valid edits;
- local/greedy search or sequential refinement;
- a strong existing harness-evolution method where feasible;
- matched-budget test-time scaling or repeated sampling where relevant.

The same task feedback, LLM calls/tokens, environment episodes, tool calls, and wall-clock/evaluation budget must be accounted for. A positive development-set result is not enough.

## 3. What is and is not established

| Claim | Audit status | Reason |
|---|---|---|
| Harness expansion can cause regression on earlier tasks | Supported by primary-source benchmark report | EVOHARNESSBENCH reports controlled expansion experiments |
| Previously successful specialist invocations can disappear on forgotten tasks | Supported as an author-reported mechanism analysis | Delegation drift analysis in the paper |
| EVOTOOL's generic blame + targeted mutation + diversity selection is new for this project | Rejected | Directly covered by ACL 2026 paper |
| Generic behavior-aware verification/regression gating is new | Rejected | HarnessLens directly covers it |
| A new EC mechanism can improve retention and adaptation simultaneously | Unproven | No experiment or surviving algorithm has established this |
| A cohort/lineage-aware EC selector would be novel | Unresolved; not admitted | Could overlap multiobjective selection, quality-diversity, continual learning, regression testing, or existing harness evolution |
| The current AES scaffold can reproduce the published benchmark result | Unproven | No reproduction has been run; the project environment is not the external benchmark |
| The project should immediately run a pilot | No | Mechanism-level prior-art audit is incomplete |

## 4. Narrow research question to investigate—not yet a method candidate

Question: Under stage-wise expansion of a specialist-agent pool, can an EC-specific policy-update/selection mechanism reduce delegation drift on previously solved task cohorts without reducing success on tasks requiring newly introduced specialists, compared with strong matched-budget baselines?

This question is narrower than “improve Agent harness evolution” and tied to a measurable failure mode. It is still not an approved method, novelty claim, or experiment authorization.

### Measurements required if the question survives further audit

1. Old-cohort retention: success on tasks solvable before a capability-pool expansion.
2. New-cohort adaptation: success on tasks requiring newly introduced specialists.
3. Required-specialist recall: fraction of required specialists invoked.
4. Distractor delegation rate: unnecessary specialist calls per task.
5. Delegation drift: change in the invoked specialist set for the same previously solved task across harness stages.
6. Cost: model calls/tokens, environment episodes, tool calls, and wall-clock.
7. Trade-off: report retention and adaptation separately; do not hide a regression behind a single aggregate score.

The benchmark paper's annotated required capabilities can support diagnostic evaluation, but any oracle information must not be exposed to the policy at inference time. The evaluator may use it privately.

## 5. Critical novelty risks

The obvious approaches are already crowded:
- keeping an archive of old specialists or old task winners;
- adding a retention objective to average success;
- preserving candidates that win on at least one old task;
- adding a regression test gate;
- selecting tasks relevant to a proposed change;
- using a Pareto front for retention versus adaptation;
- adding a generic contextual controller to choose mutation operators.

These are useful baselines and may be components, but they cannot be presented as new by themselves. Before any method proposal, audit existing mechanisms in:
- continual learning / backward transfer and stability-plasticity;
- multiobjective evolutionary optimization and quality-diversity;
- policy population methods and specialist preservation;
- routing/delegation under expanding tool or agent pools;
- HarnessLens and related selective-verification methods;
- evolutionary and non-evolutionary search under equal budgets.

The audit must find a specific failure of the closest existing method, not just a different benchmark or a different combination of known parts.

## 6. Required next research actions

Read-only only; no candidate-generation phase and no experiments yet.

1. Inspect the public HarnessLens implementation, focusing on task selection, paired evaluation, regression detection, and its acceptance gate.
2. Inspect EVOHARNESSBENCH's released artifacts/data/code availability and identify which delegation-trace fields can be reproduced without touching its held-out evaluation data.
3. Compare EVOTOOL's instance-wise winner-frequency selection with HarnessLens's behavior-aware verification on the exact old-cohort/new-cohort failure above.
4. Search primary literature for prior evolutionary methods that preserve old specialist-delegation behavior while adapting policy to a growing agent pool.
5. Write a claim-by-claim nearest-neighbor matrix, with evidence grade (FULL/PARTIAL/SECONDARY), exact mechanism, overlap, and unresolved questions.
6. Only if a specific gap survives, define one falsifiable mechanism hypothesis and an experiment protocol for later approval. Otherwise report NO_GO for this specific route and preserve the evidence.

### Stop rules

- If a close method already preserves old-task behavior while adapting to new specialists under the same setting, do not rename it; study whether it has a documented failure that can be repaired.
- If the only difference is adding a regression metric, a Pareto objective, or an archive, do not admit a new method.
- If EC does not beat random/local search and a strong non-EC baseline under matched budgets, do not claim an EC-specific contribution.
- Do not access held-out/test tasks or call a live LLM API during this audit.

## 7. Handoff prompt

Continue research in yujian777555/agentfotagent, branch research/evoharness-retention-mechanism-audit. Read this document and status.json, plus the Phase-1A-14 through Phase-1A-18 decision/audit documents. This is an independent primary-source mechanism audit, not a Phase-1A-19 candidate-generation handoff. Inspect HarnessLens code and EVOHARNESSBENCH public artifacts, then audit the closest evolutionary/continual-learning methods for preserving old specialist-delegation behavior while adapting to a growing agent pool. Do not implement a method, call a live LLM API, run MetaBox/AES scientific experiments, use GPUs, or access held-out/test data. Return a source-grounded comparison matrix and a GO/NO-GO decision on whether a specific mechanism-level gap survives.

## 8. References

1. Yang, S. et al. (2026). *EvoTool: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection*. ACL 2026. https://aclanthology.org/2026.acl-long.2016/
2. Ke, Z. et al. (2026). *EVOHARNESSBENCH: Can Your Agents Keep Pace with an Evolving Harness?* arXiv:2609.04280. https://arxiv.org/abs/2609.04280
3. Xu, J. et al. (2026). *Verify Smarter, Evolve Further: Efficient Harness Evolution through Behavior-Aware Verification*. arXiv:2608.27311. https://arxiv.org/abs/2608.27311
4. Wang, Y. et al. (2026). *Rethinking the Evaluation of Harness Evolution for Agents*. https://arxiv.org/abs/2607.12227

## Final status

RESEARCH_SIGNAL_FOUND; METHOD_NOT_ADMITTED; NO_EXPERIMENT_AUTHORIZED.

This audit deliberately does not overturn Phase-1A-18's pause. It identifies a concrete empirical failure to investigate further while preserving the requirement that any future method must improve an existing approach for a demonstrable reason.


## 9. Implementation-level check: HarnessLens

The public repository was inspected read-only at https://github.com/jhxu5214/HarnessLens (default branch main). Relevant files include README.md, harnesslens/evolution/controller.py, analyzer.py, discovery.py, incumbent.py, main_agent.py, and evaluation/blind_test_eval.py.

What the code confirms:
- The repository separates the TRAIN evolution loop from blind TEST evaluation entrypoints.
- The evolution pipeline explores task categories and editable harness surfaces, diagnoses experiences, creates candidate changes, materializes isolated harness versions, and evaluates paired rollouts.
- The main decision prompt explicitly distinguishes recovered tasks, preserved tasks, attributable regression tasks, and unresolved findings.
- The controller records accepted TRAIN evidence and can load a prior TRAIN-accepted incumbent with its changed-channel provenance and previously attributed recovered/preserved/regression task IDs.
- The implementation uses paired rollout/confirmation budget calculations and a separate blind-test evaluator. This supports the conclusion that generic paired behavior verification, incumbent preservation, and regression-aware acceptance are already implemented engineering mechanisms in HarnessLens.

What this does NOT prove:
- It does not establish that HarnessLens solves the EVOHARNESSBENCH expanding-specialist-pool setting. Its public README describes OpenCode, Codex CLI, and Pi harness evolution across Retail/Banking, Terminal-Bench, and BIRD Mini-Dev; it does not claim an evolving external specialist-agent roster benchmark.
- It does not establish that HarnessLens has an EC-specific population update/selection mechanism that solves the reported old-specialist delegation drift.
- The presence of fields such as preserved_task_ids or attributable_regression_task_ids is not proof that the attribution judge is always correct. The paper's evaluation and the code's implementation still need independent scrutiny; this project has not reproduced its performance claims.

Source links:
- README: https://github.com/jhxu5214/HarnessLens/blob/main/README.md
- Controller: https://github.com/jhxu5214/HarnessLens/blob/main/harnesslens/evolution/controller.py
- Main decision logic: https://github.com/jhxu5214/HarnessLens/blob/main/harnesslens/evolution/main_agent.py
- Incumbent evidence: https://github.com/jhxu5214/HarnessLens/blob/main/harnesslens/evolution/incumbent.py

## 10. Revised interim decision after code inspection

The broad idea “use behavior-aware evaluation and reject regressions” is now **explicitly NO-GO as a standalone novelty claim**, because HarnessLens already implements a behavior-aware candidate verification and regression-attribution workflow.

The remaining question is narrower: whether a distinct EC population-update or variation mechanism can address the specific loss of previously required specialist invocations under stage-wise external agent-pool expansion, beyond the existing HarnessLens acceptance gate, EVOTOOL's instance-wise winner-frequency selection, and standard multiobjective/quality-diversity/continual-learning baselines.

No answer is claimed yet. The next action remains a read-only prior-art audit of evolutionary population methods and continual adaptation under changing specialist-agent sets. If the only viable proposal is an archive, regression gate, Pareto objective, or task-conditioned routing rule already covered by prior art, stop this route. No method, experiment, API call, or held-out access is authorized by this note.


## 11. Expanded nearest-neighbor audit: retention, plasticity, and multi-objective evolution

A targeted search after the HarnessLens code inspection found additional close prior work. This further narrows what can plausibly be claimed as novel.

| Work | Evidence grade | Mechanism directly relevant here | Consequence |
|---|---|---|---|
| Pareto Continual Learning (AAAI 2025) | FULL publisher abstract; full mechanism not yet audited here | Formulates stability versus plasticity as multi-objective optimization and learns Pareto trade-offs | “Use Pareto optimization to balance retention and adaptation” is already covered in continual learning. https://doi.org/10.1609/aaai.v39i17.33981 |
| Continual Evolution Strategies in Control Tasks (GECCO 2026 Companion; arXiv:2608.13600) | FULL paper text inspected | Sequential ES with replay evaluations on prior tasks; measures backward transfer, forward transfer, and interference; replay improves retention but large replay harms plasticity | Replay old tasks during EC search and report the retention/adaptation trade-off are not new mechanisms. The domain is continuous control, not Agent harnesses. https://arxiv.org/abs/2608.13600 |
| Neuro-evolutionary Continual Reinforcement Learning (ICML 2026) | FULL publisher abstract; code link reported | Maintains task-specific mask populations, stores best masks, freezes activated neurons, reuses neurons by task similarity, and uses importance-guided crossover | Evolutionary preservation of old skills while adapting to new tasks is already studied in continual RL. The representation and domain differ from LLM Agent delegation. https://proceedings.mlr.press/v306/li26gb.html |
| Multi-Objective Agent Evolution with Pareto-Preserving Search (MOAE; arXiv:2609.05992) | PARTIAL: abstract-level evidence from a surfaced paper record; full text not independently inspected | Evolves complete Agent rollouts while preserving non-dominated candidates over task performance, trajectory quality, and safety; uses objective-specific diagnostics and deployment-time constrained selection | “Use a Pareto archive for multi-objective Agent evolution” is already a direct neighboring claim. Full paper/code review is required before stronger comparison. https://arxiv.org/abs/2609.05992 |
| HarnessLens (arXiv:2608.27311 + public code inspected) | PARTIAL-to-FULL for implementation structure; no independent reproduction | Behavior-relevant paired verification, attributable improvement/regression evidence, TRAIN-accepted incumbent provenance, and separate blind TEST path | “Add regression-aware verification and preserve an incumbent” is not new. |
| EVOTOOL (ACL 2026) | FULL paper text inspected; no public implementation confirmed | Module-level blame, single-module targeted mutation, instance-wise winner-frequency population selection | “Keep diverse old-task specialists using instance-level winners” is not new. |

### Updated ruling

The following broad formulations are now explicitly rejected as standalone novelty:
- retention + adaptation as two objectives;
- replay of old tasks during evolutionary search;
- a Pareto archive of Agent policies;
- an archive of candidates that win on old task instances;
- a regression gate or behavior-specific verification;
- freezing old capabilities/genes/modules without a new mechanism;
- task-similarity-based reuse of old policies as a generic idea.

The empirical observation in EVOHARNESSBENCH remains a useful *problem setting*, but the obvious remedies are already occupied by continual learning, evolutionary continual learning, multi-objective Agent evolution, and HarnessLens. The current research signal therefore does not yet imply a viable EC contribution.

## 12. What could still justify a genuine improvement?

Only a narrower result can reopen the route: identify a concrete failure of a close existing method in the expanding-specialist setting, then demonstrate why a specific EC operator or survivor/parent-selection mechanism fixes that failure better than the close method itself.

Potential diagnostic questions for the read-only audit—not algorithm proposals:
1. Does EVOTOOL's single-module blame assignment misidentify a failure when the correct old specialist is no longer selected after a new specialist is added?
2. Does its instance-wise winner-frequency selection retain a candidate that wins an isolated task but has fragile required-specialist coverage across later harness stages?
3. Does HarnessLens's behavior-relevant paired verification explicitly model stage transitions and old/new specialist cohorts, or does it evaluate candidate edits within a fixed harness context?
4. Do existing evolutionary continual-learning methods preserve a task-specific solution, but fail to preserve the *delegation structure* that made a multi-agent execution successful?
5. Are any such failures actually caused by EC selection/variation, rather than the base LLM's routing behavior or the harness API?

These are falsifiable questions to investigate in papers/code, not assertions that the methods fail. If source/code inspection does not reveal a concrete gap, close this route. Do not infer a novelty gap merely because two papers use different benchmarks or representations.
