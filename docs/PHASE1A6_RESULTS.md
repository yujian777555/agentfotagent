# Phase-1A-6 Baseline Rebuild Results

## 执行摘要

| 项 | 值 |
|---|---|
| 算法 | `lshade-canonical-reimpl`（`canonical_reimplementation; not official code`） |
| 套件 | BBOB 10D |
| 函数 | split_v2 train: F1, F2, F4, F6, F7, F10, F11, F12, F15, F18, F20, F21（12 个） |
| 种子 | 11, 22, 33 |
| 预算 | 5,000 FE / run |
| 干预 | **无**（无 N+I、无状态触发、无额外重启、无 LLM） |
| 计划运行 | 36 |
| 成功运行 | **36** |
| 失败 | **0** |
| FE 精确 | **36/36 全部 `fes == independent_fes == 5000`** |
| 总耗时 | 42.36 s |

配置冻结文件：`results/phase1a6/frozen_config.json`（含代码 SHA-256、split manifest hash）。

## 指标语义声明

- `best_raw`：`problem.eval` 返回的原始目标值（含 BBOB bias），已验证。
- `best_benchmark_cost`：`best_raw − optimum`。**不是 regret**，可为负。
- `best_regret`：仅当该函数全轨迹 `raw ≥ optimum` 时填入，否则为 `null`。
- F20 的 `optimum`（=2100）**不是** `raw_objective` 的严格下界（MetaBox Schwefel 实现特性），故 `optimum_is_lower_bound=false`，`primary=benchmark_cost`。

## 逐函数汇总（3 种子）

| F | family | best_raw 范围 | benchmark_cost 范围 | lower_ok | 备注 |
|---:|---|---|---|---|---|
| 1 | separable | 700 – 700 | 1.2e-5 – 8.3e-5 | ✓ | 达到 optimum |
| 2 | separable | 2.1e4 – 7.0e4 | 1.9e4 – 6.9e4 | ✓ | 困难 |
| 4 | separable | 1036 – 1055 | 36 – 55 | ✓ | |
| 6 | low/mod cond. | 402 – 433 | 2.4 – 33 | ✓ | |
| 7 | low/mod cond. | 301 – 311 | 0.8 – 11 | ✓ | |
| 10 | high cond. | 2.4e4 – 1.7e5 | 2.3e4 – 1.7e5 | ✓ | 高条件数 |
| 11 | high cond. | 915 – 1.6e4 | 15 – 1.5e4 | ✓ | 方差大 |
| 12 | high cond. | 3475 – 5698 | 1475 – 3698 | ✓ | |
| 15 | multimodal | 1737 – 1759 | 37 – 59 | ✓ | |
| 18 | multimodal | 704 – 768 | 3.6 – 68 | ✓ | |
| **20** | multimodal weak | **2043 – 2047** | **−57 – −53** | **✗** | **optimum 非下界** |
| 21 | multimodal weak | 786.565 – 786.565 | 86.565（恒定） | ✓ | 三种子完全相同 |

## 关键观察

1. **FE 精确性**：36/36 全部满足 `fes == independent_fes == max_fes`，无超预算、无漏计。
2. **N 行程**：全部 `100 → 4`，符合标准线性缩减在 FE=max_FE 时到达 N_min。
3. **F20 负 cost 语义已捕获**：三种子 `best_raw ∈ [2042.8, 2046.6] < optimum=2100`，canonical 实现正确置 `optimum_is_lower_bound=false`、`regret=null`，主指标为 `benchmark_cost`。这与审计 §D.3 的根因判定一致，不是优化器越界。
4. **F21 三种子 best 完全相同**（786.5654...）：提示 F21 在该预算内收敛到同一吸引子/盆地，或该函数实现存在确定性结构。属函数特性观察，不影响 FE/身份门禁。
5. **种子敏感性**：F2、F10、F11 跨种子方差大（最差与最好差 1–7 倍）；F1、F4、F15、F21 稳定。

## 与历史（lshade_reimpl）可比性

本基线 **不可** 与 4R3/5 的 `L_SHADE` 臂直接做数值比较：

- 4R3 预算为 10,000 FE（本基线 5,000 FE）；
- N(t) 公式、F 分布均不同；
- 4R3 含 N+I 对照臂，本基线无干预。

本基线的作用是 **重建可信的标准 L-SHADE 参考轨迹**，供后续机制研究作唯一合法对照臂。

## 产物清单

```
results/phase1a6/
├── frozen_config.json           # 执行前冻结的配置 + 代码 SHA-256
├── manifest_phase1a6.json       # 逐运行汇总 + 失败列表 + 代码 SHA
├── rows.json                    # 同上 rows 数组（便于程序读取）
└── trajectories/
    ├── F01_s11.json ... F21_s33.json   # 36 份完整曲线
```

每条轨迹含：`raw_curve`、`benchmark_cost_curve`、`regret_curve`（可 null）、`n_history`、`fes`、`independent_fes`、`optimum`、`optimum_is_lower_bound`、`log_points`。

## 限制

- 3 种子 / 函数，**不做统计显著性主张**。
- 仅 train split；未触碰 validation / held-out。
- 5,000 FE 是训练预算设定，不代表收敛极限。
