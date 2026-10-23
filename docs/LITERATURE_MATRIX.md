# Literature Matrix — First-Pass Mechanism Comparison

本表用于研究决策，不是穷尽性系统综述。方法级描述来自论文正文/官方代码的范围因条目而异，见 [机制审查记录](FULLTEXT_AUDIT_2026-10-23.md)。

| Work | Object / core mechanism | Overlap | Implication |
|---|---|---|---|
| EoH | LLM co-evolves heuristic thought and executable code | High for LLM-guided EC design | Cannot claim first LLM-evolutionary heuristic design |
| LLaMEA / LLaMEA-HPO | LLM-generated algorithm classes, mutation/crossover, adaptive mutation, Pareto archive; separate HPO variant | High for algorithm evolution and structure/parameter separation | Need more than algorithm generation or generic HPO |
| LLM4EO | State-aware diagnosis and stagnation-triggered operator meta-evolution | Very high for online operator improvement | Generic H1 is not novel |
| LAOS | LLM state-conditioned adaptive operator selection | High | Full-text/code audit still required |
| AwesomeDE / LMCOEA | MetaBBO-trained LLM meta-optimizer generating EA update rules; cross-problem transfer | Very high | MetaBox + LLM rule generation / cross-problem transfer insufficient |
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
