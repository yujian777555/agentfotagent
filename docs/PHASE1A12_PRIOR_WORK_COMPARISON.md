# Phase-1A-12 Prior-Work Comparison

- Date: 2026-10-29
- Scope: design-stage targeted review of direct Agent-policy evolution versus MetaBox-to-AES transfer.
- No external code executed; no LLM calls; no MetaBox/AES performance runs; no held-out results accessed.
- This is a targeted review, not an exhaustive systematic review. Evidence labels distinguish primary-source pages from prior project notes.

## Decision in brief

**Neither route is cleared as novel.** Direct evolution is more immediately aligned with the target and can be tested without inventing a cross-domain transfer object, but it overlaps strongly with prompt evolution, LLM-assisted evolutionary algorithm design, and Agent self-improvement. Transfer has a more specific research question but currently has no validated source controller and no established state/action correspondence. Phase-1A-12 should design the AES experiment object first and keep transfer as a secondary hypothesis.

## Comparison matrix

| Work | Search object / role of evolution | Feedback and selection | Overlap with direct AES route | Implication |
|---|---|---|---|---|
| EoH (Liu et al., ICML 2024) | Evolves natural-language heuristic thoughts and executable code for heuristic design | Fitness from benchmark execution, evolutionary proposal/selection | Strong overlap with LLM+EC generating executable strategies; target problem differs | “LLM proposes, EA selects executable candidates” is not novel by itself. [Primary proceedings page](https://proceedings.mlr.press/v235/liu24bs.html) |
| LLaMEA (van Stein & Bäck, IEEE TEVC 2025) | Evolves algorithm classes/implementations | Run-time performance feedback, evolutionary mutation/selection | Strong overlap with automated evolutionary search over executable algorithm objects | Need a mechanism beyond generic LLM mutation and fitness selection. [Paper](https://arxiv.org/abs/2405.20132) |
| Promptbreeder (Fernando et al., ICML 2024) | Evolves task prompts and mutation prompts recursively | Training fitness; self-referential mutation-prompt evolution | Direct overlap if AES genotype is merely prompt variants | Avoid presenting prompt/genotype evolution alone as novelty. [Primary proceedings page](https://proceedings.mlr.press/v235/fernando24a.html) |
| GEPA (ICLR 2026) | Reflectively evolves prompts/system components from full execution trajectories; uses Pareto frontier | Natural-language diagnosis, candidate edits, execution feedback, Pareto selection | Very strong overlap with trace-guided Agent/prompt improvement and Pareto selection | A “trace diagnosis + reflection + Pareto evolution” method is already covered at the generic level. [Primary conference page](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html) |
| EvoPrompt / evolutionary prompt optimization | Evolves prompts using evolutionary operators | Task score feedback | Overlap with prompt-as-genome and EA baseline | Must distinguish a policy/controller mechanism from prompt search alone; exact implementation comparison remains to be completed. |
| EvoAgent / ARTEMIS (existing project matrix) | Evolves multi-agent structures/configurations | Task performance and evolutionary selection | Broad overlap with Agent configuration evolution | Generic evolutionary Agent design is not sufficient. Prior matrix evidence varies; retrieve primary papers and code before any novelty claim. |
| Hyperagents (existing project audit) | Modifies the procedure that improves an agent/system, including cross-domain meta-level transfer | Performance feedback over self-modification | Strong overlap with recursive/meta-level improvement and transfer narratives | Bidirectional feedback or transfer story alone is not novel. |
| Harmony Harness (existing project audit) | Evolves compositional general/task-specific harness components with cross-benchmark transfer | Task metrics and harness component selection | Strong overlap with factorized Agent harness and transfer | A componentized genome or cross-task transfer is not enough. |
| LAOS / LLM4EO (existing project audit) | LLM-driven state-conditioned operator/control adaptation in numerical EC | Progress/state and operator-credit feedback | Strong overlap with Track A; less direct overlap with AES target itself | Generic LLM-assisted operator selection should not be the proposed contribution. |

## Route A — direct target-domain LLM-assisted EC

**Definition:** use a fixed LLM backbone as the task-solving Agent, while EC searches a versioned, executable policy/genotype representation that changes planning, memory, verification, tool choice, recovery, or termination behavior. The task evaluator scores actual terminal environment state.

Potentially meaningful research question (not yet a novelty claim):
> Does an explicitly structured, behaviorally testable policy representation let conventional EC discover robust multi-step Agent control policies that generalize to new task templates better than exhaustive/random search and LLM-only self-refinement under matched evaluation cost?

The potential contribution cannot simply be:
- evolving prompts (Promptbreeder/GEPA overlap);
- generating executable heuristics (EoH/LLaMEA overlap);
- using Pareto selection or trajectory reflection (GEPA overlap);
- using a genome of Agent components or cross-benchmark transfer (Harmony Harness and Agent-evolution overlap).

A defensible gap, if primary-source review supports it, would need a specific interaction between **executable policy interventions, verified tool-world state transitions, and task-family generalization**, plus evidence that the evolutionary search contributes beyond exhaustive/random search and LLM-only refinement. This is a hypothesis to audit, not an established gap.

## Route B — MetaBox-to-AES transfer

**Definition:** learn or select one explicit high-level controller object on numerical optimization traces and map its state/action semantics into AES policy evolution.

Current blockers:
1. No Track-A controller passed novelty and performance gates.
2. No validated mapping between numerical state (e.g. population diversity/progress) and Agent-search state (e.g. policy-genotype novelty, task-family success, failure modes).
3. Generic cross-domain meta-transfer and factorized harness transfer are already represented by Hyperagents/Harmony Harness in the project’s prior-work matrix.
4. An adapter alone is not a method contribution.

Transfer is not ready for an experiment. It should be reconsidered only after a concrete controller exists and a source-target mapping can be stated before seeing target outcomes.

## Experimental design implications

For the direct route:
- include exhaustive enumeration as the exact reference for the current 16-genome space;
- use unique-genome random search after redesign;
- include conventional EA and LLM-only/self-refinement;
- match evaluated unique genotypes, task episodes, interaction limits, backend, decoding and costs;
- hold out task templates, not just seeds;
- use shuffled-policy/ablation controls only for a specific causal mechanism.

For the transfer route:
- add target-only controller/search as a strong baseline;
- freeze mapping before target evaluation;
- include shuffled mapping and no-transfer controls;
- do not use held-out results to revise the mapping.

## Reference links

1. Liu et al. (2024), “Evolution of Heuristics: Towards Efficient Automatic Algorithm Design Using Large Language Model,” ICML/PMLR 235. https://proceedings.mlr.press/v235/liu24bs.html
2. van Stein & Bäck (2025), “LLaMEA: A Large Language Model Evolutionary Algorithm for Automatically Generating Metaheuristics,” IEEE TEVC 29(2), 331–345. https://arxiv.org/abs/2405.20132
3. Fernando et al. (2024), “Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution,” ICML/PMLR 235, 13481–13544. https://proceedings.mlr.press/v235/fernando24a.html
4. Agrawal et al. (2026), “GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning,” ICLR 2026. https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html

## Evidence limitation

The first three items have primary publication pages or paper records available in this pass. The direct Agent evolution, Hyperagents, Harmony Harness, LAOS and LLM4EO comparisons rely partly on existing repository audits; they must be revisited from original papers/code before any manuscript asserts an exhaustive novelty gap.
