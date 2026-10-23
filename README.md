# Agent-for-Agent：Agent 与演化计算的双向赋能研究

本仓库维护以**演化计算（EC）为方法核心、LLM Agent 自进化为研究对象**的长期研究项目。

## 当前研究判断
- 通用的“Agent 观察轨迹并改进算子”与既有 LLM4EO、LAOS、EoH、LLaMEA、AwesomeDE/LMCOEA 高度重叠。
- 通用的递归/双向自我改进与 Hyperagents、HGM、CoCoEvolve、RSI-Router 等高度重叠。
- 当前唯一保留的候选问题是：把数值优化域中学到的**同一个明确控制对象**迁移到结构不同的 Agent-genotype 搜索空间，并通过强基线、打乱映射负对照和独立任务证明增量收益。该假设新颖性风险高，尚未确认。
- 不把有限预算分配作为核心创新；MetaBox 是基础设施，不是创新点。
- 不进行真实 LLM API 实验，除非实验范围和调用/Token/费用上限获得单独明确授权。

## 维护入口
- [项目章程](docs/PROJECT_CHARTER.md)
- [相关工作机制审查](docs/FULLTEXT_AUDIT_2026-10-23.md)
- [相关工作矩阵](docs/LITERATURE_MATRIX.md)
- [前置资产对账](docs/RECONCILIATION.md)
- [研究决策记录](docs/RESEARCH_DECISIONS.md)
- [当前计划](planner/latest_plan.md)
- [机器可读状态](status.json)

当前阶段为 P0-R2：最近邻论文碰撞审查与跨表示迁移对象定义。当前仓库尚无研究算法实现；上游报告不等同于本仓库独立复现。
