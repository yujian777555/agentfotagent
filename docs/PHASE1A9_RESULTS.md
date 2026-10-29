# Phase-1A-9 Results

## Stage D 基线复现：未执行

原因：0 个候选通过四道门（Gate 2 全部失败）。按停止规则，不启动 9 次基线运行。

## 实际执行

| 阶段 | 内容 | 结果 |
|---|---|---|
| Stage A | 跨家族文献审计（6 候选） | 仅 1 个存活至 Stage B |
| Stage B | CMAES 环境核验 | 可运行但 FE/语义有偏差；A1 被覆盖 |
| Stage C | 四道门判定 | 0 个通过 |
| Stage D | 9-run 基线复现 | **未执行** |

## LLM 请求

**0**。

## 环境核验发现（供后续参考）

1. **MetaBox CMAES 优化 benchmark_cost**（减去 optimum），与 L-SHADE 的 raw_objective 语义不同。
2. **`result['fes']` 不可信**（cma 包内部计数 950 vs 实际 1000）。必须用独立 FE 计数器。
3. **`cma` 包 v4.5.0 已内置 `conditioncov_alleviate`**（C 矩阵病态缓解，阈值 1e8/1e12）。
4. **`cma` 种子可通过 `seed` 选项控制**，但 MetaBox 包装层未传递。
5. **MetaBox 无纯 GA 实现**（MFEA 多任务，GLPSO 是 PSO）。
