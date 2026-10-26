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
- 当前先搭建环境骨架并通过工程门禁；mock 测试不算 Agent 能力实验，未授权前不调用真实 API。

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

当前阶段为 P0-R3：建立本仓库自有的 Agent Evolution Sandbox（AES）实验环境。LAOS 的官方摘要已核验但正文/代码仍未取得；LMCOEA 的论文方法片段与链接代码已静态审查但未复现。迁移对象仍未定义；当前先实现可审计的环境骨架，不启动科学实验。当前仓库尚无研究算法实现；外部项目报告不等同于本仓库独立复现。
