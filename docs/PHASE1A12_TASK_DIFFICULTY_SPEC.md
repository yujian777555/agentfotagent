# Phase-1A-12 Task Difficulty Specification (Design Only)

Status: proposal only. No task generator changes, scientific episodes, API calls, or held-out access.

## Problem
The historical mock pilot reached 100% success for all 16 genotypes on six small train tasks. Repeating those tasks with more seeds/budget will not make the experiment discriminative.

## Train/dev difficulty factors
- Distractors: few irrelevant objects versus multiple decoys with overlapping labels/locations.
- Dependency depth: 2–3 actions versus 5–8 ordered prerequisites.
- Information access: direct clue versus clues distributed across notes, gauges, objects or rooms.
- Action failures: none versus a deterministic seeded invalid action or transient tool error.
- State changes: static world versus earlier action changing later legal actions.
- Recovery cost: harmless error versus an error consuming a step or requiring correction.
- Template variation: multiple dependency structures rather than new seeds of two fixed templates.

All tasks retain a single authoritative terminal-state success predicate. Ambiguous observations do not mean ambiguous success conditions.

## Calibration protocol
1. Create and inspect candidate templates in train/dev only.
2. Verify solvability with a trusted reference planner not available to the Agent.
3. Compare a fixed policy and diagnostic policy variants to detect trivial templates.
4. Reject templates no reference solver can complete within the frozen action limit.
5. Before any real-backend pilot, freeze a train/dev calibration criterion; initial criterion is that the fixed baseline is neither 0% nor 100% successful over the suite.
6. Freeze generator version, seeds and manifest hashes before method selection.
7. Do not read held-out outcomes or modify tasks based on them.

## Recovery semantics
Distinguish invalid action, transient tool failure, stale observation, and genuine dead end. Each must have a deterministic state-transition contract. The Agent must not see the failure-injection schedule or seed.

## Generalization
Current train/dev families are key_crate and dial_set; held-out is relay_route with only three instances. A future confirmatory design should reserve at least two distinct held-out task families and determine instance count from a predeclared precision/power goal. This document does not inspect or specify held-out answers.

## Required tests
- reference solvability within action limit;
- non-saturation across predeclared diagnostic policies on train/dev;
- no hidden-goal/answer leakage;
- tool preconditions enforced by environment;
- deterministic reset/step;
- hidden failure schedule;
- terminal-state score reconstruction;
- generator version/hash recorded;
- train/dev edits cannot mutate held-out artifacts.

Do not make tasks artificially hostile or tune difficulty against held-out results. Every task factor must test a declared policy capability.

## Prior-art boundary (2026-10-29)

ToolMaze (Zhu et al., 2026, [arXiv:2606.05806](https://arxiv.org/abs/2606.05806)) already studies dynamic replanning and tool anomaly recovery using DAG-based task complexity and explicit/implicit × transient/permanent tool perturbations. Therefore, the factors in this document—dependency depth, distractors, action failures and recovery—are **evaluation-readiness design**, not a novelty claim. The AES task suite can still be useful as a controlled engineering target, but it must not be presented as a novel benchmark unless a separate benchmark contribution is justified and audited.
