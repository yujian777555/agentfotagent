# Phase-1A P1A-1 Pilot Report

- Run ID: `p1a1-319b3582baad-clean-20261027T182625`
- Code SHA at run: `319b3582baad11ad7c6ed4c3e5134508a29c737b`
- Manifest: `results/p1a1_pilot/manifest_p1a1-319b3582baad-clean-20261027T182625.json`
- Traces: `results/p1a1_pilot/traces/p1a1-319b3582baad-clean-20261027T182625/`
- Analysis: `results/p1a1_pilot/analysis_p1a1-319b3582baad-clean-20261027T182625.json`

## Setup

3 train functions (F1/F10/F20), seeds 11/22, 300 FE, NP=20, minimize.
6 methods × 3 × 2 = **36 runs, 0 failures**. FE exact on all controlled runs.

## LLM execution

- Model: `deepseek-v4-pro` via DeepSeek API (real calls).
- Requests 85, retries 6, prompt tokens 11892, completion tokens 7581,
  cache hits 5, invalid responses 3 (fallback noop), API failures 0.
- Budget: 85 ≤ 100 requests. Cost not returned by API; token counts authoritative.
- **Valid actions: 81/84.** F/CR actually change across generations.
- **Hint-deviation rate: 0/84** — model echoed the state-derived hint every time.

## Results (lower metric better)

| func | seed | official | classic | explore | stag | random | **llm** |
|---|---|---:|---:|---:|---:|---:|---:|
| F1 | 11 | 6066 | 5852 | 10301 | 9550 | 2312 | **3951** |
| F1 | 22 | 8666 | 7063 | 12894 | 5344 | 5924 | **8376** |
| F10 | 11 | 8.36e7 | 4.76e7 | 8.51e7 | 5.29e7 | 5.23e7 | **4.77e7** |
| F10 | 22 | 5.75e7 | 9.57e7 | 1.16e8 | 6.30e7 | 3.75e7 | **1.18e8** |
| F20 | 11 | 4.64e5 | 8.40e5 | 1.29e6 | 6.43e5 | 5.76e5 | **6.33e5** |
| F20 | 22 | 3.04e5 | 1.53e6 | 2.36e6 | 1.73e6 | 1.82e5 | **2.00e6** |

Medians: random 3.79e5 · official 3.84e5 · llm 1.32e6 · classic 1.18e6 · stag 1.19e6 · explore 1.83e6

### llm_agent paired W-L-T

| opponent | W | L | T |
|---|---:|---:|---:|
| fixed_classic_de | 2 | 4 | 0 |
| fixed_explore_de | 5 | 1 | 0 |
| official_meta_de | 3 | 3 | 0 |
| random_valid_controller | 1 | 5 | 0 |
| stagnation_heuristic | 3 | 3 | 0 |

## Decision on H1 (pilot)

**NO_BENEFIT vs strong baselines.** The LLM agent does not beat
`random_valid_controller` or `official_meta_de` (L=5 and L=3 respectively);
median is worse than both. It beats `fixed_explore_de` but that is the weakest
controlled setting.

### Positive evidence

- Real API loop works; 81/84 valid DSL actions; F/CR change over time
  (e.g. F: 0.7→0.5→0.8…, CR: 0.5→0.3).
- Full traces + FE accounting + seed reproducibility of non-LLM arms.
- No budget breach (85/100 requests).

### Negative evidence

- 0/84 hint deviations: under prompt v5 the model echoes the scaffolding hint.
  The pilot therefore does **not** isolate LLM judgment from the hint heuristic.
- Mixed per-function results; worse than random control on 5/6 pairs.
- Early runs (documented) failed from reasoning-token empty content — fixed,
  but shows prompt brittleness of the service.

## Limitations

- n=3 functions × 2 seeds; exploratory only. No statistical claim.
- Hint-scaffolded generation confounds LLM vs heuristic. A follow-up must use a
  prompt that elicits independent choices (or report hint-only as the control).
- Official DE vs controlled DE implementations differ (labeled).
- DeepSeek API does not return cost; tokens are the budget record.

## Next step

**Modify method, then re-run** (not stop, not claim success):
1. Remove or randomize the hint and measure true model choices;
2. Compare `hint-only (no LLM)` vs `LLM` vs `random` to isolate value added;
3. Only if LLM > hint-only and > random on train, freeze and move to full train split.
