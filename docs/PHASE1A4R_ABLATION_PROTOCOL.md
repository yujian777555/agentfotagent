# Phase-1A-4R Ablation Protocol (frozen before corrected run)

- Code SHA at corrected run: `2eebcf7b40b1a6e81d15a527c1cbaeb53a0a8fe7`
- Train F1/F10/F20 × seeds 11,22,33 · 500 FE · NP=20 · minimize
- Factorial: M (memory reset) × N (population shrink) × I (immigrants)
- Controls: `state_M1N1I1` (frozen stall/div triggers + cooldown 5),
  `matched_random_timing` (FE-threshold schedule, count-matched, state-blind),
  external `official_meta_de`, `SHADE`
- Cooldown: 5 generations (state), 80 FE (matched)
- Judgment: component effects; timing (state vs matched); vs external baselines

**One corrected run only** after fixing the gen-index schedule bug (failed run
preserved as `results/phase1a4r/manifest_a4r-944575ce7344-…`).
