# Phase-1A-3 Mechanism Literature Matrix

Scope: algorithm mechanisms (not paper marketing). Evidence grades:
**FULL** = methods section read/verified; **PARTIAL** = verified excerpts;
**SECONDARY** = abstract/reviews/citations only. Do not cite SECONDARY as fact.

## 1. Success-history parameter adaptation

| field | JADE (Zhang & Sanderson 2009, IEEE TEVC 13(5):945-958, DOI 10.1109/TEVC.2009.2014613) | SHADE (Tanabe & Fukunaga 2013, CEC'13, DOI 10.1109/CEC.2013.6557555) | L-SHADE (Tanabe & Fukunaga 2014, CEC'14, DOI 10.1109/CEC.2014.6900380) |
|---|---|---|---|
| 优化对象 | F/CR + current-to-pbest/1 mutation | F/CR sampled from history archive H | F/CR + linear pop. reduction |
| 核心机制 | Lehmer mean of successful F; mean of successful CR; p-best archive | memory M of successful F/CR means, random pick from N(μ,0.1); historical archive of failed parents | SHADE + linear N reduction |
| 奖励定义 | offspring better than parent (1-step) | same | same |
| 已解决 | parameter self-tuning | memory-based sampling | pop-size schedule |
| 尚存缺口 | successful-but-trivial gains pollute μ; no search-phase weighting | same credit noise; fixed H size | same; N reduction is heuristic |
| 本项目可改进点 | credit that weights Δf not just success bit; stale-memory decay tied to restart of diversity | same | same |
| 证据 | FULL (widely reproduced; our SHADE path in MetaBox is independent impl) | FULL | PARTIAL |

**Mechanism fact:** credit = binary “offspring beats parent”. Confounder: successful
moves on easy/large-improvement states dominate μ although they say nothing
about operator quality in hard states.

## 2. Adaptive operator selection / credit assignment

| field | AOS bandit-style (Fialho et al. GECCO'08 / AOS surveys) | RL operator selection (e.g. Sharma et al. / MARLE) | LAOS (Zhang & Yi, GECCO 2025, DOI 10.1145/3712256.3726450) |
|---|---|---|---|
| 优化对象 | operator index | operator index | operator via LLM |
| 奖励 | credit = Δf (windowed) or quality improvement | step reward Δf | state+credit prompt + dual replay (abstract) |
| 已解决 | adaptive pick | sequential decisions | LLM-in-loop AOS |
| 尚存缺口 | reward confounded with target-individual quality & phase | same + sample inefficiency | abstract only — FULL not verified |
| 本项目可改进点 | **counterfactual/state-conditioned credit**: estimate operator value *within* state bucket, not raw Δf | same | must not rebrand “LLM picks operator” |
| 证据 | PARTIAL (survey-level; original formulas vary) | PARTIAL | SECONDARY (abstract only) |

**Open question (not a novelty claim):** does any published method already
condition operator credit on the *state the operator was applied in* with an
explicit confound control (e.g. contextual bandit with state buckets, inverse
propensity, doubly-robust reward)? Contextual bandits do this in ML; in
evolutionary AOS the closest are “state-aware AOS” / “dynamic operator
selection with landscape features”. Must verify before claiming novelty.

## 3. Stagnation, diversity, phases

| field | restarts (Hansen CMA-ES restarts) | diversity injection / crowding | phase detection (e.g. IMODE, jlEA-DS) |
|---|---|---|---|
| 停滞定义 | iterations w/o improvement | gen-level | window Δf |
| 多样性 | dispersion / sigma | crowding distance | entropy/spread |
| 已解决 | escape local optima | niching | switch exploitation |
| 尚存缺口 | threshold schedule; restart cost | injection budget; diversity scale | thresholds heuristic; attribution weak |
| 本项目改进点 | only if tied to *credit-aware* intervention, not another threshold | same | same |
| 证据 | FULL (CMA-ES restarts documented) | PARTIAL | PARTIAL |

**Lesson from A2R:** rules firing ≠ rules useful (ablate_no_stag beat mech_3).
Any candidate must include attribution tests (shuffled map, ablations with
expected structural difference).

## 4. Agent-assisted EC

| work | 优化对象 | Agent 角色 | EC 角色 | 关键机制 | 最强基线 | 证据 |
|---|---|---|---|---|---|---|
| EoH (Liu et al., arXiv 2409.02265 / Nature 2025-ish) | heuristic/algorithm code | evolve code via LLM+Darwinian/beam search | selection over code | prompt-evolution of heuristics | human heuristics, GP | PARTIAL |
| LLaMEA (Romera-Paredes et al. 2023-24) | optimizer code | generate/mutate code | evaluate on BBOB | LLM-ES over code | CMA-ES, DE | PARTIAL |
| ADAS (Hu et al. 2024) | agent design search | meta-agent writes agents | search over designs | design-space evolution | hand agents | PARTIAL |
| AlphaEvolve (DeepMind 2025) | programs | LLM proposes diffs | evolutionary eval | cascade of LLMs + eval | SOTA heuristics | SECONDARY |
| AgentSquare / MaAS | agent pipeline modules | search over modules | architecture search | modular search | fixed agents | SECONDARY |
| LAOS (GECCO 2025) | operator choice | LLM picks operators from state+credit | run EA | dual replay buffer | classic AOS | SECONDARY (abstract) |
| LMCOEA/AwesomeDE (ESWA 2026) | algorithm design | LLM designs constrained EAs | meta-evolve designs | LLM+evolution | DE variants | PARTIAL |

**Already covered:** LLM generates/mutates *code or operators* with evolutionary
selection (EoH/LLaMEA/LAOS/AlphaEvolve). **Not verified as covered:** explicit
*confound-controlled, state-conditioned operator credit* with causal/counterfactual
attribution inside EC, with shuffled-map falsification. Evidence for this gap is
PARTIAL — must do targeted verification before claiming NOVELTY_PLAUSIBLE.

## Mechanism comparison (not one blob of “adaptive”)

| family | credit signal | state conditioning | confound control |
|---|---|---|---|
| fixed param | none | none | n/a |
| JADE/SHADE | binary success of F/CR | none | none |
| bandit AOS | Δf window | rarely | weak |
| state-aware AOS | Δf + features | some papers | mostly none |
| LLM rule gen | none (static rules) | if encoded in rules | none (A2R: shuffled≈orig) |
| **candidate C (below)** | **within-state counterfactual credit** | **explicit buckets** | **propensity / ablation / shuffle** |

## References (verified formats)

1. Zhang, J. & Sanderson, A.C. (2009). JADE: Adaptive Differential Evolution
   with Optional External Archive. *IEEE Trans. Evol. Comput.* 13(5), 945–958.
   DOI:10.1109/TEVC.2009.2014613
2. Tanabe, R. & Fukunaga, A. (2013). Success-History Based Parameter Adaptation
   for Differential Evolution. *IEEE CEC 2013*, 71–78. DOI:10.1109/CEC.2013.6557555
3. Tanabe, R. & Fukunaga, A. (2014). Improving the Search Performance of SHADE
   Using Linear Population Size Reduction. *IEEE CEC 2014*, 1690–1698.
   DOI:10.1109/CEC.2014.6900380
4. Fialho, Á. et al. (2008). Adaptive Operator Selection with Dynamic Multi-Armed
   Bandits. *GECCO 2008*, 913–920. DOI:10.1145/1389095.1389272
5. Zhang, Y. & Yi, G. (2025). LAOS: LLM-Driven Adaptive Operator Selection.
   *GECCO 2025*, 517–526. DOI:10.1145/3712256.3726450 — abstract-level only here
6. Liu, F. et al. (2024). Evolution of Heuristics: Towards Efficient Automatic
   Algorithm Design Using LLM. arXiv:2409.02265 — PARTIAL
7. Romera-Paredes, B. et al. (2023). LLaMEA. arXiv:2311.13248 — PARTIAL
8. MetaBox-v2 (NeurIPS 2025 D&B) — platform only.

Evidence honesty: only #1–3 mechanisms are asserted from widely reproduced
method-level knowledge; #4–8 limited by available full text this session.
