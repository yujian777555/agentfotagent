# Phase-1A P1A-1B Deconfounded Pilot Report

- Branch: `phase1a-p1a1-deconfounded`
- Code SHA at run: `4c6333adb1f57059088863f233f3074703dbd6af`
- Run ID: `p1a1-4c6333adb1f5-clean-20261027T192647`
- Manifest: `results/p1a1_pilot/manifest_p1a1-4c6333adb1f5-clean-20261027T192647.json`
- Prior hinted pilot preserved separately (`p1a1-319b358…`).

## Question

After removing state-derived hints from the LLM prompt, does the LLM beat
`hint_only` and `random_valid_controller`?

## Setup

7 methods × F1/F10/F20 × seeds 11/22 × 300 FE (planned 42 runs).
`stagnation_heuristic` and `hint_only` are **different** policies (F=0.9 vs F=0.8
at stag≥5) and are reported separately.

Prompt `p1a1b-agent-v3`: public state + fixed format dummy `Pick F=0.5`
(state-independent; required because DeepSeek reasoning models return empty
content otherwise). Hint is computed post-hoc only.

## Execution

- 40/42 non-LLM runs OK; **4/6 LLM runs completed**; 2 LLM runs blocked
  (`BudgetExceeded` 100/100 requests).
- API: requests 100, retries 37, prompt 17000 tok, completion 12084 tok,
  cache 4, **invalid/empty responses 96**. Cost not returned by API.
- FE exact on all completed controlled runs.

## Paired results (completed pairs only; lower metric better)

| func | seed | hint_only | **llm** | random | official |
|---|---|---:|---:|---:|---:|
| F1 | 11 | 3951 | **1011** | 2312 | 6066 |
| F1 | 22 | 8376 | **3197** | 5924 | 8666 |
| F10 | 11 | 4.77e7 | **2.76e7** | 5.23e7 | 8.36e7 |
| F10 | 22 | 7.37e7 | **3.31e7** | 3.75e7 | 5.75e7 |
| F20 | 11 | 6.33e5 | *blocked* | 5.76e5 | 4.64e5 |
| F20 | 22 | 2.00e6 | *blocked* | 1.82e5 | 3.04e5 |

**llm vs hint_only: W=4 L=0** (F20 missing)  
**llm vs random: W=4 L=0** (F20 missing)

## Action independence (critical)

| metric | value |
|---|---|
| valid LLM actions | 28/56 events |
| set_F=0.5 (format dummy echo) | 27 |
| set_CR any | **0** |
| any non-dummy F value | **0** |
| noop fallbacks (empty content) | 28 |
| hint-deviation | 22 (because hint ≠ 0.5) |

**The model never selected an independently chosen parameter value.** Every
valid output was `set_F=0.5` — the fixed format dummy. F/CR histories are
constant 0.5. The win over hint_only/random is explained by the **fixed
(F=0.5, CR=0.5)** point, not by trajectory-conditioned LLM judgment.

## Pre-registered expand gates

| gate | status |
|---|---|
| LLM > hint_only (more W than L) | numerically yes on 4 pairs |
| LLM > random (more W than L) | numerically yes on 4 pairs |
| ≥2/3 functions non-inferior, ≥1 strict win | F1+F10 wins; F20 blocked |
| FE/traces valid, no unexplained failures | 2 LLM runs blocked by request budget |

**Mechanism check fails:** no independent parameter choices. Expanding would
test a constant-F controller labeled "LLM".

## Decision

**MODIFY METHOD — do not expand to full train split.**

Required next changes (not done in this pass):
1. Output format that cannot be satisfied by echoing a single dummy
   (e.g. force a numeric field whose value must differ from the dummy when
   state warrants, or use sampling temperature / logit bias);
2. Raise request budget or shrink generations so F20 is not blocked;
3. Re-run only if the model produces non-dummy choices; otherwise record
   `NO_BENEFIT_LLM_JUDGMENT` and treat fixed-parameter DE as the real control.

## Limitations

- 4/6 LLM pairs only; F20 missing; 96 empty responses from the API.
- Format dummy is state-independent but still a generation bias.
- No test-split access; no MetaBBO; no AES transfer.
