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
