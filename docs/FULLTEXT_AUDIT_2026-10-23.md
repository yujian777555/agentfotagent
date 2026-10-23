# Full-Text Mechanism Audit — 2026-10-23

## Scope and evidence labels

This is a first-pass mechanism audit of directly related papers and official code. “Full paper reviewed” means the paper text was accessible and relevant method sections were inspected. “Official code reviewed” means the repository or source files were inspected. It does not mean the methods were independently reproduced. LAOS and the 2026 LMCOEA journal article remain limited to publisher records/abstracts in this pass.

## 1. Agent/LLM improves evolutionary computation

### EoH — Evolution of Heuristics

Sources: [full paper](https://arxiv.org/abs/2401.02051), [official code](https://github.com/FeiLiu36/EOH).

The individual is a heuristic, represented by both a natural-language thought and executable code. The method evolves both representations, uses LLM prompt strategies for initialization/mutation/crossover, evaluates candidates on problem instances, and selects the best population. This is direct prior art for using an LLM inside an evolutionary loop to invent/improve optimization heuristics. It does not by itself establish transfer from numerical optimization control to Agent RSI.

### LLaMEA and LLaMEA-HPO

Sources: [LLaMEA paper](https://arxiv.org/abs/2405.20132), [official code](https://github.com/XAI-liacs/LLaMEA), [LLaMEA-HPO paper](https://arxiv.org/abs/2410.16309).

The official LLaMEA source supports generation and evaluation of complete algorithm classes, LLM mutation/crossover operators, parent-selection alternatives, adaptive mutation, feature-guided mutation, multi-objective fitness/Pareto archives, novelty/niching and optional HPO. LLaMEA-HPO explicitly separates structural algorithm generation from numeric hyperparameter optimization using SMAC. Therefore, neither “evolve the optimizer” nor “separate algorithm structure from numeric tuning” is a novel claim by itself. The LLaMEA PDF endpoint exceeded the current reader's content limit; the official code and LLaMEA-HPO full paper were inspected instead.

### LLM4EO — Online Operator Design in Evolutionary Optimization

Source: [full paper](https://arxiv.org/abs/2511.16485).

LLM4EO initializes operators using prior knowledge, reads evolutionary-state features and operator fitness, diagnoses limitations, and performs operator-level meta-evolution when the search stagnates. Operator fitness is defined from the success ratio of operator uses that yield better offspring. The paper evaluates flexible job-shop scheduling and includes component ablations. This is a direct collision with the generic claim “Agent observes search state/stagnation and edits operators online.” The paper's target is a scheduling domain; it does not establish the specific MetaBox-numerical-optimizer to Agent-genotype transfer proposed here.

### LAOS — Large Language Model-Driven Adaptive Operator Selection

Sources: [official GECCO program abstract](https://gecco-2025.sigevo.org/display1863), [ACM DOI](https://doi.org/10.1145/3712256.3726450).

The official conference abstract states that the LLM meta-prompt receives optimization progress, best fitness, population diversity and operator-credit assignment; it also describes a dual-layer replay buffer, with offline experience from fixed operator strategies and online experience accumulated during execution. The full ACM paper was not accessible through the available route and no official code repository was found in this pass. Exact credit formula, replay sampling, update timing and ablation evidence remain **unverified**. Do not infer details beyond the official abstract.

### AwesomeDE and LMCOEA

Sources: [AwesomeDE full paper](https://arxiv.org/abs/2509.13251), [LMCOEA publisher record and indexed method excerpts](https://www.sciencedirect.com/science/article/pii/S095741742600669X), [LMCOEA DOI](https://doi.org/10.1016/j.eswa.2026.131756).

The AwesomeDE paper uses MetaBBO meta-training to construct an LLM meta-optimizer that generates update rules for constrained evolutionary algorithms across constrained optimization problem families. The 2026 LMCOEA article describes a bi-level MetaBBO-EL process: an LLM serves as the meta-optimizer's evolutionary strategy to generate/update constrained-EA rules, which are evaluated by base evolution; it also introduces RTO²H prompt engineering and reports evaluation over 18 scalable constrained problems. This is a close method-family collision. The full LMCOEA PDF and official code were not accessible in this pass, so exact equivalence or version lineage is not established.

### MetaBox-v2

Sources: [paper](https://arxiv.org/abs/2505.17745), [official code at v2.0.0](https://github.com/MetaEvo/MetaBox/tree/v2.0.0).

The official README/API and version tag were reviewed, but MetaBox was not installed or run in this project. Version-specific baseline counts differ between the current README and paper abstract, so experiments must pin the exact version and report the corresponding counts. MetaBox is infrastructure, not the research contribution.

## 2. Evolutionary optimization of Agents and RSI

### EvoAgent

Source: [full NAACL 2025 paper](https://aclanthology.org/2025.naacl-long.315.pdf).

EvoAgent starts from a predefined specialized Agent framework, treats roles/skills/prompts/settings as evolvable variables, and uses LLM-mediated crossover, mutation and quality-check selection to generate diverse specialized agents that cooperate as a multi-agent system. It establishes that evolutionary operators can generate/extend Agent systems. Its main object is multi-agent population generation, not a controller transferred from numerical optimization.

### ARTEMIS

Source: [full paper](https://arxiv.org/abs/2512.09108).

ARTEMIS treats an Agent as a black box and jointly optimizes mixed-type configuration components, including natural-language and numeric fields. It uses semantically aware mutation and crossover, benchmark outcomes and execution logs. The paper reports that prompt/configuration automation does not transfer uniformly across domains. A generic EA over Agent settings is therefore not enough; the current proposal must distinguish its controller-transfer mechanism and compare against direct target-domain evolution.

### GEPA

Source: [ICLR 2026 full paper](https://proceedings.iclr.cc/paper_files/paper/2026/file/0e9e708b6f48e14fd0ac29e167413f76-Paper-Conference.pdf).

GEPA performs reflective prompt mutation and system-aware merge using textual feedback from task trajectories. Its Pareto-based “illumination” strategy maintains candidates that perform best on different tasks rather than always mutating the single global champion. This is a strong baseline for prompt/Agent improvement and multi-task transfer; reflection, per-task Pareto lessons and semantic prompt mutation are not new contributions for this project.

### Darwin Gödel Machine (DGM)

Sources: [full paper](https://arxiv.org/abs/2505.22954), [official code](https://github.com/jennyzhang0215/dgm).

DGM maintains an archive of self-modified coding agents, samples parents from the archive, mutates code and empirically evaluates offspring. It provides an open-ended evolutionary RSI baseline. The original DGM's archive-based agent evolution should be distinguished from methods that explicitly evolve the meta-level improvement procedure itself.

### Huxley-Gödel Machine (HGM)

Sources: [full paper](https://openreview.net/forum?id=T0EiEuhOOL), [official code](https://github.com/metauto-ai/HGM).

HGM estimates clade/meta-productivity from descendants' outcomes and uses Thompson sampling with an exploration/exploitation schedule to choose agents for further expansion/evaluation. Any proposed “lineage value”, “future descendant productivity” or productivity-guided parent-selection novelty must be compared directly with HGM rather than renamed.

### Hyperagents

Sources: [full paper](https://arxiv.org/abs/2603.19461), [official code](https://github.com/facebookresearch/Hyperagents).

Hyperagents combines a task Agent and a meta Agent in a single editable program; critically, the meta-level modification procedure is itself modifiable. It reports that meta-level improvements transfer across domains. This is a very close conceptual neighbor to generic bidirectional/recursive improvement. The project cannot claim novelty from making the improver improve itself; it must show the independent value of a specific MetaBox-derived control object and a distinct transfer method.

### AIDE²

Source: [full paper](https://arxiv.org/abs/2609.26457).

AIDE² uses an outer-loop Agent to rewrite a research Agent's code and accepts candidates only after improvement on a private/held-out grade. It evaluates generalization on external benchmarks and reports reward-hacking analysis. It is a strong RSI baseline for hidden evaluation, task-Agent versus improver separation, and held-out transfer.

### MASS

Sources: [full paper](https://arxiv.org/abs/2610.12176), [official code](https://github.com/SakanaAI/mass).

MASS asks a base model to propose, execute and self-evaluate multi-agent workflows under structural guardrails, then alternates evolutionary workflow search with trajectory-based supervised fine-tuning. The exact training loop differs from MetaBox controller transfer, but the broad claim that evolution can recursively improve Agent workflows is already covered.

### Harmony Harness

Source: [full paper](https://arxiv.org/abs/2610.15150).

Harmony Harness uses decomposition-based multi-objective evolution of Agent harnesses. It factorizes general-purpose mechanisms from benchmark-specific adaptation and dynamically composes them; it reports cross-benchmark transfer. This directly limits claims based only on separating “general control” from “domain-specific adapter”. The proposed method needs to identify a distinct transfer object and show why mapping a controller from numerical optimizer state/actions to a different Agent-genotype space is not merely the same factorization principle.

### RSI-Router

Source: [full paper](https://arxiv.org/abs/2609.34712).

RSI-Router recursively evolves subtask definitions, model routing and model-specific skills. It selects routers on a performance-cost Pareto frontier and retains dominated routers as negative experience for later evolution. This is direct prior art for history-driven Agent RSI, Pareto selection, skill evolution and feedback-driven improvement.

### CoCoEvolve

Source: [full paper](https://arxiv.org/abs/2610.12794).

CoCoEvolve's meta-reflective mutator retrieves evidence from the full evolutionary history, probes the live target system, tests hypotheses and verifies proposed changes before accepting them. Its paper includes ablations of history-access interfaces. Historical retrieval, environment probing and verified Agent mutation must be treated as existing mechanisms.

## 3. Novelty assessment after method review

### Claims that should be rejected as standalone contributions

- “Use an Agent/LLM to improve an evolutionary algorithm.”
- “Use evolutionary computation to improve Agent configurations/workflows.”
- “Add Pareto selection, diversity, historical memory, reflection or online operator mutation.”
- “Make the optimizer/Agent recursively improve itself.”
- “Transfer a general mechanism across tasks” without defining a novel transfer object and adaptation mechanism.
- “Use MetaBox to evaluate the method.”

### Candidate still worth testing, but not yet a confirmed gap

A single, explicitly defined controller discovered/selected on numerical MetaBox tasks is transferred into a structurally different Agent-genotype search space. The study must demonstrate that:
1. the same controller object is transferred, rather than merely copying an idea or hand-writing a target-domain policy;
2. the mapping from source states/actions to target states/actions is nontrivial and reproducible;
3. the transfer beats fixed generic control, target-domain tuning, standard adaptive EA, random search and shuffled/random mappings;
4. target-domain feedback adds value only if H2 first succeeds, and H3 beats one-way transfer on held-out tasks;
5. the result is distinct from the general/task-specific factorization in Harmony Harness, the meta-level transfer in Hyperagents, and MetaBBO-based rule generation in AwesomeDE/LMCOEA.

Current novelty risk: **HIGH**. LAOS and LMCOEA still need full-text/code access. If the mechanism-level gap cannot be defended, revise the research idea before implementation.
