# Phase-1A-17 — State/Action Alignment Audit for MetaBox → AES Transfer

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Purpose: test whether the project can define a fixed transferable controller object before experiments.
- Result: **NO_GO_AS_CURRENTLY_SPECIFIED**. The table below is a feasibility analysis, not an implemented mapping.

## 1. Source and target are not the same optimization problem

### Source domain: MetaBox numerical optimization

- Search space: mostly real-valued decision vectors and numeric objective values.
- Typical operators: DE strategy, differential weight F, crossover rate CR, p-best selection, archive use, restart/immigrant operations and population management.
- Observable feedback: best/median objective improvement, stagnation, population dispersion, trial success, and operator credit.
- Evaluation semantics: an offspring is often considered successful when it beats its parent under the objective; this does not necessarily mean a useful Agent task-level improvement.

### Target domain: Agent Evolution Sandbox (AES)

- Search space: structured/categorical Agent genome and executable phenotype; the project-owned runtime is currently an engineering scaffold, not validated Agent-capability evidence.
- Possible operators: mutate one or more policy genes, change edit scope/strength, recombine modules, choose parent/survivor, inject a valid policy, preserve an elite, or restart a subpopulation.
- Observable feedback: goal-state task success, normalized score change, task-family generalization, tool/runtime errors, policy-genome diversity, and execution cost.
- Evaluation semantics: a syntactically valid or executable policy may still fail the task; a local score improvement may not generalize to unseen task families.

## 2. Proposed state abstraction — and why it is insufficient

| Abstract feature | MetaBox source feature | AES target feature | Mapping status | Risk |
|---|---|---|---|---|
| Relative progress | Normalized change in best/median objective over a fixed window | Normalized change in task-success score over a fixed window | Can be normalized to a common [0,1] progress scale, but outcome distributions differ | Numeric objective deltas and stochastic task success are not exchangeable without calibration. |
| Stagnation | Fraction of recent generations without best-so-far improvement | Fraction of recent generations without task-score improvement | Closest semantic match; fixed window can be shared | Target score noise and task-family mix can produce false stagnation. |
| Diversity | Normalized pairwise distance/dispersion of numeric vectors | Normalized mixed-genome distance or semantic/behavioral policy distance | Not naturally identical; requires a target-specific metric and normalization | Choosing a target metric is itself a consequential design decision; post-hoc calibration risks leakage. |
| Recent operator credit | Improvement attributable to a source low-level operator | Task-score change after a target policy edit operator | Scalar form can be aligned; causal attribution is not automatically aligned | Source objective gain and target Agent task gain have different variance, delay and interaction structure. |
| Candidate validity | Numeric bounds/constraint feasibility, if the benchmark has constraints | Genome schema validity, runtime executability, action-contract compliance | Not a shared signal by default | A source optimizer may have no analogue of target runtime validity; this feature must not be invented as if observed in source. |
| Evaluation progress | Fraction of fixed source evaluation budget spent | Fraction of fixed target episode/candidate budget spent | Can be normalized | Does not solve differing cost and reward semantics. |

A possible abstract state vector could be z = (relative_progress, stagnation, diversity_percentile, recent_operator_credit, normalized_evaluations_spent). But this is a generic search-state representation. The project has not shown that it is a novel representation, that the same calibration works in both domains, or that it improves transfer.

## 3. Proposed action abstraction — and why it collapses to a hyper-heuristic

| Abstract action | Possible MetaBox realization | Possible AES realization | Problem |
|---|---|---|---|
| Intensify / exploit | Lower perturbation strength; use current-to-pbest or local strategy | Small/local mutation of selected genes or module | The domain-specific low-level realization differs; this is generic exploit/explore abstraction. |
| Diversify / explore | More disruptive DE strategy, broader perturbation, alternate strategy | Larger semantic edit, different gene set, module recombination or new policy injection | Multiple target operators could implement the same label; mapping is not unique. |
| Preserve elites | Keep top solutions or maintain an archive | Preserve top verified Agent policies / archive | Broadly shared EA behavior, not a novel transfer mechanism. |
| Restart / inject immigrants | Reinitialize part of numeric population | Inject random valid structured policies or reset a subpopulation | Similar intent but different sampling distributions and validity filters. |
| Switch low-level operator | Choose DE strategy and F/CR configuration | Choose target mutation/recombination family and edit scope | Operator labels and effects do not correspond. |
| Stop / continue | End source search or continue iterations | End policy search or spend more evaluations | Budget-control semantics can be matched, but finite-budget allocation is explicitly not the project's core contribution. |

If the transferred controller outputs only the five abstract actions, it is a generic hyper-heuristic/AOS policy. If it outputs DE-specific operators/parameters, it is not directly executable in AES. If a bespoke adapter reinterprets every source action after observing target results, the method is no longer a frozen transfer.

## 4. Transferability gate

A valid H2 claim would need the following tuple fixed before any target test:
- source features S_src and target features S_tgt;
- shared abstract state Z and both fixed maps phi_src, phi_tgt;
- source action set A_src and target action set A_tgt;
- fixed action maps psi_src and psi_tgt;
- controller architecture and source training objective;
- source training tasks, target development tasks and untouched target test families;
- a rule for detecting and suppressing negative transfer without using test outcomes.

No tuple is currently available. A hypothetical tuple can be designed, but doing so would be a new research design, not a transfer of an already validated controller.

## 5. A source controller is a prerequisite — currently missing

Phase-1A-14's candidate shortlist records zero surviving method candidates. Phase-1A-10's candidate review records zero blind-review PASS candidates and no Stage-D performance experiments. Therefore there is no source controller with a defensible mechanism and verified performance that can be frozen and transferred.

This is a separate blocker from state/action alignment. Even if a mapping were devised, there is no approved source object to transfer.

## 6. Required controls if H2 is ever reopened

No experiments are authorized now. If the project later reopens H2, pre-register:
1. Target-only standard EA/GP/random valid-policy search.
2. Target-only strong AOS/hyper-heuristic.
3. Random abstract controller.
4. Source-trained frozen controller with fixed state/action maps.
5. The same controller with shuffled state-feature mapping.
6. The same controller with shuffled action mapping.
7. Equal-budget target-trained controller.
8. Frozen source controller with no target adaptation.
9. Ablations for each abstract state feature and each abstract action.
10. Task-family held-out evaluation and negative-transfer analysis.

The primary endpoint must be target Agent task success/generalization, not controller accuracy, source-domain score, validity rate, or code executability.

## 7. Alignment decision

**NO_GO_AS_CURRENTLY_SPECIFIED.** The generic progress/stagnation/diversity abstraction is feasible to implement, but is not itself novel. The concrete source/target action mapping is lossy and many-to-many. A source controller that passed the novelty gate does not currently exist. H2 should remain paused unless a new, independently reviewed transfer mechanism resolves all three issues before any experiment.
