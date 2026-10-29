# Phase-1A-14 Candidate Shortlist — NO-GO

- Date: 2026-10-29
- Branch: phase1a-phase11-unified-agent-ec-roadmap
- Evidence matrix: docs/PHASE1A14_PRIOR_WORK_MATRIX.md
- Decision: **NO_GO_CANDIDATE_SHORTLIST**.
- This is not a project-level NO-GO.

## Screened candidate families

| Candidate | Nearest direct prior art | Verdict |
|---|---|---|
| Failure diagnosis + targeted Agent-module mutation + EA selection | EvoTool; GSME; PRISM; TTHE/Evoflux | NO_GO_GENERIC |
| Semantic-local mutation / trust-region policy evolution | ELMER; SeDev; LLM-optimizer trajectory analysis; AdaEvolve | NO_GO_AS_STATED |
| Semantic pathology archive / quality-diversity | GSME; DGM; DEI; EvolRepair | NO_GO_GENERIC |
| Paired gene interaction / linkage-aware recombination | Differential Grouping; fitness-based linkage learning; GOMEA/CGOMEA; AgentSwift | NO_GO_FCLE |
| Adaptive LLM-EA controller / mutation intensity / stagnation response | AdaEvolve; LAOS; LMCOEA; prior Phase-1A audits | NO_GO_GENERIC |
| Query-conditioned Agent architecture or workflow selection | MaAS; AgentSwift; SWIFT; Learn-to-Configure | NO_GO_GENERIC |
| Harness optimizer that improves its own procedures | VERSE; AgenticEvolve; HSI; Hyperagents audit | NO_GO_GENERIC |
| Verifier-free / weak-feedback Agent evolution | OpenSkill; UCoE; RHO; DemoEvolve; GSME's verifier-gate design | NO_GO_AS_STATED |
| Runtime interface / harness adaptation | Life-Harness; EvoHarness-RL; GSME; VERSE | NO_GO_GENERIC |
| Heterogeneous LLMs as mutation operators in QD search | DEI | NO_GO_GENERIC |
| Robustness/generalization as sole novelty | GSME; MaAS; Life-Harness; SWIFT and standard robust optimization | NOT_A_METHOD |
| New task benchmark / more difficult tasks as sole novelty | ToolMaze and broad Agent benchmark literature | NOT_A_METHOD |
| Better statistical gating / activation tracking / fitness tie-breakers alone | GSME and standard experimental design | NOT_A_METHOD |

## Why no candidate was promoted

The screened ideas are reasonable mechanisms or useful engineering practices, but each currently lacks a defensible algorithmic distinction from close prior work. No source code, benchmark result or novel acronym can compensate for that missing distinction.

No candidate should be implemented or tested as a scientific claim on the present evidence. The next phase must formulate a narrower problem with a specific EC update/selection rule before generating another candidate list.
