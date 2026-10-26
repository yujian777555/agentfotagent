# Literature Matrix — First-Pass Mechanism Comparison

本表用于研究决策，不是穷尽性系统综述。方法级描述来自论文正文/官方代码的范围因条目而异，见 [机制审查记录](FULLTEXT_AUDIT_2026-10-23.md)。

| Work | Object / core mechanism | Overlap | Implication |
|---|---|---|---|
| EoH | LLM co-evolves heuristic thought and executable code | High for LLM-guided EC design | Cannot claim first LLM-evolutionary heuristic design |
| LLaMEA / LLaMEA-HPO | LLM-generated algorithm classes, mutation/crossover, adaptive mutation, Pareto archive; separate HPO variant | High for algorithm evolution and structure/parameter separation | Need more than algorithm generation or generic HPO |
| LLM4EO | State-aware diagnosis and stagnation-triggered operator meta-evolution | Very high for online operator improvement | Generic H1 is not novel |
| LAOS | Official GECCO 2025 abstract: LLM meta-prompt includes progress, best fitness, population diversity and operator credit assignment; dual-layer replay separates offline fixed-strategy experience from online run experience. | Direct overlap with generic state-conditioned operator selection and history-guided adaptive control. | Official abstract verified; full text, exact credit/replay equations, ablations and official code not obtained. See [LAOS/LMCOEA audit](LAOS_LMCOEA_MECHANISM_AUDIT_2026-10-26.md). |
| AwesomeDE / LMCOEA | LLM meta-evolution generates executable constrained-EA update rules and evaluates them across numerical optimization problems; LMCOEA linked code generates DE-specific MATLAB offspring rules and selects strategy IDs using aggregated per-problem rewards. | Very high for meta-evolution, LLM-generated EA rules and cross-problem transfer in numerical optimization. The DE rule itself is not a domain-invariant Agent-genotype controller. | Publisher method text partly retrieved; linked LMCOEA repo statically inspected but not run. README claims MIT while no root LICENSE exists in observed tree; repository completeness/reproducibility unresolved. See [LAOS/LMCOEA audit](LAOS_LMCOEA_MECHANISM_AUDIT_2026-10-26.md). |
| EvoAgent / ARTEMIS | Evolutionary multi-agent generation; semantic mutation/crossover of Agent configurations | High for Agent evolution | Generic EA-over-Agent-genome is not novel |
| GEPA | Reflective prompt mutation, system-aware merge, Pareto candidate illumination | High for trajectory feedback and prompt evolution | Reflection/Pareto alone is not novel |
| DGM / HGM | Archive-based self-modification; lineage/clade productivity selection | High for RSI selection | Compare archive and lineage baselines |
| Hyperagents | Editable task/meta improvement procedure; cross-domain meta-level transfer | Very high for recursive improvement | Generic H3 not novel |
| AIDE² / MASS | Hidden-grade self-modification; evolutionary workflow search alternating with SFT | High for RSI and workflow improvement | Need mechanism-specific difference |
| Harmony Harness | Multi-objective compositional harness evolution; general/task-specific factorization and cross-benchmark transfer | Very high for transfer | Generic factorization/transfer is not novel |
| RSI-Router / CoCoEvolve | Historical skill/routing evolution; history retrieval, probing and verified mutation | High for feedback/history reuse | History/reflection/verification not novel alone |

## Candidate gap (unconfirmed)

A source-domain controller learned/selected on numerical MetaBox optimization is transferred as the same explicit control object into a structurally different Agent-genotype evolutionary search space. The contribution, if any, must be a nontrivial and reproducible mapping between state/action semantics, not the two-stage narrative or an adapter alone.

**Novelty risk: HIGH.** No code implementation or confirmatory experiment is authorized by this document.
