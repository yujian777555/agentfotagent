# Latest Plan — P0-R1: Remote Reconciliation and Hypothesis Audit

- Date: 2026-10-23
- Repository baseline: `main @ f7ff93d00c95a89e0232058c7cfd761b726fc75e`
- Mode: planning / evidence audit
- Status: IN_PROGRESS; no implementation or real API experiment authorized by this plan
- Audit working checkpoint before this plan update: read-only baseline was `main @ e36c79edf31712ff68c7569354a682f5f7f56da8`.

## Goal

把当前新建的 GitHub 远端与先前对话中报告的本地研究状态对账，并明确第一篇论文最关键的可否证假设。不得把历史描述直接当作当前远端代码或复现实验结果。

## Audit progress (2026-10-23)

Completed in the current planning-only pass:
- Verified initial commit `f7ff93d00c95a89e0232058c7cfd761b726fc75e` and governance HEAD `e36c79edf31712ff68c7569354a682f5f7f56da8`.
- Confirmed the current `agentfotagent` remote has no source tree, tests, Phase 0 simulator, or experiment outputs.
- Reviewed related repositories read-only: EvoController (prior action-attribution negative evidence), EvoPareto-Agent (code substrate but latest report says real HTTP=0), and llm-agent-rsi-r12-audit (offline/synthetic only).
- Added `docs/RECONCILIATION.md`, `docs/LITERATURE_MATRIX.md`, and `plans/phase0_hypothesis_audit.md`.
- Identified LLM4EO, LAOS, LMCOEA, and AwesomeDE as direct prior art for LLM-based operator selection, online operator evolution, and MetaBBO-assisted update-rule generation. H1 alone is not a sufficient novelty claim. H2 cross-domain transfer remains the main discriminative hypothesis.
- Inspected MetaBox-v2 official `v2.0.0` README/API docs read-only; not installed or executed.

Still unresolved:
- The reported local `d46a76d` Phase 0 source and 46/46 raw test output have not been located in the checked remote/Library sources. This is not a claim that they do not exist on the user's local disk.
- Full method/code audits of LAOS, LMCOEA, AwesomeDE, ARTEMIS, EvoAgent, AIDE², MASS, GEPA, DGM, HGM, and Hyperagents remain pending; abstracts/selected method sections are not a completed novelty audit.
- No MetaBox benchmark, simulator efficacy experiment, or real LLM API experiment has been run in this pass.

## Task 1 — Reconcile prior artifacts

1. 检查本地项目是否确实包含先前报告的 Phase 0 baseline/simulator。
2. 若存在，记录准确路径、HEAD、工作区状态、测试命令和原始测试输出；不要直接覆盖或重写。
3. 将可核验文件按最小必要范围导入本仓库，并在提交说明中注明来源和复核方式。
4. 对话中曾报告：本地 HEAD `d46a76d`、工作区 clean、Phase 0 baseline/simulator、46/46 tests passed；这些数字目前只属于历史上下文，需重新验证。
5. 对话中曾提到 NSGA-III、PEEM、PPEC 和 155 轮演化的探索统计；先找到原始日志/代码，确认其定义和来源，禁止直接作为论文证据。

**验收：** 形成一份可追溯的 reconciliation 记录；每项信息标记为 VERIFIED、REPRODUCED、HISTORICAL-UNVERIFIED 或 NOT-FOUND。

## Task 2 — Audit H1/H2/H3

- H1：Agent 诊断是否能产生超越简单参数修改/代码重写的有效演化机制？
- H2：在 MetaBox 数值优化中发现的高层控制策略，是否能迁移到未见过的 Agent RSI 任务？
- H3：Agent 进化反馈是否能在单向迁移之上产生额外收益？

对每项假设写明：操作化定义、比较基线、主指标、独立测试划分、随机种子、否证条件和最小可接受效应。不要预设假设为真。

## Task 3 — Literature overlap matrix

逐项对照 EoH、LLaMEA、LMCOEA、MetaBox-v2、EvoAgent、ARTEMIS、AIDE²、MASS。对每篇工作至少记录：核心问题、方法机制、优化对象、反馈/选择机制、基准、主要结果、与本项目重叠、尚未解决的差异。必须查看论文正文或官方材料，不以名称或摘要单独下结论。

## Task 4 — Define the smallest discriminative experiment

提出最小实验，优先区分“跨域控制知识真的可迁移”与“任何自适应搜索都能产生类似效果”。实验至少包含：
- 原始演化控制基线；
- 经典自适应演化基线；
- Agent 辅助发现但不迁移；
- 迁移控制策略；
- 若前四组支持迁移，再加入反馈消融。

所有组使用相同或明确可比的任务、种子和评估协议。测试集保持独立，不参与策略搜索。

## Hard constraints

- 不新增 NSGA-III 实现，直到 Phase 0/H1-H3 审计通过。
- 不发起真实 LLM API 调用，除非用户另行明确批准实验范围与调用/Token/费用上限。
- 不把有限预算分配设为核心创新。
- 不把 MetaBox 本身当成论文贡献。
- 不宣称尚未复现的历史结果。
- 每次执行先记录基线 commit；提交必须说明变更、验证命令、测试结果和未解决问题。

## Deliverables

1. `docs/RECONCILIATION.md`：本地/远端证据对账。
2. `docs/LITERATURE_MATRIX.md`：相关工作机制级对照与引用。
3. `plans/phase0_hypothesis_audit.md`：H1/H2/H3 的操作化定义和实验协议。
4. 更新 `status.json`，只记录已核验的事实。

## Exit gate

只有当当前远端来源明确、Phase 0 可以复现、相关工作对照已完成、假设有可执行且可否证的实验协议后，才进入 MetaBox 算法发现的实现阶段。若 H2 的迁移假设在最小实验中不成立，应先调整研究问题，而不是自动增加双向闭环复杂度。


## Follow-up full-text audit — 2026-10-23

### Newly established evidence

- Full paper reviewed: EoH, LLM4EO, AwesomeDE, ARTEMIS, EvoAgent, GEPA, DGM, HGM, Hyperagents, AIDE², MASS, Harmony Harness, RSI-Router and CoCoEvolve.
- Official source code inspected: EoH and LLaMEA; LLaMEA supports algorithm-level generation/evolution, mutation/crossover prompts, adaptive mutation, feature guidance, parent-selection options, multi-objective Pareto archives, novelty/niching and optional HPO. LLaMEA-HPO separately offloads numeric parameter tuning to SMAC.
- LAOS full text/code and the LMCOEA publisher PDF/official code remain blocked in this pass. The official GECCO abstract provides LAOS state/credit/replay details; ScienceDirect indexed excerpts expose LMCOEA's bi-level MetaBBO-EL, RTO²H and 18-problem setup, but neither is a complete paper/code audit.
- The broad H1 and H3 narratives are directly covered by prior art. H2 remains the only current candidate, but its novelty risk is high because Harmony Harness and Hyperagents already report transferable mechanisms across benchmarks/domains.

### Next actions

1. Continue seeking author manuscripts or official implementations for LAOS and LMCOEA; do not invent details beyond the available abstract.
2. Write an explicit mechanism-level contrast between the proposed transfer object and Harmony Harness, Hyperagents, LMCOEA/AwesomeDE, GEPA and CoCoEvolve.
3. Decide whether the transferable object is a policy, executable control rules or a learned representation. Define a nontrivial state/action alignment method rather than a thin adapter.
4. Verify the downstream Agent phenotype and evaluator, preferably using a real random-search arm and strong target-domain controller.
5. If no mechanism-level difference survives this audit, revise the idea before coding. Do not proceed merely because the two-stage narrative sounds attractive.
