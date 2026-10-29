# Phase-1A-12 Prior-Work Comparison

- Date: 2026-10-29
- Scope: design-stage targeted review of direct Agent-policy evolution versus MetaBox-to-AES transfer.
- No external code executed; no LLM calls; no MetaBox/AES performance runs; no held-out results accessed.
- This is a targeted review, not an exhaustive systematic review. Evidence labels distinguish primary-source pages, official code inspected, and prior project notes.

## Decision in brief

**Neither route is cleared as novel.** Direct evolution is immediately aligned with the target, but the generic route is now strongly covered by direct prior art—most importantly **EvoTool (ACL 2026)**, whose official paper and implementation explicitly use trajectory-grounded blame attribution, LLM-guided targeted mutation of a modular tool-use policy, and diversity-aware evolutionary selection. AgentSquare covers modular Agent search; EvoAgent covers evolutionary multi-agent generation; EvoPrompt and Promptbreeder cover evolutionary prompt optimization; TTHE and Evoflux cover executable harness/workflow evolution from execution feedback.

Transfer has a more specific question, but there is no validated source controller and no established state/action correspondence. Existing project audits also identify Hyperagents and Harmony Harness as overlaps for generic meta-level improvement and cross-domain harness transfer.

**Phase-1A-12 decision update: `NO_GO_AS_GENERIC_METHOD` for direct Agent evolution; `NOT_READY` for transfer; continue only with a narrower, mechanism-level gap search.** The Agent application target remains fixed; this is not a project-wide NO-GO.

## Comparison matrix

| Work | Search object / role of evolution | Feedback and selection | Overlap with this project | Implication |
|---|---|---|---|---|
| EoH (Liu et al., ICML 2024) | Evolves natural-language heuristic thoughts and executable code for heuristic design | Benchmark fitness; evolutionary proposal/selection | LLM + EC generating executable strategies | “LLM proposes, EA selects executable candidates” is not novel by itself. [Primary proceedings page](https://proceedings.mlr.press/v235/liu24bs.html) |
| LLaMEA (van Stein & Bäck, IEEE TEVC 2025) | Evolves algorithm classes/implementations | Runtime performance feedback; evolutionary mutation/selection | Automated evolutionary search over executable algorithm objects | Need a mechanism beyond generic LLM mutation and fitness selection. [Paper](https://arxiv.org/abs/2405.20132) |
| EvoPrompt (Guo et al., ICLR 2024) | Evolves natural-language prompts with EA operators and LLM-generated offspring | Development-set task fitness | Direct overlap if AES genotype is merely prompt variants | Prompt-as-genome and LLM+EA are already covered. [Primary conference page](https://proceedings.iclr.cc/paper_files/paper/2024/hash/9156b0f6dfa9bbd18c79cc459ef5d61c-Abstract-Conference.html); [official code](https://github.com/microsoft/EvoPrompt) |
| Promptbreeder (Fernando et al., ICML 2024) | Evolves task prompts and the mutation prompts that generate them | Training fitness; self-referential mutation-prompt evolution | Recursive prompt/self-improvement | A generic self-improving prompt/evolution loop is covered. [Primary proceedings page](https://proceedings.mlr.press/v235/fernando24a.html) |
| GEPA (ICLR 2026; existing project audit) | Reflectively evolves prompts/system components from execution trajectories and uses Pareto selection | Natural-language diagnosis, candidate edits, execution feedback | Trace-guided Agent/prompt improvement | “Trace diagnosis + reflection + Pareto evolution” is not a sufficient novelty claim. [Primary conference page](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html) |
| AgentSquare (Shang et al., ICLR 2025) | Modular Agent search over Planning, Reasoning, Tool Use, and Memory; module evolution/recombination; in-context performance predictor | Task scores across six benchmark settings | Direct overlap with current AES genes and any expanded modular Agent genome | Enlarging the genome to planning/memory/tool/recovery modules and running an EA is not a contribution by itself. [Primary conference page](https://proceedings.iclr.cc/paper_files/paper/2025/hash/0ae94013da7cd459402fd77874e09ee3-Abstract-Conference.html); [official code](https://github.com/tsinghua-fib-lab/AgentSquare) |
| EvoAgent (Yuan et al., NAACL 2025) | Evolves existing Agent frameworks into multi-agent systems using mutation, crossover and selection | Task performance over diverse settings | Evolutionary generation and selection of Agent structures | Generic evolutionary Agent design is covered. [ACL Anthology](https://aclanthology.org/2025.naacl-long.315/) |
| **EvoTool (Yang et al., ACL 2026)** | Four evolvable prompt modules: Planner, Selector, Caller, Synthesizer | Trajectory-grounded LLM blame attribution; mutate only the blamed module using natural-language feedback; diversity-aware population selection | **Near-direct overlap with the obvious proposal** to diagnose Agent traces, target a faulty module, mutate it with an LLM, and preserve diverse policies | **Do not reinvent this loop under a new name.** ACL primary paper and official `SPEC.md`, `blame.py`, `mutate.py`, `select.py`, `loop.py`, and `policy/modules.py` were inspected. [ACL 2026 paper](https://aclanthology.org/2026.acl-long.2016/); [official implementation](https://github.com/SYang2000/ACL_2026_EvoTool) |
| TTHE (Nie et al., 2026) | Evolves executable Agent harnesses during evaluation from unlabeled execution traces | Agentic proposers and judge use execution-derived signals; frozen underlying LLM | Evolution of executable control/harness programs and trace-feedback adaptation | Generic “evolve the harness from execution traces” is covered; detailed protocol comparison remains partial. [arXiv:2607.08124](https://arxiv.org/abs/2607.08124) |
| Evoflux (Bhandari et al., 2026) | Evolves executable tool-workflow graphs with typed edits, execution feedback, adaptive edit intensity, meta-guided redesign and diversity pruning | Execution feasibility and downstream task outcomes | Evolution of tool workflows and repair from execution feedback | Workflow evolution alone is not a sufficient novelty claim. [arXiv:2606.12674](https://arxiv.org/abs/2606.12674) |
| ToolMaze (Zhu et al., 2026) | Benchmark for dynamic replanning and anomaly recovery with DAG complexity and explicit/implicit × transient/permanent tool perturbations | Verifiable recovery metrics and task completion | Proposed AES task-difficulty factors around dependencies and tool failures | Adding tool failures or DAG tasks is useful evaluation design, not itself a novel method. [arXiv:2606.05806](https://arxiv.org/abs/2606.05806) |
| Hyperagents (existing project audit) | Modifies the procedure that improves an agent/system, including meta-level transfer | Performance feedback over self-modification | Recursive/meta-level improvement and transfer narrative | Bidirectional feedback or transfer alone is not novel; prior project audit is not a fresh full-text review in this pass. |
| Harmony Harness (existing project audit) | Evolves compositional general/task-specific harness components with cross-benchmark transfer | Task metrics and harness component selection | Factorized Agent harness and transfer | Componentized genome or cross-task transfer is not enough; prior project audit is not a fresh full-text review in this pass. |
| LAOS / LLM4EO (existing project audit) | LLM-driven state-conditioned operator/control adaptation in numerical EC | Search state/progress and operator-credit feedback | Track A numerical controller design | Generic LLM-assisted operator selection should not be the contribution. Existing evidence levels remain as recorded in the project literature matrix. |

## Evidence level for the new 2026 overlap

### EvoTool — strongest direct overlap

**Evidence: primary paper + official code inspected.** The ACL Anthology identifies the paper as ACL 2026, pages 43553–43572, DOI [10.18653/v1/2026.acl-long.2016](https://doi.org/10.18653/v1/2026.acl-long.2016). The official repo at [SYang2000/ACL_2026_EvoTool](https://github.com/SYang2000/ACL_2026_EvoTool) was inspected:
- `SPEC.md` defines a four-module policy and its rollout/evaluation contract;
- `src/evolve/blame.py` uses the LLM to assign one blamed module from a full per-substep trajectory;
- `src/evolve/mutate.py` rewrites only the blamed module using trajectory and critique signals;
- `src/evolve/select.py` includes diversity selection by instance-wise winners and compares greedy/top-k baselines;
- `src/evolve/loop.py` implements the self-evolving loop, including parent selection, targeted mutation, child acceptance, and population selection.

These are the same mechanism family that a generic Phase-1A-12 direct route would otherwise propose. A narrower contribution must be more than changing the module names, task generator, or fitness tie-breaker.

### TTHE / Evoflux / ToolMaze — high-risk recent overlap

These were checked at their primary arXiv pages, not reproduced. TTHE explicitly evolves executable harnesses from execution traces during evaluation; Evoflux evolves executable tool-workflow graphs with execution feedback; ToolMaze formalizes dynamic replanning and tool anomaly recovery. They reduce confidence in generic claims about trace-guided harness evolution, workflow repair, and adding tool-failure tasks. Full-text/official-code audits are still required before asserting exact algorithm identity or absence of overlap.

## Route A — direct target-domain LLM-assisted EC

**Definition:** use a fixed LLM backbone as the task-solving Agent while EC searches a versioned, executable policy/genotype representation; the evaluator scores actual terminal environment state.

A potentially meaningful question is still possible, but it must be narrower than “can EC improve an Agent?” For example, one could investigate a specific EC mechanism for typed, executable, state-transition-constrained Agent policies and prove that it contributes beyond exhaustive/random search and LLM-only self-refinement. This is **not yet a candidate** because the mechanism-level prior-art gap has not been established.

The following are insufficient on their own:
- evolving prompts (EvoPrompt/Promptbreeder/GEPA overlap);
- evolving modules in planning/memory/tool use (AgentSquare overlap);
- trace-based blame + targeted LLM mutation + diversity selection (EvoTool overlap);
- evolving executable harnesses/workflows from traces (TTHE/Evoflux overlap);
- adding tool-failure tasks or DAG dependencies (ToolMaze evaluation overlap);
- generic evolutionary generation of multi-agent systems (EvoAgent overlap).

The current `aes-genome-v1` has only 16 configurations and the historical mock pilot saturated. The proposed `aes-genome-v2` is a design scaffold, **not approved for implementation as a research method** until a distinct mechanism is identified.

## Route B — MetaBox-to-AES transfer

**Definition:** validate an explicit high-level controller on numerical optimization traces, then map the same controller object into AES policy evolution.

Current blockers:
1. No Track-A controller passed novelty and performance gates.
2. No validated mapping exists between source-domain states/actions and target-domain Agent-search states/actions.
3. Existing project audits already identify Hyperagents/Harmony Harness as overlaps for broad meta-level transfer and factorized harness transfer.
4. TTHE adds a recent, direct example of evolving executable harnesses from Agent execution traces.
5. An adapter alone is not a method contribution.

Transfer is not ready for an experiment. Reconsider only after a concrete controller exists, its source/target semantics are specified before target evaluation, and target-only and shuffled-mapping controls are frozen.

## Experimental-design implications (engineering only)

The Phase-1A-12 design docs remain useful as **readiness contracts**, not as a research contribution:
- `PHASE1A12_GENOME_V2_SPEC.md`: semantic intervention and canonicalization checks before implementation;
- `PHASE1A12_TASK_DIFFICULTY_SPEC.md`: train/dev-only calibration and terminal-state verifiability;
- `PHASE1A12_FITNESS_AND_BASELINE_CONTRACT.md`: success-first lexicographic fitness and fair baselines.

For the current 16-genome version, exhaustive enumeration is the exact reference. After any approved redesign, compare fixed policy, random unique-genome search, conventional EA, and LLM-only/self-refinement with matched episodes and costs. Do not run until the mechanism novelty gate and AES readiness gate pass.

## Overall decision

- Direct generic Agent evolution: **`NO_GO_AS_GENERIC_METHOD`**.
- Transfer: **`NOT_READY`**.
- AES v2: design-only, not approved for implementation as a claimed method.
- Project objective: **unchanged**—apply a validated LLM-empowered EC method to Agent improvement.
- Next activity: search for a specific EC mechanism gap that remains after EvoTool, AgentSquare, TTHE, Evoflux, EvoPrompt, Promptbreeder, EoH/LLaMEA and the existing transfer audits. Do not spend API or performance budget on a generic version of an already published loop.
