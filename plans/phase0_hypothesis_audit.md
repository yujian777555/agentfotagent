# P0-R1 — H1/H2/H3 Operationalization and Smallest Discriminative Experiment

**Status:** DRAFT / zero-API planning only. No implementation or live model experiment is authorized by this document.  
**Repository baseline for this audit:** `agentfotagent` governance HEAD `e36c79edf31712ff68c7569354a682f5f7f56da8`.  
**Research constraint:** The evolutionary-computation mechanism must be central; MetaBox is infrastructure; do not make finite-budget allocation the main claim.

## 1. Research question and order

The research question is not “can an LLM be combined with an EA?” EoH, LLaMEA, LLM4EO, LAOS and LMCOEA already make broad claims in that territory.

The discriminative question is:

> Can an Agent help discover a state-conditioned evolutionary control policy on MetaBox-v2, and can the **same abstract control policy**, after a declared domain adapter, improve Agent RSI on independent tasks beyond strong static/adaptive baselines?

Sequence:
1. **H1 source-domain gate:** show that an Agent-proposed controller helps on held-out MetaBox problems against a statically tuned controller and relevant adaptive/LLM-based baselines.
2. **H2 transfer gate:** freeze the controller and test it on independent Agent-RSI tasks. Do not update it using target test results.
3. **H3 feedback gate:** only if H2 passes, test whether Agent evolution feedback adds value over one-way transfer.

H1 alone is not enough for a novelty claim because online LLM operator design is already studied. H2 is the core cross-domain hypothesis; H3 is optional.

## 2. Shared control interface (candidate, not an approved method)

Represent the policy as (pi(z_t) ightarrow a_t), where the state is computed only from observations available at time (t).

### Candidate state features

- normalized progress slope over a fixed recent window;
- stagnation length / no-improvement ratio;
- population or candidate-genome diversity/novelty;
- recent intervention/operator success and regression rates;
- uncertainty / disagreement when available.

Normalize and document every feature. Avoid using the absolute score scale as the only signal, because MetaBox fitness and Agent task success have different semantics.

### Candidate abstract actions

- `EXPLORE`: use a broader variation or new search mode;
- `EXPLOIT`: perform a smaller/local improvement;
- `DIVERSIFY`: switch parent/lineage/operator or restore diversity;
- `REPAIR`: target a weak component based on an observable failure trace;
- `ROLLBACK/RESTART`: return to a validated parent or restart a bounded part of the search.

These labels are not claimed to be novel. The experiment must test whether the **timing/selection rule** learned on MetaBox adds value beyond fixed rules and target-domain tuning.

### Domain adapters

| Abstract action | MetaBox numerical-optimization adapter | Agent-RSI adapter |
|---|---|---|
| EXPLORE | Select a broader search operator or higher exploration setting within a frozen optimizer's legal action set | Broader redesign or a new candidate branch |
| EXPLOIT | Select a local/refinement operator or lower-intensity step | Local edit to the current candidate's existing component |
| DIVERSIFY | Change operator/parent or perform a bounded diversity-restoring move | Select another parent/lineage or an alternative strategy |
| REPAIR | Adjust the identified underperforming control/operator component | Edit a failure-associated prompt/workflow/tool-policy component |
| ROLLBACK/RESTART | Restore a prior optimizer state or bounded restart, if the chosen MetaBox adapter supports it | Revert to a validated parent/checkpoint or restart a bounded branch |

A runtime policy must not receive hidden benchmark labels or future rewards. A separate oracle-label analysis may be reported only as an upper bound.

## 3. H1 — Agent-assisted evolutionary-control discovery

### Operational definition

Freeze one base optimizer and its legal action interface. Let the Agent inspect training trajectories and propose a structured policy/rule set that maps the state features above to abstract actions. Parse/validate the output; invalid proposals fail closed. Evaluate policies on the same train/validation cases and a disjoint test set.

### Required baselines

1. Frozen default/base optimizer.
2. Strong classical adaptive optimizer/parameter-control baseline (select after inspecting the chosen MetaBox problem and optimizer; e.g. a relevant DE/SHADE-family baseline if DE is used).
3. Best static configuration selected by random search or SMAC on train/validation.
4. A simple hand-coded state rule (stagnation/diversity threshold) with the same action interface.
5. Classical adaptive operator selection (AOS), where relevant.
6. An LLM4EO-style online operator-design baseline or a carefully labeled adapted baseline if exact reproduction is infeasible.
7. Offline LLM algorithm/heuristic generation baseline (EoH/LLaMEA) if its optimization object is comparable.

### Metrics

- primary: normalized area under the convergence curve / normalized final error, with direction and normalization fixed before confirmation;
- secondary: target-attainment rate, held-out function/problem-family performance, generalization gap, robustness across seeds, valid-action rate, and intervention success;
- cost is recorded as a fairness constraint and secondary measure, not the central scientific objective.

### Split and stopping rule

Use a train/validation/test split by underlying problem identity/family, not merely random rollout rows. The final test is untouched during rule search, prompt edits and HPO.

H1 fails if the Agent-proposed controller does not beat the strongest statically tuned/classical baseline on held-out tasks, if the effect is limited to training functions, or if its gain disappears under matched evaluation budgets. If LLM4EO-style online operator evolution explains the result, narrow the claim to transfer rather than claiming a new generic operator-evolution method.

## 4. H2 — Transfer to Agent RSI

### Operational definition

After H1 is confirmed, freeze the MetaBox-derived abstract policy. Map only its abstract action decisions through the declared Agent-RSI adapter; do not re-fit its decision rule on Agent test outcomes.

The target adapter may use an existing Agent-genome evolution implementation as a software substrate after code review. `EvoPareto-Agent` is currently a candidate substrate, but its latest report has real HTTP = 0; it is not yet a real-LLM evidence source. No NSGA-III rewrite is needed for this audit.

### Required baselines

1. Fixed/default Agent evolution controller.
2. Generic hand-coded explore/exploit/repair policy.
3. Statically tuned target-domain controller, tuned only on target train/validation tasks.
4. MetaBox-derived transferred controller.
5. Shuffled/random transfer policy as a negative control.
6. Directly target-trained controller as an optional upper bound, only if budget permits and it is clearly distinguished from transfer.

### Metrics

- primary: held-out Agent task score/success after a fixed number of candidate evaluations;
- secondary: parent-child paired improvement, effective edit rate, regression rate, held-out/OOD gap, diversity/unique valid candidates, and API/token/latency costs;
- use the same base model, initial genome, task split, number of evaluated candidates and acceptance rule across arms.

H2 fails if transfer does not beat both the no-transfer baseline and the generic hand-coded controller on held-out tasks, or if a shuffled/random policy performs similarly. If target-domain tuning is stronger, report that the cross-domain transfer hypothesis was not supported.

## 5. H3 — Does Agent feedback add value beyond one-way transfer?

Only start after H2 passes.

Compare:
- **one-way:** frozen MetaBox-derived policy controls Agent RSI;
- **feedback:** structured, post-run Agent outcomes update the policy for future tasks;
- **shuffled feedback:** same feedback volume but task/action labels are shuffled;
- **no-feedback placebo:** feedback is collected but does not change the policy.

Use sequentially separated task batches. Feedback and updates may use the development stream only; a final hidden task set is evaluated once after the policy is frozen.

H3 fails if feedback does not improve future held-out Agent tasks beyond one-way transfer, or if shuffled feedback gives comparable gains.

## 6. Parameter tuning — separate the four parameter classes

| Parameter class | Examples | Treatment |
|---|---|---|
| **Base optimizer parameters** | DE population size, (F), (CR), strategy/operator settings | Freeze the base optimizer for the first controller test. If needed, tune a baseline on train/validation before comparing controllers. Do not tune the base algorithm and the controller simultaneously. |
| **Controller-rule parameters** | Stagnation window, diversity threshold, action persistence/hysteresis, success-rate smoothing | Declare in the policy grammar. Tune only on train/validation, or evolve them as genes; do not silently do both. |
| **EA meta-parameters** | Population/offspring count, parent/survivor selection, mutation scope, crossover/variation mixture | Use a small screening design, then random search/SMAC for a strong static baseline. Freeze before confirmatory test. |
| **LLM generation parameters** | Model/version, temperature, prompt version, number of proposals, retries | Freeze in each comparison. If tuned, treat that as a separate factor and account for all proposal/evaluation calls. |

### Staged tuning procedure

1. **Freeze the genotype and action interface.** Do not alter state features, action set, base optimizer and scoring function at once.
2. **Pilot sensitivity screen.** On train/dev problems, vary only a small number of influential settings; use a fractional-factorial or one-factor-at-a-time screen to find plausible ranges.
3. **Static HPO baseline.** Use random search or SMAC on train/validation. This is the minimum fair baseline; beating a default setting is not enough.
4. **Control comparison.** Compare the best frozen setting against a deterministic schedule, classical AOS (e.g. probability matching/adaptive pursuit or a bandit controller), and any self-adaptive setting that fits the action representation.
5. **Confirmatory run.** Freeze all settings and run independent seeds on held-out problems. A zero-API synthetic test may use at least 20 independent seeds to validate the statistical pipeline, but such synthetic results do not establish real Agent efficacy.
6. **Report full curves and all failures.** Report per-problem/per-seed outcomes and confidence intervals, not only the best run.

The control method should be accepted only if it adds capability beyond the best static configuration under matched task/rollout budgets. “Adaptive tuning is better than defaults” is not a sufficient claim.

## 7. Zero-API work allowed at this stage

- inspect MetaBox-v2 code/config interfaces and lock the candidate version;
- audit prior repositories read-only and create provenance records;
- define the policy schema, state/action mappings, metrics and train/validation/test split;
- build synthetic data only to test analysis code and known-effect/null-effect behavior;
- design unit tests for parsing, invalid action rejection, deterministic mapping and leakage guards.

Not authorized at this stage:
- live LLM API calls;
- claims of actual Agent improvement based on synthetic runs;
- new NSGA-III implementation;
- large MetaBox runs before the base problem/adapter and metric contract are frozen;
- using hidden-test feedback to tune the controller.

## 8. Exit gate for P0-R1

Proceed to a small MetaBox CPU feasibility run only when:
1. prior-art overlap for LLM4EO/LAOS/LMCOEA has been reviewed sufficiently to state the intended difference;
2. the base optimizer and action interface are fixed;
3. the parameter classes and static-HPO baseline are specified;
4. train/validation/test splits are disjoint and versioned;
5. the smallest experiment can distinguish transfer from generic adaptation;
6. the user explicitly approves the execution scope and any model/API budget before any real LLM call.

No new algorithm is approved by this plan.
