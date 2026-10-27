# Phase-1A P1A-1E DeepSeek Flash Preflight Report

- Branch: `phase1a-p1a1-flash-preflight`
- Code SHA: `810f7c5b242f67afd1bed5059de8409c73bd935e`
- Model: **`deepseek-flash` only** (confirmed available)
- Prompt: `p1a1d-agent-v1-flash` (same pure-text protocol as P1A-1D; no examples, no hint)
- Preflight: 3/3 requests, 0 retries · `results/p1a1_pilot/preflight_p1a1e_flash_p1a1d-agent-v1-flash.json`
- Verdict: **LLM_POLICY_DEGENERATE** — formal experiment **NOT STARTED**

## Flash availability

`deepseek-flash` responds with `thinking=disabled` + `json_object`.
HTTP OK, `finish_reason=stop`, `reasoning_content` empty.

## Single-variable preflight

| state | stag | budget | action | valid | hint |
|---|---:|---:|---|---|---|
| A | 2 | 0.40 | `set_F=0.7` | ✓ | set_F=0.5 |
| B | 8 | 0.40 | `set_F=0.7` | ✓ | set_F=0.8 |
| C | 2 | 0.85 | `set_F=0.7` | ✓ | set_CR=0.3 |

UNIQUE_SIGS = `{('set_F', 0.7)}` — identical to the P1A-1D `deepseek-v4-pro` attractor.

## Gates

| gate | result |
|---|---|
| 3/3 real requests success | PASS |
| 3/3 legal DSL actions | PASS |
| ≥2 distinct signatures | **FAIL** |
| single-variable change → signature change | **FAIL** |
| no hint leak / no old cache / no unexplained failure | PASS (new cache ns `…-flash`) |

## Budget

3 requests · 540 prompt / 54 completion tokens · 0 empty · 0 API failures ·
cost not returned by API.

## Decision

**`LLM_POLICY_DEGENERATE` on `deepseek-flash` as well.**  
Switching the model family did **not** produce state-dependent control actions
under the same no-example protocol. Do not start the 42-run formal experiment.
Do not fake diversity.

Cross-model observation (P1A-1D v4-pro vs P1A-1E flash): both collapse to
`set_F=0.7` regardless of stag/budget. This strengthens the conclusion that
the current instruction format does not elicit trajectory-conditioned
parameter choice from DeepSeek chat models at temperature 0.

Options left (not executed here): state-computed numeric field with
consistency validation; a different model family with free numeric control;
or stop the H1 LLM-control branch.
