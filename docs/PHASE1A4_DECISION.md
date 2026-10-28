# Phase-1A-4 Decision

## Verdict on DPR-SHADE as specified

**`METHOD_REVISION_REQUIRED`** — not eligible for larger experiments as-is.

Evidence (3 seeds, 500 FE, train F1/F10/F20):
- Reset/shrink beats no-reset (8-1) and no-shrink (7-2): **reset family worth keeping**.
- **State triggers lose to shuffled triggers (3-6):** the claimed
  diversity/stall detector is not the source of benefit. Random resets win.

This is the same attribution failure pattern as A2R: mechanism fires ≠
mechanism is what works.

## What is retained

1. **Reset/shrink family** (memory reset + N reduction + immigrants) is a
   viable research object.
2. Honest empirical question (Path R-adjacent): *when do restarts/resets help
   SHADE-like algorithms?* — publishable as analysis without novelty claims.
3. Agent contribution remains **unverified** (no LLM this phase). Do not
   claim Agent-EC improvement from this pilot.

## What is closed

- CC-SOC / quality credit line: closed (3N2).
- DPR-SHADE's specific stall+quantile triggers: **rejected by shuffled control**.
- No 2000-FE formal run; no Phase-1B.

## Next (concrete)

Either (a) redesign trigger using information the shuffle control cannot
mimic (e.g. predicted improvement from *held-out* restart trials — needs new
protocol), or (b) switch to an empirical paper on restart policies in SHADE
with honest baselines. Whichever: re-run a shuffled control **before** any
expansion. Agent stays as diagnosis tool until then.

## Evidence

- code `56c319064c92…`; results `results/phase1a4/manifest_a4pilot-56c319064c92-clean-20261028T151259.json`
- tests: `tests/test_phase1a4_dpr.py` 3 passed; suite 273+ passed on branch
- 0 LLM; 0 test/val access; MetaBox train only
