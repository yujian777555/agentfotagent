# Phase-1A-16 — Typed/Contract-Aware Evolutionary Policy Audit

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Scope: source-level mechanism audit only; no implementation or experiments.
- Question: Is typed/contract-aware evolutionary variation for executable stateful tool-use policies a defensible new EC mechanism?

## 1. Decision summary

**No generic contract-aware variation candidate survives.** Close precedents already cover:
- type-safe genetic programming prevents type-incompatible trees;
- grammar-guided GP constrains legal program syntax and variation;
- constraint-processing GP uses types and semantic constraints to restrict the search space;
- GenProg evolves program patches using test outcomes and execution-path-localized changes;
- proof-guided genetic improvement uses proof search to obtain semantics-preserving transformations;
- LLM + many-objective grammar-guided GP seeds evolution with LLM-generated programs and uses structural-similarity objectives;
- contract-based program synthesis and SMT/abstract-interpretation-guided search cover behavioral preconditions/postconditions.

The specific application to stateful tool-use Agent policies may be useful engineering, but application specificity is not an algorithmic novelty. No new operator is admitted.

## 2. Four different notions that must not be conflated

| Notion | What it guarantees | What it does not guarantee | Prior mechanism |
|---|---|---|---|
| Syntax/grammar validity | Candidate is in the allowed language/AST grammar | It compiles, obeys runtime preconditions, or solves the task | Grammar-guided GP; Whigham 1995; MaOG3P/SBMaOG3P |
| Type validity | Function arguments and return values satisfy a type system | State-dependent action legality, temporal invariants, or goal achievement | Strongly Typed GP; Montana 1995 |
| Behavioral/semantic preservation | A transformation preserves specified semantics under proof/model assumptions | The policy is better at the task or satisfies unmodeled requirements | Proof-guided genetic improvement; formal synthesis |
| Task correctness/runtime contract satisfaction | Executed policy meets a specified contract or task oracle on tested executions | Generalization beyond tested states/tasks unless separately established | GenProg test-suite fitness; PSyCo/SNES; model checking; contract synthesis |

A successful design must state which property its operator guarantees and which properties remain empirical.

## 3. Primary-work matrix

| Work | Representation | Exact mechanism | Feedback/constraints | Novelty consequence |
|---|---|---|---|---|
| Montana (1995), Strongly Typed Genetic Programming | Typed program trees with explicit and generic types | Modify GP generation and genetic operators so function arguments and return values obey type constraints | Type system constrains legal trees and variation | Type-preserving mutation/crossover is classic GP, not a new Agent-specific operator. |
| Whigham (1995), Grammatically-Based Genetic Programming | Derivation trees under context-free grammar | Grammar defines initial language and directs crossover/mutation; grammar bias can evolve | Only grammatical programs are generated/modified | Grammar-constrained policy programs are not new by themselves. |
| A methodology for processing problem constraints in GP (1996) | GP trees with problem-specific typing and semantic constraints | Transform user constraints to a normal form and use them to restrict the represented search space | Can exclude invalid/redundant/undesired subspaces | Use of action contracts to restrict GP's search space needs a mechanism beyond ordinary constraint-aware GP. |
| Weimer et al. (GECCO/ICSE 2009); Le Goues et al. (TSE 2012), GenProg | Program variants/source-code patches | Genetic programming with delete, swap, insert; edits biased to execution-path locations; variants cross back to original program; post-search delta debugging minimizes repair | Positive/negative test cases encode required behavior and target defect; non-compiling/time-out programs receive zero fitness | Test-guided, execution-local mutation and preserve-original-functionality are already established. |
| Kocsis & Swan (2018), Genetic Programming + Proof Search = Automatic Improvement | Algebraic data types/program fragments | Replace ordinary mutation with deterministic proof search that yields semantics-preserving transformations | Proof search certifies a class of transformations | A semantics-preserving operator must differ materially from proof-guided program improvement, not merely claim safer edits. |
| Tao et al. (2024; journal version 2025), MaOG3P/SBMaOG3P | Grammar-guided programs seeded from LLM code | Map an LLM-generated candidate into a grammar-compliant program; use many-objective similarity measures plus I/O error to guide evolution | BNF grammar guarantees syntactic conformity; input/output fitness guides search | Directly covers LLM-seeded grammar-guided EA, many-objective similarity to LLM candidates, and grammar compliance. |
| Gulwani, Polozov & Singh (2017), Program Synthesis | Programs satisfying user intent/specifications | Enumerative search, constraint solving, stochastic search and deduction-based synthesis | Specifications, examples, or logical constraints | The space of synthesis approaches is broader than GP; compare non-EC solvers. |
| Dimovski (2026), Imperative-program synthesis from assumptions and assertions by abstract analysis and SMT mutations | Program templates with statement/expression holes | Statement-directed enumeration; abstract interpretation prunes; incremental SMT-based expression mutations | Assumptions/assertions and static analysis | Behavioral pre/postcondition-guided variation and SMT mutations are active, very recent work. |
| Belzner & Wirsing (2021), PSyCo/SNES | Neural policy parameters | Evolution strategies update policy; Bayesian model checking adjusts reward/cost Lagrangian based on confidence in satisfying probabilistic constraints | Independent probabilistic safety requirements and verification | Safety constraints in evolutionary policy search are already studied. |
| Heck et al. (AAAI 2026), constrained/robust policy synthesis | Policies constrained by structure/representation requirements | SMT plus probabilistic model checking | Formal specifications and robust MDP analysis | Formal synthesis is a strong non-EC comparator and may be preferable when contracts are decidable. |

## 4. What a tool-use Agent policy adds — and what it does not

A policy may be represented as a typed program or finite-state controller whose inputs include symbolic tool-world observations and internal state, and whose outputs are actions such as read, calculate, write, verify, retry, or stop. Each action may have preconditions and effects.

This domain introduces useful distinctions:
- static type rule: the action argument has the right shape;
- state-dependent precondition: the action is legal in the current environment state;
- postcondition/effect: the state transition after the action is valid;
- episode goal: the final task state is correct;
- generalization: the policy succeeds on unseen task families and states.

These are not automatically new algorithmic mechanisms. Enforcing action preconditions in the runtime can be a safety wrapper. Filtering invalid candidates after mutation is a rejection/repair strategy. Constraining the grammar is grammar-guided GP. Test-driven evolution is program repair. A new contribution would require a precisely specified evolutionary operator/selection rule that exploits state-dependent contracts in a way not equivalent to these existing approaches.

## 5. Candidate checks

| Candidate phrasing | Verdict | Reason |
|---|---|---|
| Use strongly typed GP for Agent tool policies | NO_GO | Directly covered by STGP and policy GP. |
| Use a grammar to ensure valid tool calls | NO_GO | Grammar-guided GP and grammar-constrained program synthesis. |
| Reject/repair invalid mutations using action preconditions | NO_GO_AS_STATED | Generic constraint handling, filtering/repair, and program synthesis; no distinct update rule specified. |
| Use execution failures to target edits | NO_GO_GENERIC | GenProg execution-path-localized mutation, MLES failure-guided policy evolution, and HarnessEvolve reference-trajectory diagnosis. |
| Use tests/contracts as fitness | NO_GO | GenProg, program synthesis, safe policy synthesis; also risks overfitting the visible test set. |
| Use proof search to preserve policy semantics | NO_GO_GENERIC | Kocsis & Swan 2018; formal methods and SMT synthesis. |
| Use LLM seeds plus grammar-GP and multi-objective similarity | NO_GO | MaOG3P/SBMaOG3P (2024/2025). |
| New contract-conditioned variation using temporal action effects | UNRESOLVED, NOT ADMITTED | Potentially more specific, but no exact rule or proof of a mechanism-level gap was established. |

## 6. Conclusion

The generic typed/contract-aware GP route is closed as a new-method claim. The narrower temporal-effect-conditioned operator is not a candidate yet: no executable rule, nearest-neighbor comparison, or falsifiable advantage has been demonstrated.

This phase is not a project-wide NO-GO. It rejects only the current family of generic validity/contract-aware variation claims. The next audit returns to the charter's central unresolved hypothesis: whether an explicit evolutionary-control policy discovered on a source optimization domain can transfer to the structurally different Agent-policy search domain under a fixed state/action mapping.

## 7. References

1. Montana, D. J. (1995). Strongly Typed Genetic Programming. Evolutionary Computation, 3(2), 199–230. https://doi.org/10.1162/evco.1995.3.2.199
2. Whigham, P. A. (1995). Grammatically-Based Genetic Programming. Proceedings of the Workshop on Genetic Programming: From Theory to Real-World Applications, 33–41. https://gpbib.cs.ucl.ac.uk/gp-html/whigham_1995_GBGP.html
3. A Methodology for Processing Problem Constraints in Genetic Programming. (1996). Computers & Mathematics with Applications, 32(8), 97–113. https://doi.org/10.1016/S0898-1221(96)00170-8
4. Weimer, W., Nguyen, T. V., Le Goues, C., & Forrest, S. (2009). Automatically Finding Patches Using Genetic Programming. ICSE 2009, 364–374. https://doi.org/10.1109/ICSE.2009.5070536
5. Le Goues, C., Nguyen, T. V., Forrest, S., & Weimer, W. (2012). GenProg: A Generic Method for Automatic Software Repair. IEEE Transactions on Software Engineering, 38(1), 54–72. https://doi.org/10.1109/TSE.2011.104
6. Kocsis, Z. A., & Swan, J. (2018). Genetic Programming + Proof Search = Automatic Improvement. Journal of Automated Reasoning, 60, 157–176. https://doi.org/10.1007/s10817-017-9409-5
7. Tao, N., Ventresque, A., Nallur, V., & Saber, T. (2024). Enhancing Program Synthesis with Large-Objective Grammar-Guided Genetic Programming. Algorithms, 17(7), 287. https://doi.org/10.3390/a17070287. Journal version (2025): Computer Standards & Interfaces, 92, 103938. https://doi.org/10.1016/j.csi.2024.103938
8. Gulwani, S., Polozov, A., & Singh, R. (2017). Program Synthesis. Foundations and Trends in Programming Languages, 4(1–2). https://www.microsoft.com/en-us/research/publication/program-synthesis/
9. Dimovski, A. S. (2026). Imperative-program synthesis from assumptions and assertions by abstract analysis and SMT mutations. Computer Languages, Systems & Structures. https://doi.org/10.1016/j.cola.2026.101395
10. Belzner, L., & Wirsing, M. (2021). Synthesizing Safe Policies under Probabilistic Constraints with Reinforcement Learning and Bayesian Model Checking. Science of Computer Programming, 206, 102620. https://doi.org/10.1016/j.scico.2021.102620
11. Heck, L., Macák, F., Češka, M., & Junges, S. (2026). Constrained and Robust Policy Synthesis with Satisfiability-Modulo-Probabilistic-Model-Checking. AAAI 2026, 36253–36261. https://doi.org/10.1609/aaai.v40i43.40944
12. Sobania, D., Schweim, D., & Rothlauf, F. (2023). A Comprehensive Survey on Program Synthesis with Evolutionary Algorithms. IEEE Transactions on Evolutionary Computation, 27(1), 82–97. https://doi.org/10.1109/TEVC.2022.3162324
