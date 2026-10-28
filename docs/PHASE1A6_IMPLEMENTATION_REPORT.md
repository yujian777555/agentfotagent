# Phase-1A-6 Implementation Report

## 目标

在不覆盖历史实现的前提下，建立独立的 **标准 L-SHADE 重实现**，并用独立测试门禁验证其与 Tanabe & Fukunaga (CEC 2014) 算法语义的一致性。

## 交付物

| 文件 | 作用 |
|---|---|
| `experiments/metabox/agent_assisted_ec/lshade_canonical.py` | 标准 L-SHADE 重实现（`canonical_reimplementation; not official code`） |
| `tests/test_phase1a6_lshade_canonical.py` | 独立门禁测试（47 项） |
| `experiments/metabox/agent_assisted_ec/run_phase1a6_baseline.py` | 一次 train-only 基线重建驱动脚本 |

`lshade_reimpl.py` **未改动**，作为 Phase-1A-4R3/4R2/4R/5 历史证据的载体保留。

## 官方实现检索结论

未找到可核验的 Tanabe/Fukunaga 官方 L-SHADE 公开仓库（该算法的常见引用实现多为第三方 C++/MATLAB 重实现，许可证与版本不可追溯）。因此本实现严格依据：

1. R. Tanabe & A. S. Fukunaga, *Success-history based parameter adaptation in Differential Evolution*, IEEE CEC 2014.
2. SHADE 前作（CEC 2013）中关于成功历史记忆与外部档案的约定。

文件头明确标注 **`canonical_reimplementation; not official code`**。

## 修复依据

### 1. 种群缩减公式

| 项 | 值 |
|---|---|
| 论文公式 | `N_target = round(N_init + (N_min − N_init) · FE / max_FE)` |
| 旧实现 | `max(N_min, round(N_init · (1 − FE/max_FE)))` |
| 差异 | 旧公式更早触及 N_min（FE=4800/5000 时 4 vs 8） |
| 修复 | `linear_n_target()` 使用论文插值式；测试断言端点 100/4 与中点 52 |

### 2. F 采样

| 项 | 值 |
|---|---|
| 论文 | Cauchy(M_F, 0.1)；F>1 截断为 1；F≤0 重采样 |
| 旧实现 | Normal(M_F, 0.1) 裁剪 [0,1] |
| 修复 | `sample_f()` 用 Cauchy 逆 CDF + 标准边界；测试验证重尾、非负、截断 |

### 3. CR 采样

论文 Normal(M_CR, 0.1) 裁剪 [0,1]；旧实现一致。canonical 保留，测试验证边界与均值。

### 4. 成功历史

M_F Lehmer 平均 `Σ w F² / Σ w F`，M_CR 加权算术平均 `Σ w CR / Σ w`，`w = |Δf|`；空成功集不更新、不推进 k_pos。旧实现此处一致，canonical 保持并用单元测试锁死公式数值。

### 5. 变异索引排除

论文要求 r1≠i、r2≠i、r2≠r1。旧实现 r2 抽样未排除 r1。canonical 用 `select_r1_r2()` 显式排除，测试覆盖含档案情形。

### 6. 档案与缩减同步

canonical 在 N 缩减时裁剪档案至新 N，保持容量不变量 `|A| ≤ N`。

### 7. 父子代选择

canonical 采用 `trial_fit ≤ parent_fit`（论文常见的最小化接受规则）。

### 8. 指标语义

分离 `raw_objective` / `benchmark_cost` / `regret`；仅当全轨迹 `raw ≥ optimum` 时才填 `regret`，否则 `regret=None`。F20 历史负值问题由该字段分离解决。

### 9. 显式记录的约定差异

- **边界处理**：clip 到 [lb, ub]。部分论文变体在边界与父代分量之间重采样；clip 是广泛使用的简化，已在文件头注明。
- **p-best 取整**：`max(2, floor(p·N))`。论文未规定 round/ceil/floor；此处记录为约定。
- **档案容量**：随当前 N。论文 "size=NP"；部分实现固定为 N_init。此处取论文字面义。

## 独立测试门禁

`tests/test_phase1a6_lshade_canonical.py` — **47 项，全部通过**。

| # | 覆盖项 | 测试类 |
|---|---|---|
| 1 | 缩减公式端点/中点/与旧公式差异 | `TestLinearNTarget` |
| 2 | N 单调不增、≥ N_min | `TestPopulationSchedule` |
| 3 | F/CR 分布与边界 | `TestParameterSampling` |
| 4 | 变异索引约束 | `TestIndexConstraints` |
| 5 | 成功历史更新与空集 | `TestMemoryUpdate` |
| 6 | 档案容量与缩减一致性 | `TestArchive` |
| 7 | 最小化与父子代选择 | `TestSelection` |
| 8 | raw/cost/regret 语义（含负 cost 场景） | `TestMetricSemantics` |
| 9 | F1/F6/F24 真实身份 | `TestRealFunctionIdentity` |
| 10 | 精确 FE、种子复现、轨迹完整性 | `TestFEReproducibility` |

全量回归：`tests/` **356 项 collected，exit code 0**（无失败、无跳过导致的红灯）。

## 已知限制

1. 非官方代码，无参考实现可做数值逐位比对；正确性锚定在论文公式 + 单元测试。
2. 边界处理与 p-best 取整存在实现约定（见上），非论文强制项。
3. MetaBox F20 optimum 语义问题属基准套件性质，非本实现可修复。
