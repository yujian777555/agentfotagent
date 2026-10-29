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
