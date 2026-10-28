# Phase-1A-6 Decision

## 决策

**证据基础修复完成 — CONDITIONAL GO（仅限"实验基础设施可信"这一结论）**

基线重建成功（36/36，FE 精确），说明：
1. 现在存在一个语义清晰、经独立测试验证的 **标准 L-SHADE 重实现**；
2. 函数评价、optimum、benchmark_cost / regret 的关系已核实并分离记录；
3. 函数身份与 train split 可核验。

**但这不构成任何新算法有效的证据。** Phase-1A-6 的全部产出是基础设施纠错与基线重建，不是性能主张。

## 门禁核对

| 门禁 | 状态 | 证据 |
|---|---|---|
| 标准实现独立存在 | ✅ | `lshade_canonical.py`（`not official code` 明示） |
| 与论文公式一致性 | ✅ | N(t)/Cauchy F/记忆更新/索引排除 单元测试锁死 |
| 独立测试 ≥ 10 项 | ✅ | 47 项全过；全量 356 项 exit 0 |
| 函数评价语义核实 | ✅ | `eval` 返回 raw_objective；optimum 非总是下界（F20） |
| regret 仅在验证后使用 | ✅ | canonical 分离三字段；F20 走 benchmark_cost |
| FE 精确 | ✅ | 36/36 `fes == indep == 5000` |
| 函数身份 | ✅ | F1/F6/F24 类名核验；运行时逐条比对 |
| train split 冻结 | ✅ | `SPLIT_V2_TRAIN` + `manifest_hash` |
| 基线只跑一次、无干预 | ✅ | 36 runs，0 LLM，无 N+I/触发/重启 |
| 历史结果不覆盖 | ✅ | 4R3/5 manifest 原样保留；重分类文档独立成文 |

## 已发现的实现差异（摘要）

1. **N(t) 公式非标准**（高）：旧实现更早触及 N_min。
2. **F 采样用 Normal 而非 Cauchy**（高）：尾部行为不同。
3. **F≤0 裁剪而非重采样**（中）。
4. **r1 可等于 r2**（低）。
5. **`regret` 命名错误**（阻断级语义）：历史字段实为 benchmark_cost；F20 出现负值。

## 历史结论分类（详见 PHASE1A6_HISTORICAL_EVIDENCE_REVIEW.md）

- **仍可信**：LLM 能力边界、质量残差 credit、bucket-UCB 恒等、matched-random 方法论、FE/身份基础设施。
- **仅对旧实现有效**：4R3 N+I W-L-T、4R2 state-vs-matched 数值、4R 因果归因、5 的 adaptive-N 数值阈值。
- **已废弃解释**："标准 L-SHADE 线性 N 与进度脱钩是算法缺陷"（脱钩来自旧公式）。
- **已修正语义**：F20 "负 regret" → optimum 非严格下界。

## 下一步（本阶段结束后）

基于 **可信轨迹**（`results/phase1a6/trajectories/`）与现有文献，选择下一种值得研究的演化机制。

约束：
1. 不预先指定新算法；
2. **不得**再次启动已关闭的重启（N+I）或自适应种群缩减主张；
3. 与标准 L-SHADE 的任何比较必须以 `lshade_canonical.py` 为唯一对照臂；
4. 如动用 LLM，沿用 6-request 预算（3 propose + 3 critique），hand-design 与 random-change 对照先行。

## 停止规则执行情况

本阶段 **未** 触发停止条件：
- 标准实现 ✅ 可核验
- 函数身份 ✅ 可核验
- 评价语义 ✅ 已核实
- FE 计数 ✅ 一致

若上述任一项失败，将立即停止而不启动 36 runs — 实际执行顺序为：审计 → 实现 → 测试通过 → 冻结配置 → 运行。

## 元数据

| 项 | 值 |
|---|---|
| 分支 | `phase1a-phase6-lshade-canonical-audit` |
| 基线 SHA | `a4a5897e6f555d0471284216a16b876c751a3edd` |
| LLM 调用 | 0 |
| validation/test split 访问 | 无 |
| 历史结果覆盖 | 无 |
