# Phase-1A-18 Follow-up — Harness-Expansion Retention/Adaptation Audit

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Status: **PRIMARY_SOURCE_GROUNDED_RESEARCH_LEAD; NOT_ADMITTED; PHASE1A18_PAUSE_REMAINS**
- Scope: source-level literature and project-code audit only. No method implementation, live API call, MetaBox/AES scientific run, GPU job, or held-out access occurred.

## 1. Why this is now the priority follow-up

The supplied prior-session record identifies a more concrete research problem than generic Agent self-improvement: **when the externally supplied set of tools, skills, or specialist agents grows, previously successful tasks may regress because the agent stops invoking capabilities that remain available.**

This follow-up gives that problem priority. The EVOTOOL blame-to-intervention mismatch recorded in docs/PHASE1A18_EVOTOOL_BLAME_ACTIONABILITY_AUDIT.md remains a secondary empirical lead, not the main thesis candidate.

The project-wide decision is unchanged: **do not reopen method discovery or create Phase-1A-19 yet.** The task is to determine whether a precise evolutionary-computation mechanism remains uncovered after auditing the nearest primary sources.

## 2. Primary-source evidence

### 2.1 EVOHARNESSBENCH identifies a measurable failure mode

Ke, Z., Patil, V., Shi, H., Li, Y., Liu, Y., Shekkizhar, S., Koul, A., Wang, J., Nguyen, X. P., Yavuz, S., Bansal, M., & Joty, S. (2026). *EvoHarnessBench: Can Your Agents Keep Pace with an Evolving Harness?* arXiv:2609.04280v3. https://arxiv.org/abs/2609.04280

The benchmark treats the externally supplied harness—not only the task stream—as non-stationary. It contains 17 multi-stage streams, 802 unique tasks, 520 tools, 42 skills, and 62 specialist agents. It separately evaluates deployment retention under harness expansion and self-evolving adaptation with persistent artifacts.

Specific evidence relevant to this project:

- The largest reported harness-induced forgetting is on the evolving-agent axis: deployment backward transfer reaches **−34.7%** in the Agents' Last Exam setting.
- In the evolving-agent analysis, forgotten tasks show substantially more delegation drift than retained tasks; without adaptation, the reported drift rises from **13% to 25%**.
- The paper attributes the regression mainly to previously required specialists no longer being invoked, rather than solely to newly added irrelevant specialists.
- Adaptation raises required-specialist recall from roughly 79% to as high as 89%, while selection precision remains around 90%; this does not eliminate the tension between required-agent coverage and unnecessary delegation.
- The paper reports that no evaluated mechanism simultaneously achieves high specialist recall and low distractor routing as the pool grows.

These are author-reported results from a preprint/benchmark paper, not an independent replication. The exact figures and definitions must be retained with their original setting; they should not be merged into one generic forgetting percentage.

### 2.2 Capability-preserving evolution is a direct overlap warning—and states a boundary

Yu, Y., Yuan, X., Jin, H., Liu, H., Yu, Y., & Wang, H. (2026). *Do Self-Evolving Agents Forget? Capability Degradation and Preservation in Lifelong LLM Agent Adaptation.* arXiv:2605.09315v1. https://arxiv.org/abs/2605.09315

The paper proposes Capability-Preserving Evolution (CPE), using the generic objective
\[
\mathcal{L}_t(R)+\lambda\Omega_t(R,R_{t-1}),
\]
where the preservation term discourages destructive changes to prior capability-supporting structures. Its instantiations include behavioral anchors for workflow evolution, skill-repository consolidation, Fisher-weighted parameter constraints, and evidence-gated memory preservation.

Consequences for this project:

- “Optimize new tasks while preserving old-task performance” is **not** a novel claim by itself.
- Adding an old-task regression penalty or merely tuning a preservation coefficient would be a weak contribution without a distinct, justified mechanism.
- The paper's Limitations section explicitly leaves more open-ended trajectories involving dynamic environments, multi-agent interaction, and continuously expanding capability spaces as future work. This is a boundary worth auditing, not proof of novelty.

### 2.3 Continual self-evolution already studies stability–plasticity and interference

Chen, X., Huang, Y., Xu, Y., Zhao, Z., McQuinn, E., Liu, J., & Yao, H. (2026). *Are Self-Evolving Agents Continual Learners?* arXiv:2610.25858v1. https://arxiv.org/abs/2610.25858

This preprint evaluates ReasoningBank, GEPA, and Meta-Harness on topic, workflow, domain, and compound task-stream shifts. It reports a stability–plasticity trade-off: global prompt/workspace edits can interfere with unseen tasks and overwrite earlier knowledge, while similarity-based memory retrieval can introduce foreign memories and retrieval collisions.

It is adjacent to the target problem. Its primary non-stationarity is the task stream and self-evolved harness state; the specific externally expanding tool/skill/specialist pool in EvoHarnessBench remains a narrower setting to compare, not an assumed novelty gap.

## 3. Additional nearest-neighbor methods that block superficial claims

| Work | Mechanism already covered | What this means here |
|---|---|---|
| EVOTOOL (ACL 2026) | Modular tool-use policy evolution; trajectory-grounded blame; targeted single-module mutation; diversity-aware population selection | “Use EC to evolve Agent tool-use policies” is not new. Any proposed change must address a concrete failure EVOTOOL does not solve and beat it or a faithful baseline. |
| AEL (Findings of EMNLP 2026) | Fast Thompson Sampling over memory-retrieval policies plus slower LLM diagnosis/reflection that can add a new policy arm | Generic adaptive policy selection or diagnosis-triggered policy addition is already covered. |
| HarnessForge (EMNLP 2026) | Joint harness–policy co-evolution, fault-guided harness tailoring, and policy alignment | “Co-evolve the harness and internal policy” is not new by itself. |
| Harness Updating Is Not Harness Benefit (EMNLP 2026) | Separates the ability to produce useful harness updates from the ability of an executing agent to benefit from them | Candidate-update quality alone is insufficient; the downstream agent must actually improve. |
| Evo-Harness (EMNLP 2026) | Compiles noisy execution context into reusable skills for online adaptation | Skill extraction/compilation from trajectories is an existing alternative. |
| Classical AOS, GP, multi-objective EA and quality-diversity methods | Operator credit assignment, structured program/policy search, Pareto trade-offs, and behavior-diverse archives | These are mandatory nearest baselines. A multi-objective formulation, archive, or adaptive operator schedule is not a novelty claim by itself. |

Primary sources:

1. Yang et al. (2026), *EVOTOOL*, ACL 2026. https://aclanthology.org/2026.acl-long.2016/
2. Xu et al. (2026), *AEL: Evolving Agent Harness in Open-Ended Environments*, Findings of EMNLP 2026. https://aclanthology.org/2026.findings-emnlp.1316/
3. Chen et al. (2026), *HarnessForge: Joint Harness and Policy Evolution for Adaptive Agent Systems*, EMNLP 2026. https://aclanthology.org/2026.emnlp-main.1893/
4. Lin et al. (2026), *Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents*, EMNLP 2026. https://aclanthology.org/2026.emnlp-main.2326/
5. Wei et al. (2026), *Evo-Harness: Context-to-Harness Skill Compilation for Self-Evolving Agents*, EMNLP 2026. https://aclanthology.org/2026.emnlp-main.969/

The existence of these papers does not prohibit a method improvement. It means the improvement must be defined against their exact mechanisms rather than against a generic “baseline Agent.”

## 4. Project-code fit audit: current AES does not yet implement harness expansion

A read-only inspection of the current project code confirms that the present AES can serve as a controlled Agent-policy search scaffold, but it cannot yet reproduce this particular failure mode without an environment extension.

Frozen code references on the working branch:

- src/agentfotagent/environments/tool_world.py, blob SHA 563c164a660a5b337e664d7a4eea016794457409
  - Defines fixed READ_ONLY_TOOLS, STATE_CHANGING_TOOLS, and ALL_TOOLS; the exposed tool set is not stage-versioned.
- src/agentfotagent/tasks/generators.py, blob SHA 962f3b628353488311701be186f753d4023df8c1
  - Current task families are key_crate, dial_set, and held-out-only relay_route; there is no staged external capability-release stream.
- src/agentfotagent/genome/schema.py, blob SHA 907dd9b37d8e601b1214ddf182dab8d3911b672e
  - The current four genes cover planning mode, memory policy, verification policy, and tool-selection policy. There is no explicit specialist-delegation genome or delegation-set trace contract.

Thus the existing AES must not be described as already supporting EvoHarnessBench-style external harness evolution. Any later target-domain test would first require a separately reviewed environment/evaluator extension and new disjoint task-family splits. No such extension is authorized in this audit.

## 5. Candidate problem boundary—not a method proposal

The only problem boundary that currently merits further prior-art checking is:

> Under an externally expanding specialist/tool capability pool, can an evolutionary update/selection mechanism preserve the required behaviors for previously solved task cohorts while improving adaptation to newly introduced capabilities, without increasing unnecessary delegation or relying on a larger evaluation budget?

The observed failure is more specific than aggregate “forgetting”: old tasks can stop invoking previously required specialists, while mechanisms that increase recall may also route to more distractors.

This is **not yet a method or innovation point**. The following simple formulations are already too weak:

- adding an old-task score to the fitness function;
- optimizing old/new task success as two objectives without a mechanism-level reason;
- using a generic Pareto archive or NSGA-II/III;
- scheduling modules from historical acceptance rate;
- adding a generic retention coefficient;
- co-evolving harness and policy without a specific uncovered failure mechanism.

## 6. Falsifiable gate for any future proposal

A future method proposal must specify, before any experiment:

1. **Target behavior:** a deterministic trace-level definition of previously required specialist/tool coverage, new-capability usage, and unnecessary delegation.
2. **Failure reproduction:** the same previously successful task must be re-evaluated under a larger capability pool, and the trace must show whether required calls disappeared or distractor calls increased.
3. **EC-specific mechanism:** the exact genotype, variation/update rule, selection rule, and reason the mechanism should outperform ordinary search. “Use NSGA-III” or “keep old-task scores high” is insufficient.
4. **Equal-budget baselines:** static/no adaptation; random search; local search; conventional EA/GP; EVOTOOL-style targeted mutation; CPE-style preservation; an appropriate multi-objective EA; and an LLM-only or fixed-policy-selection comparator where semantics match.
5. **Separate outcomes:** old-cohort retention, new-cohort adaptation, required-call recall, distractor rate, end-to-end verified success, and evaluation/tool/token cost.
6. **Independent task families:** tune only on development tasks; reserve held-out task families and do not inspect their outcomes during method selection.
7. **Stop rules:** if standard EA, random/local search, CPE-style preservation, or an equal-budget simple policy matches the proposed method, or if only the aggregate score improves while retention/adaptation trade-off worsens, close the method claim.

No experiment should start until the mechanism-level prior-art audit and an explicit scope/budget approval are complete.

## 7. Decision and next action

**Decision: LEAD_UNRESOLVED_MORE_PRIMARY_SOURCE_NEEDED.** The problem is well-motivated by primary-source evidence, and CPE itself names dynamic, multi-agent, expanding capability spaces as a future-work boundary. However, the exact EC-specific mechanism gap remains unproven in the presence of EVOTOOL, AEL, HarnessForge, CPE, continual self-evolution work, and classical evolutionary/quality-diversity methods.

Next action: conduct a source-level mechanism comparison, including official code where available, focused on how each method represents and preserves prior delegation behavior as the available tool/agent set changes. If the only difference left is a standard retention objective, archive, or operator scheduler, record NO-GO and keep the project paused. Only a precise uncovered mechanism may justify drafting a development-only protocol.

### Hard limits

- 0 live LLM API requests.
- 0 MetaBox performance experiments.
- 0 AES scientific performance runs.
- 0 GPU hours.
- No held-out/test access.
- No new algorithm implementation or Phase-1A-19 candidate-generation handoff.
- Do not modify openissue, EvoPareto-Agent, or any other repository.

---

# Audit Round 2 — Direct Prior Art for Continual Multi-Agent Delegation

- Date: 2026-11-02
- Status: **LEAD_NARROWED; METHOD_GAP_UNRESOLVED; PHASE1A18_PAUSE_REMAINS**
- Scope: publisher/preprint paper inspection plus read-only inspection of official source repositories where available. No code in agentfotagent was changed; no experiment, live API, MetaBox/AES run, GPU job, or held-out access occurred.

## 8. Correction and precise reading of the benchmark evidence

The 13% to 25% delegation-drift comparison in EvoHarnessBench is **not** a general before/after increase caused by adaptation. It compares previously solved tasks that remain retained with those that become forgotten, under the no-adaptation condition: forgotten tasks show more delegation drift (25%) than retained tasks (13%). The paper further says that the drift is mainly explained by previously required specialists no longer being invoked, not simply by newly added irrelevant agents being invoked.

Additional agent-axis evidence from the same paper:

- Under cumulative agent-pool deployment, Codex moves from 6.5% to 8.8% pass rate on EOG, but from 5.3% to 4.2% on ALE. Pool expansion is environment-dependent.
- On ALE, deployment backward transfer reaches -34.7%, the largest harness-induced forgetting reported across the tool, skill, and agent axes.
- On EOG, required-agent precision remains around 90%, while required-agent recall improves from 79% without adaptation to as high as 89%. This points to delegation completeness rather than simply choosing more relevant agents.
- For Meta-Harness on EOG, cumulative adaptation scores 18.5%; task-specific agent exposure scores 19.4%; exposing the final pool from the beginning, with no staged pool change during adaptation, scores 20.3%. The paper interprets the sequence of pool changes—not just pool size—as a source of difficulty.
- The paper explicitly proposes bi-level adaptation as future work: inner updates adapt persistent state, while an outer objective evaluates whether updates remain effective across harness stages.

Source: Ke et al. (2026), EvoHarnessBench, Sections 4.3–5, Table 6–8 and Figure 6–8, arXiv:2609.04280v3, https://arxiv.org/abs/2609.04280.

## 9. New direct and adjacent competitors

### 9.1 EvoMAS — graph evolution, role specialization, and cross-stage stability

Wei, Y., Huang, Z., Xu, R., Wang, H., & Xing, W. W. (2026). *EvoMAS: Heuristics in the Loop—Evolving Smarter Agentic Workflows*. Proceedings of the 43rd International Conference on Machine Learning, PMLR 306, 133736–133763. https://proceedings.mlr.press/v306/wei26m.html

The published ICML abstract confirms three highly overlapping components: a seven-strategy evolutionary repertoire (six exploration/exploitation strategies plus a custom strategy), role-level evolution of agent specialization and collaboration, and curriculum-guided evolution with cross-stage stability.

The accessible full-text submission version formalizes a workflow as a directed graph and describes diversity expansion, conceptual recombination, cross-domain hybridization, fine optimization, best-practice synthesis, and role specialization. It also describes a Cyber Creator that revises rules and strategy distributions from evolutionary history. Its cross-stage stability constraint uses cumulative average performance over all difficulty stages. This is a direct overlap warning:

- Generic graph-based evolution of multi-agent workflows is already covered.
- Generic role specialization and dynamic operator selection are already covered.
- Generic curriculum-based retention across earlier task stages is already covered.
- A new proposal cannot claim these mechanisms as its contribution merely by applying them to another Agent benchmark.

Important boundary: the published abstract and the accessible full-text submission version are not the same artifact. Detailed formula-level claims in this audit are attributed to the accessible submission text; they must be checked against the final PMLR PDF before being quoted as final-version details. A stable official source-code repository was not independently verified in this pass.

### 9.2 MAS-Orchestra — holistic multi-agent graph orchestration through RL

Ke, Z., Ming, Y., Xu, A., Chin, R., Nguyen, X.-P., Jwalapuram, P., Wang, J., Yavuz, S., Xiong, C., & Joty, S. (2026). *MAS-Orchestra: Understanding and Improving Multi-Agent Reasoning Through Holistic Orchestration and Controlled Benchmarks*. ICML 2026, PMLR 306, 56527–56570. https://proceedings.mlr.press/v306/ke26c.html

The method casts orchestration as function-calling RL. The orchestrator creates a complete multi-agent orchestration in one decision, using callable goal-oriented subagents and a task-level reward. The paper uses GRPO and introduces MASBENCH with Depth, Horizon, Breadth, Parallel, and Robustness axes. Official code: https://github.com/SalesforceAIResearch/MAS-Orchestra (repository HEAD inspected: 0527c70a508eb49ed42d5dd49a91ea857551e242).

This is a strong non-EC baseline for selecting multiple specialists and constructing their communication/dependency topology. Its reported benchmark is not a continual external-pool expansion protocol and does not establish retention of previously successful delegation sets across successive agent-pool versions.

### 9.3 CARvE / Continual Model Routing — direct overlap on an expanding expert label space

Bell, J., Carfi’, G., Gramaglia, G., & Lomonaco, V. (2026). *Continual Model Routing in Evolving Model Hubs*. ICML 2026, PMLR 306, 7412–7453. https://proceedings.mlr.press/v306/bell26a.html

CARvE is the strongest newly identified adjacent method for the pool-expansion aspect. It treats routing as class-incremental learning over a growing set of model IDs and introduces CMRBench with four sequential experiences and over 2,000 candidate models. Its method uses:

- a prompt encoder and learned model-ID embedding registry;
- fixed-size candidate-set contrastive training;
- hard, semantic, and far negative sampling;
- domain–model coreset replay;
- checkpoint anchoring of previously seen model-ID embeddings and the projection, while newly added IDs remain unanchored.

With 10% replay, the paper reports 80.7% domain accuracy and 5.9% forgetting versus 75.9% and 13.1% for standard replay. Official code: https://github.com/atlas-luiss/CMR (HEAD 712e77b31d254918d38b5c126ba7d793b841d20b). Static code inspection confirmed the router embedding registry, candidate sampling, hard-negative mining, and old-ID/projection anchor implementation; relevant blobs include router.py (8cc15bf...), router_regularizers.py (79dc750...), and hard_mining.py (caf7be8...).

Boundary: CARvE predicts one model ID for a query. It does not construct a set of multiple required specialists, an ordered delegation plan, or an inter-agent graph, and it does not measure end-to-end success after the selected experts interact. It is nevertheless a mandatory continual-routing baseline; an evolutionary method must outperform or complement this mechanism in the genuinely multi-agent setting, not ignore it.

### 9.4 MASQD — multi-agent quality-diversity as a required EC baseline

Iyer, S., Aydeniz, A. A., et al. (2026). *Multiagent Quality-Diversity for Effective Adaptation*. ECAI 2025 proceedings, first published online 2026-08-25. https://doi.org/10.3233/FAIA251201

MASQD builds an archive of diverse, high-performing multi-agent teams using CEM-RL, a team-level policy representation, archive-anchored exploration, and a descriptor-conditioned critic. It evaluates multi-agent MuJoCo teams under environmental perturbations. This is not an LLM specialist-pool benchmark and does not address temporal agent-pool growth, but it blocks any superficial claim that an archive of diverse multi-agent solutions is itself new. Its behavior-descriptor design and QD metrics should be considered in future baseline design.

### 9.5 Harness Updating Is Not Harness Benefit — activation and adherence are separate from update quality

Lin, M., Wu, J., Wang, Z., et al. (2026). *Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents*. EMNLP 2026, pp. 52829–52852. https://aclanthology.org/2026.emnlp-main.2326/

This paper separates the ability to write useful harness updates from the ability of the task-solving model to benefit from them. It identifies harness-activation failure (relevant artifacts are not invoked) and harness-adherence failure (artifacts are loaded but not followed). Its protocol keeps the model backbone, tool interfaces, and execution policies fixed; evolvable components are skills, prompts, and memories depending on the benchmark. It therefore does not solve external specialist-pool expansion, but it reinforces a necessary evaluation rule: score actual invocation and use, not only the quality of the proposed update or the router's nominal selection.

### 9.6 HarnessForge — confirmed joint harness-policy evolution

Chen et al. (2026). *HarnessForge: Joint Harness and Policy Evolution for Adaptive Agent Systems*. EMNLP 2026. Paper: https://aclanthology.org/2026.emnlp-main.1893/; official code: https://github.com/mingju-c/HarnessForge (HEAD 8bef9488c35a21ef510a6f069476305025ba5519).

Read-only inspection of the official README confirms a three-stage harness-tailoring pipeline: module localization from trajectories, archive-guided improvement-direction generation, and candidate harness generation, followed by validation and Pareto-style survivor filtering. A separate policy-alignment loop turns successful rollouts into SFT data. This blocks generic claims about jointly evolving harness structure and task-solving policy. The inspected protocol does not establish per-cohort retention of required specialist sets under a temporally changing external agent pool.

### 9.7 AEL — adaptive policy arms do not equal an evolving specialist pool

Xu et al. (2026). *AEL: Evolving Agent Harness in Open-Ended Environments*. Findings of EMNLP 2026. https://aclanthology.org/2026.findings-emnlp.1316/

The paper's default setting keeps the planner, 12-tool set, and tool implementations fixed, while using Thompson Sampling over memory-retrieval policies and slower LLM reflection to add policy arms. Optional planner LinUCB and per-tool Thompson Sampling are disabled in the default configuration because they degrade results in the short-horizon setting. Thus AEL is a relevant policy-adaptation baseline, not direct evidence that continual multi-agent delegation under an expanding specialist pool is solved.

### 9.8 CPE and EVOTOOL remain major overlap controls

CPE already addresses old/new capability retention in workflow, skill/tool, model, and memory evolution. Its skill/tool experiment uses a bounded 30-skill bank, top-5 retrieval, and sequential domains; its limitations explicitly identify dynamic environments, multi-agent interaction, and continuously expanding capability spaces as future work. It blocks a generic retention-regularizer claim.

EVOTOOL already provides modular tool-use policy evolution with trajectory-grounded blame, targeted mutation, and diversity-aware selection. It blocks generic blame-aware or module-targeted mutation claims. Its existing single-run blame-to-intervention anomaly remains secondary and does not replace the present primary problem.

## 10. Narrowed problem boundary

The defensible problem boundary is now more precise than general capability retention:

> **Continual, set-valued, graph-structured delegation under an externally expanding specialist-agent pool:** as the available specialist set changes across stages, preserve the required-agent coverage of previously solved task cohorts while adapting to new tasks and specialists, without increasing unnecessary delegation or end-to-end execution cost.

This boundary has three necessary properties:

1. **Set-valued:** a task may require several specialists; choosing one model ID (CARvE) is not enough.
2. **Graph-structured:** invocation order, dependencies, parallelism, and aggregation matter; selection precision alone does not ensure success (MAS-Orchestra and EvoHarnessBench).
3. **Continual under external pool changes:** the set of available specialists and the order in which it changes are part of the environment; task-difficulty curriculum alone (EvoMAS) is not equivalent.

The primary metrics must be separated: old-cohort backward transfer, new-cohort forward transfer, required-agent recall, required-agent precision, exact required-set coverage, invocation/adherence, end-to-end verified success, and delegation cost/latency. Aggregate pass rate alone is insufficient.

## 11. What remains unproven: the EC mechanism gap

A candidate mechanism worth investigating—not yet an innovation claim—is **change-aware evolutionary search over task-conditioned delegation graphs with explicit per-cohort coverage preservation**. It would have to differ from simply adding an old-task score to EvoMAS, applying CARvE-style anchoring to IDs, or using a standard QD archive.

Before any implementation, the following comparisons are mandatory:

- EvoMAS-style graph evolution and its cross-stage stability control;
- MAS-Orchestra-style holistic RL orchestration;
- CARvE-style continual single-expert routing adapted as a multi-label baseline;
- CPE-style preservation;
- HarnessForge-style harness-policy evolution;
- EVOTOOL-style blame-targeted module mutation;
- AEL-style bandit policy selection;
- standard graph GP/EA, NSGA-II/III, MAP-Elites/QD, and a simple local-search baseline.

The mechanism must specify what is uniquely evolved, what is protected, how new specialist IDs enter the genotype, how old cohorts are evaluated, and why the operator/selection rule should beat the above controls at matched evaluation and inference budgets. If a standard graph EA with per-cohort constraints or a QD archive achieves the same result, the proposed EC novelty is not established.

## 12. Project-objective compatibility gate

This target-domain problem does **not** by itself satisfy the repository's original H1/H2/H3 objective. The project charter requires: (H1) Agent-assisted discovery of an EC control mechanism on a source-domain optimizer; (H2) transfer of that high-level control mechanism from MetaBox to an independent Agent-evolution target; and (H3) only conditionally, additional bidirectional feedback. No valid source-to-target transfer object has yet been established. A target-domain graph-evolution paper alone would therefore require an explicit project-scope decision and must not be silently presented as proof of the original two-way-empowerment hypothesis.

## 13. Decision after Round 2

**Decision: KEEP_PAUSE; LEAD_NARROWED; EC_METHOD_GAP_UNRESOLVED.** The audit has found a narrower and better-supported target-domain problem, but the method gap is not yet admitted. New work increases the overlap burden: EvoMAS covers graph evolution, role specialization, dynamic operators, and curriculum retention; CARvE covers continual routing over an expanding expert label space; MAS-Orchestra covers holistic multi-agent graph orchestration; MASQD covers QD archives of multi-agent teams; CPE covers capability preservation; HarnessForge covers joint harness-policy evolution.

Next action: complete the mechanism matrix against these exact methods and classical graph GP/QD/continual routing. Decide whether a distinct EC mechanism remains. No Phase-1A-19, no AES extension, and no experiment before a separate explicit scope/budget authorization.

### Hard limits remain

- 0 live LLM API requests.
- 0 MetaBox performance experiments.
- 0 AES scientific performance runs.
- 0 GPU hours.
- No held-out/test access.
- No new algorithm implementation or Phase-1A-19 candidate-generation handoff.
- Do not modify openissue, EvoPareto-Agent, or any other repository.
