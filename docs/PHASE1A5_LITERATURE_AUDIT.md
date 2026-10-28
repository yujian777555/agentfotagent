# Phase-1A-5 Literature Audit

Closed lines (do not reopen): CC-SOC/quality-credit; DPR-SHADE state triggers;
N+I restart on L-SHADE; stagnation/memory-reset/restart family.

## Selection/DE mechanism papers

### UDE — Is Selection All You Need in Differential Evolution? (2026)
**Evidence: SECONDARY** (title/topic from brief). Core idea: selection
mechanism itself carries more weight than mutation variants. Implies DE
defects may live in *selection/replacement* rather than F/CR. Nearest to a
possible "selection pressure" patch. **CANNOT claim selection改进 as novel
without full-text.**

### BDVS — Best Discarded Vector Selection (2022)
**Evidence: SECONDARY.** Uses discarded (failed) trial vectors instead of
dropping them. **ALREADY_COVERED** as "save/use failed candidates" — explicitly
listed as non-novel in this brief.

### ATBDE — failure-memory adaptive DE
**Evidence: SECONDARY.** Failure memory drives adaptation. **ALREADY_COVERED**
(failure history ≠ new).

### AR-aDE — archive-reuse adaptive DE (2024)
**Evidence: SECONDARY.** External archive reuse. **ALREADY_COVERED**
(archive ≠ new).

### EoH / LaMEA / AlphaEvolve
**PARTIAL/SECONDARY** as before: LLM generates code; evolution selects.
**ALREADY_COVERED** for "LLM writes mutation strategies" and "EA searches
LLM code".

### LMCOEA / LLM MetaBBO surveys (2026)
**SECONDARY.** LLM-designed EAs are crowded space.

## Mechanism gap candidates that survive the "not-renaming" filter

| candidate | gap | nearest | risk |
|---|---|---|---|
| selection-side: replace worst-first with probability weighted by *relative* rank within generation (not absolute fitness) | UDE hints selection matters; rank-normalized pressure is testable | UDE (needs full-text), tournament | MED |
| success-history: cap the influence of outlier-large improvements on M_F (robust Lehmer mean / trimmed) | JADE/SHADE Lehmer mean sensitive to rare huge Δf | robust stats in CMA | LOW-MED |
| archive: only store *diverse* discarded vectors (min-distance filter) | BDVS stores all discards | BDVS | MED |

**Most defensible for a minimal patch:** robust success-history update
(trim/winsorize Δf weights entering M_F/M_CR) — precise math, small diff,
directly testable against L-SHADE, not a restart/trigger story.

## Evidence honesty

Full method text not obtained for UDE/BDVS/ATBDE/AR-aDE this session. Claims
of novelty are therefore **UNRESOLVED**; the pilot is hypothesis-testing only.
