# LAOS and LMCOEA Mechanism Audit — 2026-10-26

## Scope and evidence boundary

This audit is for **Agent-for-Agent (yujian777555/agentfotagent) only**. It continues P0-R2, the novelty-collision and cross-representation-transfer audit. It does not use or update the separate openissue thesis project.

No experiment was run, no source repository was installed, no generated algorithm was executed, and no live LLM API was called.

Sources inspected:
- LAOS official GECCO 2025 proceedings abstract: https://gecco-2025.sigevo.org/display1874
- LAOS official conference program: https://gecco-2025.sigevo.org/display1865
- LAOS DOI: https://doi.org/10.1145/3712256.3726450
- LMCOEA journal article: https://doi.org/10.1016/j.eswa.2026.131756
- LMCOEA linked code repository: https://github.com/Yxxx616/LMCOEA
- MetaBBO platform cited by LMCOEA: https://doi.org/10.48550/arXiv.2503.22722

LAOS full paper and official implementation were not obtained in this pass. Its mechanism description below is limited to the official conference/publisher abstract. For LMCOEA, the publisher's indexed article text exposed method/experiment/conclusion excerpts, but a direct open of the ScienceDirect page returned 403; the linked code repository was inspected statically. Neither paper was independently reproduced.

## 1. LAOS — Large Language Model-Driven Adaptive Operator Selection for Evolutionary Algorithms

**Citation:** Yisong Zhang and Guoxing Yi, GECCO 2025, pp. 517–526, DOI 10.1145/3712256.3726450.

### Verified mechanism

The official proceedings abstract describes an LLM-based adaptive operator selection (AOS) framework. Its meta-prompt contains optimization-state information, including optimization progress, best fitness and population diversity, together with operator credit assignment. LAOS also uses a dual-layer replay buffer:
- **Offline layer:** historical experience collected under fixed operator strategies.
- **Online layer:** experience generated dynamically during the current optimization run.

An experience-sampling mechanism supplies the LLM with prior examples to support subsequent operator-selection decisions. The paper reports tests on continuous numerical optimization and three categories of combinatorial optimization.

### Overlap with Agent-for-Agent

LAOS directly overlaps the generic H1 claim that an LLM/Agent can inspect evolutionary state, use operator-performance feedback, consult historical experience, and adaptively choose evolutionary operators. These elements cannot be claimed as the core innovation of this project.

It also constrains H2. A transfer proposal based on “learn a state-conditioned controller and apply it to another search domain” must be distinguished from simply reusing LAOS-like state features and an operator-selection prompt. The target action mapping must preserve meaningful controller semantics rather than manually rename target operators to generic roles.

### Evidence limits

The official proceedings page confirms the high-level method, but the full paper, detailed credit formula, replay sampling/update equations, ablations, and official code were not verified here. Do not describe these unverified details as audited facts. No official LAOS code repository was located in this pass.

## 2. LMCOEA — Large Language Model Assisted Meta-Evolution for Automated Constrained Optimization Evolutionary Algorithm Design

**Citation:** Xu Yang, Rui Wang, Kaiwen Li, Wenhua Li, Weixiong Huang and Wei Liu, *Expert Systems with Applications* 317 (2026), article 131756, DOI 10.1016/j.eswa.2026.131756.

### Verified high-level method

The article describes an LLM-assisted meta-evolution framework for constrained optimization evolutionary algorithms (COEAs), implemented in an evolutionary-learning MetaBBO setting. The LLM acts as a meta-level variation/generation mechanism for base-level update rules. Its RTO²H prompt framework uses history and constraints to guide generation. The generated update rules are evaluated by base-level evolutionary runs over multiple constrained optimization problems; the reported objective is to discover update rules that generalize across the source problem family.

### Static code inspection

The linked repository's current main SHA is a1d3f71639fb2c77af25c7c3f52bd9e1f87f1e03. The inspected tree contains six root files:
- Awesome_DE_MS_Metaoptimizer.m
- Awesome_DE_MS_Baseoptimizer.m
- Awesome_DE_MS_Metaoptimizer_finalAgent.mat
- README.md
- appendToHistory.m
- testdeepseek.py

The README describes a larger src/ layout and uses generic yourusername URLs, but those paths are not present in the observed tree. The README claims an MIT license, yet no root LICENSE file is present in the observed tree. Treat licensing and completeness as unresolved; do not assume the README statement alone establishes repository terms.

The code shows the following mechanism:
1. testdeepseek.py asks a DeepSeek chat model to generate a MATLAB updateFuncN implementation for differential-evolution offspring generation.
2. Awesome_DE_MS_Baseoptimizer.m executes that function over a constrained optimization problem and compares its score with a baseline DE run. The reward is based on the difference from the baseline score; failed generated code triggers a fallback DE path and a -999 reward.
3. Awesome_DE_MS_Metaoptimizer.m tracks candidate generated strategies and per-problem rewards, aggregates reward across problems, and keeps high-scoring strategy IDs. Later prompts can include historical strategies and scores.
4. The inspected state includes flattened population decisions, objective values, constraint violations and a problem index. The target-level action is a generated mutation/update rule or its strategy ID—not an abstract, already domain-invariant controller.

### Code/reproducibility caveats

- testdeepseek.py contains the literal placeholder string deepseekey as its API-key value. This is not a usable secret, but it is still a poor configuration pattern; no API call was made.
- MATLAB files contain machine-specific Windows paths for generated update rules and history. The repository is not self-contained as published.
- In loadHistory, for i = 1:length(obj.metaNP) iterates only once when metaNP is the scalar value 5; this appears inconsistent with the stated intent to include the five best strategies.
- The code does not provide a verified standalone reproduction of the paper's full MetaBBO setup. No code was executed, and the article's reported performance is not independently reproduced by this project.

### Overlap and implication

LMCOEA is a direct nearest neighbor for LLM-driven meta-level generation/evolution of executable EA update rules, with cross-problem learning inside numerical constrained optimization. Together with AwesomeDE, it makes “LLM generates EA rules and evolutionary selection improves them” an insufficient novelty claim.

However, the inspected LMCOEA update rule is a **DE-specific MATLAB offspring-generation function** operating on numerical vectors, objective values and constraint violations. It is not itself a controller that can be dropped into an Agent-genotype search space. A claim that the *same controller object* transfers to Agent RSI therefore still lacks a concrete object and semantic mapping.

## 3. What the two audits imply for H1/H2/H3

| Hypothesis | Updated assessment | Reason |
|---|---|---|
| H1 — Agent diagnoses evolutionary traces and improves operators | **Rejected as a standalone novelty claim** | LAOS directly covers state-conditioned LLM operator selection with operator credit assignment and offline/online experience replay; LLM4EO and other reviewed work further overlap meta-evolution. |
| H2 — transfer the same controller object from numerical optimization to Agent-genotype evolution | **Still unproven; transfer object remains undefined** | LAOS offers a high-level operator-selection controller but its target action space is EA operators; LMCOEA evolves a DE update-rule program. Neither supplies an off-the-shelf, semantically invariant controller for Agent-genotype mutation. |
| H3 — use Agent evolution feedback to improve the controller recursively | **Conditional and not currently justified** | It depends on H2 having a nontrivial, reproducible transfer effect; generic recursive feedback is already crowded prior art. |

## 4. Mandatory transfer-object gate before implementation

The next step is to define one transfer object precisely and attempt to falsify it. For the chosen object, document:
- source observation features and which remain meaningful in the target domain;
- source actions and their target counterparts;
- which action semantics are invariant, and evidence for that invariance;
- what mapping/adaptation data are learned from target development tasks;
- why this is not just a hand-written adapter, a generic AOS policy, or target-domain retraining;
- a shuffled-mapping negative control and an independently held-out target task-family split.

The existing project plan lists three candidate representations—executable state-action rules, policy parameters, or a learned control representation. Do not blend them into one vague “controller.” If none can be transferred without hand-authoring target semantics, or if the best result is explained by target-only tuning, revise or abandon H2 before coding.

## 5. Immediate next actions

1. Record LAOS as **official-abstract verified, full text/code not obtained**, not as fully audited.
2. Record LMCOEA as **publisher method text partially retrieved and linked code statically inspected; not reproduced; repository completeness/license unresolved**.
3. Formalize and compare the candidate transfer objects against LAOS, LMCOEA/AwesomeDE and Harmony Harness.
4. In parallel, audit the actual executable genotype, evaluator, and random-search arm in the candidate downstream repositories NeuroEvoScientist and EvoPareto-Agent. Do not modify those repositories.
5. No algorithm implementation, MetaBox run, or live LLM API experiment until the transfer-object and phenotype/evaluator gates pass.
