# Phase-1A P1A-1C Preflight Diagnostic

- Branch: `phase1a-p1a1-api-contract`
- Code SHA: `68828fa0c96146aa2a593c4e7bb83c85806d3613`
- Preflight budget used: **3/3** requests (0 retries, 0 empty, 0 API failures)
- Status: **LLM_POLICY_DEGENERATE** — formal 42-run re-execution **NOT STARTED**

## API contract fix (verified)

| item | before (P1A-1B) | after (P1A-1C) |
|---|---|---|
| thinking mode | default (consumed all max_tokens) | `thinking:{"type":"disabled"}` |
| response_format | none | `json_object` |
| max_tokens | 128 | 256 |
| empty content | 96/100 requests | **0/3** |
| reasoning_tokens | 128 (all budget) | **0** |
| finish_reason | (unrecorded) | `stop` ×3 |
| diagnostics | partial | id, http, finish_reason, reasoning_len, usage |

Empty-response root cause: DeepSeek reasoning mode burned the entire
`max_tokens` budget so `message.content` stayed empty. Disabling thinking and
using JSON response format resolves this.

## Preflight conditions

| # | condition | result |
|---|---|---|
| 1 | ≥2/3 legal JSON actions | **PASS** (3/3) |
| 2 | ≥2 distinct action signatures across 3 states | **FAIL** (only `set_F=0.35`) |
| 3 | no state-derived hint / Pick placeholder | **PASS** |
| 4 | request/retry/invalid stats consistent | **PASS** (3/3, 0 retry) |
| 5 | client extracts and parses final answer | **PASS** |

### Condition-2 evidence

Three distinct states (low success / high stagnation / late budget) all produced:

```json
{"action":"set_F","params":{"value":0.35}}
```

The model echoes the first syntax example (`0.35`) regardless of state.
This is **decision degeneration**, not API failure. Forcing different values
would fabricate independence and is forbidden.

## Budget accounting (this round)

- Preflight: 3 requests, 480 prompt tokens, 54 completion tokens, 0 reasoning
- Formal experiment: **not run** (gate failed)
- Total: 3 / 140 request budget; cost not returned by API

## Decision

**STOP formal LLM re-run.** Label `LLM_POLICY_DEGENERATE`.

Non-LLM baselines from P1A-1B remain valid and unchanged; they are not
re-reported as new LLM evidence. Do not expand to full train split.

## Next (for a later pass, not executed here)

1. Change the interaction so echo of a single example is not a stable optimum
   (e.g. require a numeric field whose value must be computed from the state,
   or present candidates without numbers and require free numeric output);
2. Or accept that this model+prompt family cannot support trajectory-conditioned
   parameter control and test a different model family;
3. Re-preflight (≤3 requests) before any formal re-run.
