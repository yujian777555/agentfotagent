# Phase-1A-9 Decision

## 决策

**NO_GO_PHASE1A_ALGORITHM_DISCOVERY**

跨算法家族筛选中，所有候选被已有方法覆盖（`ALREADY_COVERED`）。没有候选通过创新性审查（Gate 2）。

## 停止条件核对

| 条件 | 状态 |
|---|---|
| 没有候选通过创新性审查 | ✅ **触发停止** |
| 所有候选均被已有方法覆盖 | ✅ **触发停止** |
| 没有可靠的原始论文证据 | ❌（有证据，但指向已有方法） |
| 现有环境无法提供可信基线 | ❌（CMA-ES 可运行） |
| 无法设计独立归因实验 | ❌（可设计，但无新机制可归因） |

## 六个候选的最终去向

| 候选 | 家族 | 判定 | 关键覆盖方法 |
|---|---|---|---|
| A1 C 矩阵特征值裁剪 | CMA-ES | ALREADY_COVERED | `cma.conditioncov_alleviate` |
| A2 CSA 步长保护 | CMA-ES | ALREADY_COVERED | CSA 改进文献 |
| B1 多样性锦标赛选择 | GA | ALREADY_COVERED | fitness sharing / crowding |
| B2 自适应重组率 | GA | ALREADY_COVERED | jGA / AGA |
| A2'（文献审计阶段） | — | ALREADY_COVERED | sep-CMA-ES / VD-CMA |
| B2'（文献审计阶段） | — | ALREADY_COVERED | 自适应参数控制 |

## 建议

**暂停当前算法发现路线。**

Phase-1A-7（DE 机制）→ NO_GO
Phase-1A-8（archive×boundary）→ NO_GO
Phase-1A-9（跨家族）→ NO_GO

三条独立路线均未产出通过创新性审查的机制。继续在同一框架内寻找新算法的边际收益极低。

### 可考虑的替代方向

1. **系统性 Agent 辅助算法设计实证研究**：不以"发现新算法"为目标，而是量化 Agent 在算法设计各环节（问题识别、方案生成、消融设计）的实际贡献。
2. **重新确定研究问题**：从"发现新演化机制"转向"理解演化算法的失败模式"——利用已积累的 100+ 条诊断轨迹。
3. **复现研究**：选择 2-3 篇高质量 DE/CMA-ES 论文做独立复现，产出可核验的 baseline 资源。

## 元数据

| 项 | 值 |
|---|---|
| 分支 | `phase1a-phase9-cross-family-pivot-audit` |
| 基线 SHA | `354b7f9` |
| LLM 请求 | 0 |
| 运行数 | 0（Stage D 未启动） |
| validation/test 访问 | 无 |
| main 修改 | 无 |
