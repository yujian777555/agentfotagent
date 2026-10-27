# Phase-1A P1A-1D Preflight Report

- Branch: `phase1a-p1a1-no-example-preflight`
- Code SHA: `4da5f031ff16c2d6b1ad1df4ec9965875d2274b6`
- Prompt version: `p1a1d-agent-v1` (pure text protocol, **no** concrete examples)
- Preflight: **3/3 requests used** (no retries), artifacts in
  `results/p1a1_pilot/preflight_p1a1d_p1a1d-agent-v1.json`
- Verdict: **LLM_POLICY_DEGENERATE** — formal 42-run experiment **NOT STARTED**

## Single-variable states

| state | stag | budget | other fields |
|---|---:|---:|---|
| A baseline | 2 | 0.40 | gen=5 F=0.5 CR=0.5 succ=0.2 imp=0.1 |
| B high stag | 8 | 0.40 | identical |
| C high budget | 2 | 0.85 | identical |

## Results

| state | model action | valid | finish | empty |
|---|---|---|---|---|
| A | `set_F=0.7` | yes | stop | 0 |
| B | `set_F=0.7` | yes | stop | 0 |
| C | `set_F=0.7` | yes | stop | 0 |

UNIQUE_SIGS = `{('set_F', 0.7)}` — **1 signature only**

Prompt strings differ only in `stag` / `budget` (verified prompt SHA-256:
A `3dab6a10…`, B `0a5d1618…`, C `be0635f4…`). Hint never enters the prompt.

## Gate evaluation

| # | gate | result |
|---|---|---|
| 1 | ≥2/3 legal JSON | **PASS** (3/3) |
| 2 | ≥2 distinct signatures | **FAIL** (1/1) |
| 3 | single-variable change → signature change | **FAIL** (B=A, C=A) |
| 4 | no hint in prompt/cache | PASS |
| 5 | no empty/budget/unexplained failure | PASS |

## Interpretation

Removing concrete examples fixed example-echo (`0.35`) but the model still
returns the **same** action (`set_F=0.7`) for all three states. This is policy
degeneration, not API failure. Forcing diversity would fabricate state
dependence and is forbidden.

## Budget

3 / 140 requests · 531 prompt tokens · 78 completion tokens · 0 reasoning ·
0 empty · 0 API failures · cost not returned by API.

## Decision

**STOP.** `LLM_POLICY_DEGENERATE`. Do not launch the formal 42-run experiment.
Do not re-prompt the same protocol repeatedly.

Evidence-based next options (not executed in this pass):
1. Require a numeric field that **must** be computed from state (e.g. output
   `F_new` as an explicit function of stag/budget) and validate consistency;
2. Try a different model family with proven free-form numeric control;
3. Accept that this DeepSeek model cannot support trajectory-conditioned DE
   parameter control and stop the H1 LLM-control hypothesis.

P1A-1B/C historical artifacts remain untouched.
