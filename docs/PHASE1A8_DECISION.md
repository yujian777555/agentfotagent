# Phase-1A-8 Decision

## 决策

**NO_GO_INTERACTION**

Archive × Boundary Repair 交互效应在 4 个 BBOB 函数、5 个种子的 2×2 配对实验中**未呈现可复核的一致方向**。不进入 Agent 机制设计阶段。

## 停止规则核对

| 条件 | 状态 | 证据 |
|---|---|---|
| 文献审计未发现完全相同的机制 | ✅ | 6 篇论文审计，未发现 archive×boundary 交互被实质覆盖 |
| Stage A 事件数量充足 | ✅ | OOB 率 23.7%，archive 采样率 51.2% |
| A0 与标准实现一致 | ✅ | 7 项测试逐位验证 |
| FE / 轨迹完整性 | ✅ | 100 runs（20+80）FE 全部精确 |
| archive × repair 有可复核的交互证据 | ❌ | 交互 W-L-T 在所有函数上为 2-3 或更差 |
| 交互现象有明确算法解释 | ❌ | 观测差异可由噪声/异常值解释 |
| 至少两个函数方向一致 | ❌ | 0 个函数方向一致 |

满足任一 NO_GO 条件即停止。本阶段满足 3 项。

## 已确认的观测事实（非新算法主张）

1. **修复 trial 成功率系统性低于未修复 trial**（全函数全种子一致）
2. **修复位移方向与搜索方向相反**（cosine ≈ -0.4 至 -0.65）
3. **OOB 事件集中在搜索早期**（Q1 占比 >75%）
4. **archive 启用使 OOB 率略升**（0.237 vs 0.176），但幅度小

这些是 Stage A 的可复核观测，可作为后续研究的证据基础。

## 未启动 Agent 阶段

按协议，`CONDITIONAL_GO_FOR_AGENT_HYPOTHESIS` 的 5 个条件中有 3 个不满足。不申请 `deepseek-flash` 预算。

## 元数据

| 项 | 值 |
|---|---|
| 分支 | `phase1a-phase8-archive-boundary-interaction` |
| 基线 SHA | `5d945dc` |
| LLM 请求 | 0 |
| Stage A 运行 | 20/20，FE 精确 |
| Stage B 运行 | 80/80，FE 精确 |
| validation/test 访问 | 无 |
| main 修改 | 无 |
