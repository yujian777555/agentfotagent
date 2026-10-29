# Phase-1A-12 Fitness and Baseline Contract (Design Only)

Status: proposal only. No runs, API calls or held-out access.

## Primary outcome
Verified terminal-state task success remains the primary objective. Self-reported completion, a hand-written prior, and action count alone are not success.

## Lexicographic selection proposal
1. Maximize verified success rate.
2. If tied, minimize mean normalized steps among successful episodes.
3. If still tied, minimize invalid-action rate.
4. If still tied, minimize repeated-state/no-progress rate.

Success rate uses all scheduled episodes in its denominator. Failures and timeouts remain visible. Only predeclared infrastructure failures may be retried, and retries remain in the ledger. Normalized steps are steps divided by the fixed task limit, calculated among successful episodes so failed runs cannot appear artificially cheap. Log numerator and denominator for every rate. Do not replace this with an arbitrary weighted sum.

## Required reporting
Report task-family and aggregate success with uncertainty intervals, paired comparisons on shared task instances, successful-episode normalized steps, invalid-action and no-progress rates, backend errors/timeouts, measured tokens/cost, unique genomes, proposals, cache hits and actual episode executions. Freeze model version, decoding and seeds before runs.

## Baselines
For aes-genome-v1, evaluate all 16 normalized genomes exhaustively on the same train tasks; this is the exact finite-space reference.

After a larger genome is accepted, compare:
- fixed hand-designed policy;
- random unique-genome search without replacement;
- a named conventional EA with frozen operators and parameters;
- LLM-only/self-refinement with matched feedback and candidate/episode budget;
- LLM-assisted EC only when its role is explicit and distinct from generic prompt evolution;
- mechanism-specific ablation or shuffled control when required by the causal claim.

## Fairness
Hold fixed the model/backbone and decoding, task manifests and seeds, evaluator, step limit, genome space, cache identity, unique evaluated genomes, episode executions and failure accounting. Report candidate budget and episode budget separately. Cache hits must not create unequal effective evaluations.

## Selection and confirmation
Tune on train; select on dev; freeze method, metric, manifests and statistical plan; obtain separate authorization for a real backend and budget; then evaluate once on sealed confirmation families. Do not feed confirmation outcomes back into method design and still call them test results.

## Stop criteria
Do not start scientific evaluation if policies all saturate or fail, alleles are behaviorally equivalent, baselines have unequal search spaces/budgets, scores cannot be reconstructed from terminal state, LLM-only comparison is unmatched, or data leakage exists. Require a predeclared practical effect and uncertainty interval; no post-hoc metric selection.
