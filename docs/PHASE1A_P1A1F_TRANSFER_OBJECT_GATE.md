# Phase-1A P1A-1F Transfer-Object Gate

- Branch: `phase1a-p1a1f-transfer-object-gate`
- Base: `9a6d5940e5cc620076900ad1a6a5d46c08846ad3`
- Scope: source audit + mechanism comparison + research decision only.
- No LLM API, no MetaBox performance run, no AES performance run.

---

## 1. Frozen negative result (do not re-litigate)

| fact | evidence |
|---|---|
| `deepseek-v4-pro` → `set_F=0.7` on A/B/C | P1A-1D preflight |
| `deepseek-flash` → `set_F=0.7` on A/B/C | P1A-1E preflight |
| API contract is not the blocker | 3/3 legal JSON, thinking disabled, json_object |
| No state-dependent action observed | single-variable tests, temp=0 |
| Formal 7-method experiment never started | gates failed |

**Status of LLM-direct DE parameter control:** `REJECTED_FOR_CURRENT_PROTOCOL`.
This does **not** generalize to all LLM controllers. Do not spend more turns
tuning prompts or swapping DeepSeek models for this protocol.

---

## 2. Code audit (actual implementation, not filenames)

### 2.1 Agent genotype (`src/agentfotagent/genome/schema.py`)

| gene | alleles | space |
|---|---|---|
| planning_mode | direct, plan_first | 2 |
| memory_policy | none, bounded_episodic | 2 |
| verification_policy | none, check_before_finalize | 2 |
| tool_selection_policy | fixed_ranking, state_conditioned | 2 |

Total **16** normalized genotypes. Intervention tests
(`tests/test_gene_interventions.py`, `tests/test_gene_semantics.py`) show each
gene changes runtime decisions (plan consumption, verify-gating submit,
recall-driven search, tool ranking). **Confirmed by code+tests.**

### 2.2 Fitness (AES)

- Success from **terminal environment state** via `StateBasedEvaluator.success_predicate`
  (tool_world locality, sealed hidden goal, self-report ignored). **Confirmed.**
- Budget fixed by task `max_steps`; not genome-controlled. **Confirmed.**
- Fail-closed on malformed state/goal. **Confirmed** (R3–R4 tests).

### 2.3 Search operators (AES / evolution package)

- `ConventionalEA`: (μ+λ) truncation; variation = **single-gene neighbor**;
  no crossover; tournament selection. **Confirmed from source.**
- `RandomSearch`: uniform over the 16-point space.
- `TransferEA` (pilot): allele-prior biased mutation — already judged
  NO_GO_OR_PIVOT on saturated AES tasks.

### 2.4 Source-domain control (MetaBox controlled DE)

Generation-level observable state (from `controlled_de.py`):
`improvement_rate, stagnation_steps, population_diversity, success_fraction,
budget_fraction, best, F, CR`.
Actions: `set_F`, `set_CR`, `noop` (mutation/restart fail-closed).
FE accounting independent. **Confirmed.**

### 2.5 Cross-domain comparability

| dimension | source (MetaBox DE) | target (AES genome EA) |
|---|---|---|
| search space | continuous ℝ^dim | 16 discrete genotypes |
| fitness | continuous regret | binary task success (+ optional steps) |
| control action | F/CR scalars | which gene to flip / which allele |
| state | stagnation, diversity, success frac | generation progress of a 16-point search |
| budget | FE 300 | genome proposals (≤16 unique) |

**Critical gap:** the AES search space has **16 points**. Any controller over
this space is a lookup table. A “transfer mechanism” that selects among 16
points cannot demonstrate nontrivial control unless the target space and/or
task difficulty grow. This is a structural fact of the current repo, not a
hypothesis.

### 2.6 Literature gap (from `LAOS_LMCOEA_MECHANISM_AUDIT`)

- **LAOS** (GECCO’25): LLM AOS with state + credit + dual replay. Overlaps
  generic “LLM picks operators from search state.”
- **LMCOEA/AwesomeDE**: LLM meta-design of constrained optimizers.
- **LLM4EO / EoH / LLaMEA**: LLM generates/edits algorithms.
- **Not shown anywhere (honest gap):** a *verified* mapping from **measured
  search-effect interventions** in continuous optimization onto **discrete
  genotype-search operators**, with shuffled-mapping negative control and
  family-level holdout — i.e. effect-identified transfer, not renamed operators.

---

## 3. Three transfer-object candidates

| criterion | A rules | B policy params | C effect representation |
|---|---|---|---|
| shared semantics S/T | weak (different spaces) | medium (normalized features) | **medium–strong** (effect labels) |
| nontrivial vs hand rewrite | **no** (rules are the rewrite) | weak (hyperparam transfer) | **yes if effects are identified** |
| distinguishable from LAOS | weak (state→action rules = AOS) | weak | **yes** (effect ID + mapping learnability) |
| distinguishable from LMCOEA | weak | weak | **yes** (transfer object ≠ algorithm generator) |
| identifiable on target | n/a | needs retraining | **needs intervention data** |
| shuffled-mapping control | meaningful | weak | **decisive** |
| current AES feasibility | feasible but trivial | feasible but ceiling | **blocked by 16-point space** |

### Candidate A — explicit state–action rules
Rules like “if stagnation≥k then increase diversity” **are** LAOS-class AOS.
Transferring them is renaming. **NOT SELECTED.**

### Candidate B — control policy parameters
π_θ over normalized z. Transfer = hyperparameter transfer. Distinguishing
transfer benefit from target-only tuning is exactly the hard part; with 16
points it is impossible. **NOT SELECTED.**

### Candidate C — search-effect control representation
z = φ(s), u = π_θ(z) ∈ {explore ↑, exploit ↑, diversity recover},  
a_S = g_S(u) (e.g. F/CR / restart),  
a_T = g_T(u) (e.g. which gene-neighborhood to mutate / allele prior).  

g_T must be **learned from target intervention data** (Δsuccess / Δsteps when
applying an operator family), not hand-written. Shuffled (effect→operator)
mapping is the negative control.

---

## 4. Priority candidate and mathematical definition (C)

**Source state** s_S = (improvement_rate, stagnation, diversity, success_frac, budget_frac)  
**Target state** s_T = (proposal progress, best success rate, genotype Hamming
spread, stagnant proposals, unique-genome ratio)  

**Shared representation** z = φ(s) = normalized vector in ℝ^5 (per-domain
feature maps into common semantics: progress, stall, spread, yield, budget).  

**Policy** u = π_θ(z) ∈ Δ{explore, exploit, recover} (simplex; deterministic
argmax or sample).  

**Source realization** g_S(u): explore→raise F / lower CR; exploit→lower F;
recover→restart-like diversity injection (where supported).  

**Target realization** g_T(u):  
- explore → mutate on more gene dimensions (or random-allele)  
- exploit → single-gene neighbor around best  
- recover → force least-used allele flip / shuffle one gene  

**Adaptation:** estimate effect matrix E_T[operator, effect] from a fixed
intervention budget on **train** tasks only; learn g_T as the assignment that
maximizes predicted effect under u.  

**Success criterion (measurable):**  
paired per-task-family success (or steps) of transfer controller >
target-only tuned controller AND > shuffled-map control, with FE/proposal
budget equality.  
**Failure criterion:** target-only matches transfer, or shuffled map ≡ transfer
→ hypothesis unsupported.

**Honesty clause:** if g_T is hand-assigned, this is **not** a transfer
contribution (explicitly ruled out).

---

## 5. Differentiation

| prior work | their claim | our residual claim if C succeeds |
|---|---|---|
| LAOS | LLM+state picks operators | effect-identified **cross-domain** map + shuffled control, not operator naming |
| LMCOEA/AwesomeDE | LLM designs optimizer | transfer **object** + intervention ID, not algorithm generation |
| LLM4EO/EoH/LLaMEA | LLM writes algorithms | no code generation; typed control object |
| own AES transfer pilot | allele prior | saturated; superseded by C **only if** space/difficulty grows |

**Core contribution candidate:** *intervention-identified effect representation*
(not “Agent”, not “EC”, not “bidirectional feedback”).

---

## 6. Falsifiable next-phase protocol (only if GO)

Source: MetaBox controlled DE, train F1–12 / val 13–18 / test 19–24 (split_v2).  
Target: AES — **only after** search space ≥ ~64 genotypes or hardened tasks
(no success ceiling). train/dev = key_crate+dial_set families; **held-out =
relay_route**, never used for mapping learning.

Arms (equal proposal budget, ≥10 seeds):  
1 transfer-C (learned g_T) · 2 target-only tuned · 3 vanilla EA · 4 random
controller · 5 shuffled effect→operator map · 6 hint-only/rule A as sanity.

Primary: task success rate (pairwise W-L-T per family). Secondary: steps,
invalid rate. Stop: no benefit vs (2) or shuffled ≈ transfer.

---

## 7. Risks and stop conditions

1. **16-point ceiling** — transfer unidentifiable. Must expand first.  
2. Effect matrix E_T not identifiable (interventions too noisy). Stop.  
3. Target-only matches transfer. Record NO_BENEFIT; do not retune to force win.  
4. Shuffled map matches transfer. Mapping artifact → reject mechanism.

---

## 8. GO / NO-GO

| item | decision |
|---|---|
| LLM-direct DE control (current protocol) | **REJECTED_FOR_CURRENT_PROTOCOL** (frozen) |
| Candidate A (rules) | **NO-GO** (LAOS overlap; rewrite) |
| Candidate B (params) | **NO-GO** (hyperparam transfer; ceiling) |
| Candidate C (effect representation) | **CONDITIONAL GO** |

**CONDITIONAL GO** requires, **before any transfer experiment**:

1. Expand AES genotype space and/or task difficulty so success is not at
   ceiling (structural precondition; measure first).  
2. Implement target intervention logging (which operator, which effect).  
3. Freeze split_v2 + AES family splits and the shuffled-map control.

If (1) cannot be met, the honest verdict is **`NO_GO_TRANSFER`** for the
current MetaBox↔AES pairing.

**Not a novelty claim.** No performance result is asserted in this document.
