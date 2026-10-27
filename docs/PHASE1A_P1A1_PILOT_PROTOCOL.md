# Phase-1A P1A-1 Pilot Protocol

- Experiment: `P1A1_AGENT_DE_PILOT`
- Hypothesis H1: trajectory-conditioned LLM control of DE parameters beats fixed-parameter DE and deterministic rule controllers under equal FE budget and seeds.
- Status: exploratory pilot (3 functions × 2 seeds × 300 FE). Not confirmatory.

## Domain and split

- Platform: MetaBox metaevobox 2.0.2 (PyPI), BBOB-10D, minimize.
- Functions from **split_v2 train only**: F1 (separable, difficult), F10 (high conditioning, easy), F20 (multimodal weak, easy).
- Seeds 11, 22. Population 20. Max FE 300. Dim 10.

## Methods

1. `official_meta_de` — MetaBox DE (separate implementation).
2. `fixed_classic_de` — controlled DE, DSL controller F=0.5.
3. `fixed_explore_de` — controlled DE, exploration DSL controller.
4. `stagnation_heuristic` — deterministic stagnation rule (no LLM).
5. `random_valid_controller` — seeded random DSL actions.
6. `llm_agent` — DeepSeek `deepseek-v4-pro` selecting DSL actions from public state.

Methods 2–6 share `controlled_de` (rand/1/bin). Official DE is compared separately.

## LLM agent

- Public state only (gen, F, CR, stagnation, success_fraction, budget).
- DSL actions only: set_F / set_CR / noop. No code execution, no optimum access.
- Budget: ≤100 requests, ≤$1, one retry max (counted). Max output 128 tokens.
- Prompt v5 (`p1a1-agent-v5`): single JSON exemplar + "Pick F=x." because DeepSeek
  reasoning models return empty content on multi-JSON prompts. The hint is
  state-derived scaffolding; **model output is the executed action** and
  hint-vs-output divergence is logged.

## Metrics

Primary: best raw objective (minimize) / regret when optimum known.
Secondary: FE counts, action validity, hint-deviation rate, wall time, tokens.

## Artifacts

`results/p1a1_pilot/manifest_p1a1-<sha>-clean-<ts>.json` and
`results/p1a1_pilot/traces/<run_id>/`. No overwrite of prior runs.
