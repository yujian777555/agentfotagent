# Agent-for-Agent：Agent 与演化计算的双向赋能研究

本仓库维护以**演化计算（EC）为方法核心、LLM Agent 自进化为研究对象**的长期研究项目。

## 当前研究判断
- 通用的“Agent 观察轨迹并改进算子”与既有 LLM4EO、LAOS、EoH、LLaMEA、AwesomeDE/LMCOEA 高度重叠。
- 通用的递归/双向自我改进与 Hyperagents、HGM、CoCoEvolve、RSI-Router 等高度重叠。
- 当前核心研究假设仍是：先在 MetaBox 数值优化域验证 Agent 辅助的演化控制，再将明确的控制对象应用于本项目自己的 Agent 自进化环境。跨域迁移及双向反馈均未证实，必须接受强基线和否证实验。
- 不把有限预算分配作为核心创新；MetaBox 是基础设施，不是创新点。
- 不进行真实 LLM API 实验，除非实验范围和调用/Token/费用上限获得单独明确授权。

## 实验环境原则
- agentfotagent 必须拥有自己的 Agent Evolution Sandbox（AES）目标域环境、基因型/表型运行时、评价器、任务划分、实验协议和结果记录。
- MetaBox-v2 只作为数值优化源域的标准化基础设施，不是论文贡献。
- NeuroEvoScientist、EvoPareto-Agent 是独立项目，仅可只读参考，不作为本项目的实验环境、代码依赖或结果来源。
- AES 工程骨架已通过 Phase-0 R4 engineering gate，但尚无 Agent 能力或科学有效性结论；历史 mock pilot 已饱和，不能作为科学证据。当前方法发现路线处于暂停状态，只有在出现可复现的具体失败模式且通过机制级新颖性审查后，才考虑重新开放实验。

## 维护入口
- [项目章程](docs/PROJECT_CHARTER.md)
- [自有实验环境规范](docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md)
- [相关工作机制审查](docs/FULLTEXT_AUDIT_2026-10-23.md)
- [LAOS / LMCOEA 机制审计（2026-10-26）](docs/LAOS_LMCOEA_MECHANISM_AUDIT_2026-10-26.md)
- [相关工作矩阵](docs/LITERATURE_MATRIX.md)
- [前置资产对账](docs/RECONCILIATION.md)
- [研究决策记录](docs/RESEARCH_DECISIONS.md)
- [当前计划](planner/latest_plan.md)
- [机器可读状态](status.json)

当前研究状态（2026-10-29）：Phase-1A-18 的暂停决定仍然有效。根据补充的历史会话，下一步优先审计“外部工具/技能/专家 Agent 集合扩张后，旧任务为何停止调用原本必需的能力”这一具体问题。EvoHarnessBench 提供了可测量的 delegation-drift 证据，但 CPE、EVOTOOL、AEL、HarnessForge 等已有工作构成重要重叠，尚无新 EC 机制成立。EVOTOOL blame-to-intervention mismatch 保留为次要线索。当前只做机制级文献/源码审计；不创建 Phase-1A-19，不启动 API、MetaBox/AES 科学实验、GPU 或 held-out 测试。详见 [Harness 扩张与能力保持审计](docs/PHASE1A18_HARNESS_EXPANSION_RETENTION_AUDIT.md)、[EVOTOOL 次要线索](docs/PHASE1A18_EVOTOOL_BLAME_ACTIONABILITY_AUDIT.md)、[当前计划](planner/latest_plan.md) 与 [机器可读状态](status.json)。
