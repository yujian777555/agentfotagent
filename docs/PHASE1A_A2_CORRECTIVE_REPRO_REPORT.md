# Phase-1A-2R Corrective Reproduction Report

- Branch: `phase1a-a2-corrective-repro`
- Code SHA: `a0f435e328d1ac2ee7cb9b16ca37b3e993f00616`
- Run ID: `a2r-a0f435e328d1-clean-20261028T122041`
- Manifest: `results/agent_assisted_ec_corrective/manifest_a2r-a0f435e328d1-clean-20261028T122041.json`
- Frozen manifest: `results/agent_assisted_ec/manifest_a2-1fc4033…` (git SHA `3b6fb101…` recorded)
- Frozen mechanism: `agent_mech_3` (hash `8008f05085bd11f2…`), **not regenerated**, no LLM calls

## 1. Implementation defects vs reporting gaps

| item | type | fix |
|---|---|---|
| rand/2/bin non-standard | **implementation bug** | v=x_r1+F(r2−r3)+F(r4−r5), 5 distinct ≠ i; raises if insufficient |
| Fixed DE CR inconsistent with annotation | **implementation bug** | base F=0.5 CR=0.9 explicit in protocol |
| Deterministic baseline unreachable rule | **implementation bug** | single reachable rule: stag≥5→rand/2 else rand/1 |
| Ablation/shuffled built from mech_1 | **implementation bug** | rebuilt from frozen mech_3 |
| Random-mech threshold scale mismatch | **implementation bug** | frozen scales from train state ranges |
| Missing full action traces | **reporting gap** | per-run JSON traces + SHA-256 (1560 traces) |
| Diversity inject without FE guard | **implementation bug** | FE-safe partial/skip + reject reasons |
| Validation script unbound to manifest | **implementation bug** | explicit frozen path required (train repro binds it) |

Original P1A-2 numbers remain historical; they are **not** comparable to this run.

## 2. Protocol (frozen before comparison)

12 train funcs `[1,2,4,6,7,10,11,12,15,18,20,21]` × seeds `[11,22,33,44,55]`
× 300 FE, NP=20, dim=10, base F=0.5 CR=0.9. 25 controlled arms + official DE +
SHADE. **1680/1680 runs OK, FE exact (300=300).**

## 3. Corrected results (median metric, lower better)

| arm | median |
|---|---:|
| **fixed_classic** | **23415** |
| random best-of-20 | 15922 |
| random median-of-20 | 32326 |
| ablate_no_stag | 30622 |
| official_meta_de | 41914 |
| **agent_mech_3** | **53083** |
| deterministic | 53489 |
| ablate_no_div / shuffled_map | 53083–53489 |
| SHADE | (see manifest) |

**agent_mech_3 paired W-L-T (60 pairs):**

| opponent | W-L-T |
|---|---|
| fixed_classic | **17-38-5** (loses) |
| deterministic | 1-4-55 (mostly tie) |
| official_meta_de | 29-26-5 |
| SHADE | 37-18-5 |
| shuffled_map | **0-0-60** (identical metrics) |
| ablate_no_stag | 19-36-5 (ablation better) |
| vs 20 random mechs | mean W 21.1 / mean L 33.9; wins only 7/20 |

Per-function: mech_3 loses or ties deterministic on all 12; loses best-random 11/12.

## 4. Mechanism attribution (frozen mech_3)

- Operators used: rand/1 2600, **rand/2 14180** (stagnation rule fires heavily).
- **inject_diversity: 5 events, 20 individuals resampled** — div≤30 almost never
  true (train diversity ≈20–60). The diversity rule is effectively dead.
- first-match: stag rule (index 0) shadows div rule whenever both hold.
- shuffled_map equals mech_3 metrics on all 60 pairs → with 2 rules and the
  observed trigger pattern, the state→action shuffle is behaviorally inert
  here; this does **not** support state-dependent mechanism credit.

## 5. Decision

**`NO_BENEFIT` — stop current mechanism hypothesis. Do not run untouched
confirmation functions [3,8,23]. Do not proceed to Phase-1B.**

After correcting bugs that inflated the original claim:
1. frozen agent_mech_3 is **worse** than fixed classic DE (17-38-5);
2. no advantage over a one-rule deterministic baseline (1-4-55);
3. loses the random-mechanism distribution (7/20);
4. ablation *removing* stagnation is better — the headline rule hurts;
5. inject_diversity never meaningfully fires.

The earlier train “wins” were implementation artifacts (wrong rand/2, CR
mismatch, weak deterministic baseline, misbuilt controls).

## 6. Integrity

- FE exact; 1560 traces with SHA-256; run IDs unique; clean worktree at run.
- No LLM; no test split `[5,9,14,17,19,24]` access; no Phase-1B.
- Historical P1A-1B..E and P1A-2 artifacts preserved unchanged.
