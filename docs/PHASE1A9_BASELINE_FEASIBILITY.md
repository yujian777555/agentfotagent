# Phase-1A-9 Baseline Feasibility

## 1. MetaBox 安装版本与来源

| 项 | 值 |
|---|---|
| 包名 | `metaevobox` 2.0.2 |
| 安装路径 | `D:\metabox-env\Lib\site-packages\metaevobox\` |
| CMA-ES 依赖 | `cma` 包 v4.5.0 |
| 来源 | PyPI（git SHA `5565a281`） |

## 2. 算法可用性

| 算法 | MetaBox 类 | 单目标 BBOB 可用 | 备注 |
|---|---|---|---|
| CMA-ES | `CMAES` | ✅ | 包装 `cma` 4.5.0 |
| SHADE | `SHADE` | ✅ | DE 家族 |
| DE | `DE` | ✅ | DE 家族 |
| Random Search | `Random_search` | ✅ | 仅对照 |
| MFEA | `MFEA` | ❌ | 多任务，需 `mto_tasks` |
| GLPSO | `GLPSO` | ❌ | PSO（已排除） |
| 纯 GA | **无** | ❌ | 需从头实现 |

## 3. CMAES 实现核验

### 3.1 初始化

```python
config.NP = 50  # MetaBox 强制设置
es = cma.CMAEvolutionStrategy(np.ones(dim), 0.3, {
    'popsize': NP, 'bounds': [0, 1], 'maxfevals': maxFEs, ...
})
```
初始均值为 `np.ones(dim)`（归一化空间中点），σ0 = 0.3。

### 3.2 目标函数调用与指标语义 — **偏差发现**

```python
def problem_eval(x):
    x = np.clip(x, 0, 1)
    x = x * (problem.ub - problem.lb) + problem.lb
    if problem.optimum is None:
        fitness = problem.eval(x)
    else:
        fitness = problem.eval(x) - problem.optimum  # ⚠️ 减去 optimum
    return fitness
```

**MetaBox CMAES 优化的是 `benchmark_cost`（raw − optimum），不是 raw objective。**
与 L-SHADE（优化 raw objective）**语义不同**。

影响：
- F20（optimum 非下界）：benchmark_cost 可为负，但 CMA-ES 仍正确最小化
- 直接对比 L-SHADE 与 CMA-ES 的 "best_raw" 需各自减去/加回 optimum

### 3.3 FE 计数 — **偏差发现**

| 计数方式 | 值 | 问题 |
|---|---|---|
| `result['fes']`（`es.result[3]`） | 950（1000 FE 预算时） | cma 包内部计数 |
| MetaBox 自身 `__FEs` | NP × generations | 不等于实际 eval 次数 |
| **独立计数** | **1000** | **正确** |

`result['fes']` **不可信**。必须使用独立 FE 计数器。

### 3.4 随机种子

`cma` 包支持 `seed` 参数，同种子可复现。但 MetaBox CMAES **未传递外部 seed** 到 cma 选项——需要在使用时手动构造 cma options。

### 3.5 C 矩阵访问与修改

- `es.C` 可读可写 ✅
- `es.D`（特征值）可读 ✅
- `conditioncov_alleviate` **已内置**：`[1e8, 1e12]` — 自动缓解病态

## 4. 候选 A1（特征值裁剪）可行性

| 检查项 | 结果 |
|---|---|
| 基线可运行 | ✅ |
| FE 可精确 | ✅（需独立计数） |
| 种子可控 | ✅（需手动传 `seed` 到 cma） |
| 指标可解释 | ✅（benchmark_cost 语义） |
| C 矩阵可注入修改 | ✅ |
| **最近邻已有相同机制** | **❌ `conditioncov_alleviate` 已内置** |

## 5. GA 家族可行性

- **无纯 GA 实现**。需从头实现（~300-400 行）。
- 实现 + 独立验证成本高，且文献审计显示所有 GA 候选均 ALREADY_COVERED。
- **不推荐投入。**

## 6. 结论

CMA-ES 基线在 MetaBox 中可运行但有 FE 计数和指标语义偏差（可通过独立计数器解决）。然而候选 A1 的核心机制（C 矩阵病态缓解）已被 `cma` 包 `conditioncov_alleviate` 覆盖。
