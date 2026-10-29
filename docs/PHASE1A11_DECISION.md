# Phase-1A-11 Decision

- Date: 2026-10-29
- Branch: `phase1a-phase11-unified-agent-ec-roadmap`
- Audited code baseline: `3c3c6293aefa4861047b56d2c4d1057feb6a9b7c`
- Scope: read-only candidate, literature, source and configuration audit; no experiments.

## Overall decision

**CONTINUE THE PROJECT; DO NOT CONTINUE THE CURRENT CANDIDATE BATCH OR RUN SCIENTIFIC AES EXPERIMENTS YET.**

The project target remains: **LLM-empowered evolutionary computation applied to improving Agent**. The Phase-1A-10 failure is not a project-level NO-GO. It is evidence that the current free-form candidate generation process did not produce a mechanism that passed novelty review. The target application is fixed; the claimed benefit remains empirical.

## Separate gate decisions

| Track / gate | Decision | Evidence | What it means |
|---|---|---|---|
| Track A: Phase-1A-10 four candidates | **`NO_GO_CURRENT_CANDIDATES`** | See `PHASE1A11_CANDIDATE_AUDIT.md` and `PHASE1A11_LITERATURE_MATRIX.md`. Boundary repair/resampling/reflection are established; F-floor/diversity reset overlaps existing parameter-control and diversity/restart work. | Do not implement or run these candidates as new algorithms. Do not spend another API batch regenerating the same ideas. |
| Track B: AES engineering scaffold | **`ACCEPTED_FOR_ENGINEERING_ONLY`** | Phase-0-R4 independent review and current versioned source. | Existing evaluator, tool world, provenance and baseline harness can support engineering work. This is not Agent capability evidence. |
| Track B: scientific AES experiment readiness | **`AES_BLOCKED_REPAIR_REQUIRED`** | Only 16 genomes; historical mock pilot saturated at 100% success; current EA selection uses success rate only; no real LLM Agent backend in the audited runtime; only three held-out tasks. | Redesign search space, task discrimination, fitness tie-breaking and backend before scientific runs. |
| H2: transfer from MetaBox to AES | **`NOT_READY`** | No source-domain controller has passed Track A; no explicit controller object with aligned source/target semantics is validated. | Do not treat cross-domain transfer as established or begin H3. |
| H3: bidirectional feedback | **`NOT_STARTED`** | H2 is unproven. | Remains conditional and should not be implemented now. |

## Key findings that change the plan

### 1. Track A is a candidate-generation failure, not a universal impossibility result

The four remaining candidates are not four independent mechanisms. Three belong to the same boundary-repair family; one combines a non-dimension-specific F floor with diversity-triggered memory reset. The relevant prior-art sources include:
- Boks et al. 2021, [10.1145/3449726.3463214](https://doi.org/10.1145/3449726.3463214): resampling, random reinitialization, reflection and other BCHMs.
- Biedrzycki et al. 2019, [10.1016/j.swevo.2018.10.004](https://doi.org/10.1016/j.swevo.2018.10.004): 17 BCHMs across seven DE variants.
- Tanabe & Fukunaga 2020, [10.1109/TCYB.2019.2892735](https://doi.org/10.1109/TCYB.2019.2892735): 24 F/CR parameter-control methods.
- Deng et al. 2020, [10.1016/j.knosys.2020.106388](https://doi.org/10.1016/j.knosys.2020.106388), and Lin & Meng 2024, [10.1016/j.eswa.2024.123634](https://doi.org/10.1016/j.eswa.2024.123634): dimension-level/stagnation/diversity-triggered intervention and restart mechanisms.

The targeted audit does not prove every exact combination was previously published. It does establish that no candidate currently has a sufficiently distinct, coherent and evidence-ready mechanism claim.

### 2. The target application cannot be tested meaningfully on the current saturated mock setup

The current genotype is a Cartesian product of four binary genes, giving 16 configurations. The historical mock pilot reports all 16 genotypes solving all six train tasks. The mock backend is a scripted policy with hand-written family-specific plans. The conventional EA ranks candidates only by success rate, so the pilot's 1.0 ties cannot guide selection even though steps vary.

Therefore, increasing seeds or the evaluation budget on the same task set is not the next step. The task distribution, genotype, objective and real backend must become discriminative first.

## Important clarification: Agent improvement is the target; transfer is optional

The project's application objective is **not negotiable**: the eventual method must be evaluated on improving Agent performance. However, **MetaBox-to-AES transfer is only one possible bridge**, not a result and not a requirement to preserve if it proves unproductive.

The next design phase must compare two routes without presuming either works:
1. **Transfer route:** first validate a specific LLM-assisted EC controller on MetaBox, then map the same explicit controller object into AES with target-only and shuffled-mapping controls.
2. **Direct target route:** use LLM-assisted EC directly to evolve executable Agent policies/genotypes in AES, comparing against fixed Agent, exhaustive search where feasible, random search, conventional EA and LLM-only refinement.

The direct route is not automatically novel: it must be audited against existing LLM-assisted EA, prompt/workflow evolution, and Agent self-improvement methods. The transfer route is not automatically novel either. The decision between them requires a mechanism-level literature audit and a fair experiment design; do not force H2 simply because it appears in the older charter.

## Next phase — design only, no scientific run

Create a Phase-1A-12 design proposal with these deliverables:
1. A richer but semantically grounded AES genotype specification. Every gene/allele must have an observable runtime effect and an intervention test. Avoid decorative genes.
2. A task-difficulty plan that removes 100% success saturation on train/dev without touching held-out tasks. Use varied information requirements, distractors, action dependencies and recovery after wrong actions; keep the terminal-state evaluator authoritative.
3. A predeclared fitness contract: verified success remains primary; specify a deterministic tie-breaker or multiobjective treatment for steps, invalid actions and other measured costs. Do not choose metrics after observing which favors EA.
4. A baseline plan that includes exhaustive enumeration for the current 16-genome space, and—after the search space is redesigned—fixed Agent, random unique-genome search, conventional EA and a strong LLM-only/self-refinement comparator under the same evaluation conditions.
5. A source-to-target comparison of transfer vs direct target optimization, with nearest prior work, expected mechanism, falsification conditions and stopping rules.
6. A real backend integration plan for `deepseek-flash` only, including version/decoding, API/token caps, cache semantics and error accounting. Do not call the API until a separate budget is approved.

### Hard limits retained

- 0 real LLM API requests in this phase.
- 0 MetaBox performance experiments.
- 0 AES scientific performance experiments.
- 0 GPU hours.
- No held-out/test result access.
- No reopening previously falsified algorithm claims without a new independently audited hypothesis.

## Final state

- Track A current candidates: **closed**.
- Track B engineering scaffold: **available, engineering only**.
- Track B scientific experiment: **blocked pending redesign**.
- Cross-domain transfer: **hypothesis only**.
- Overall project: **continue with AES/Agent-targeted method redesign**, not project-wide NO-GO.
