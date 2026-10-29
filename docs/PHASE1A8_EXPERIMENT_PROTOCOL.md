# Phase-1A-8 Experiment Protocol

## 配置（冻结）

| 项 | 值 |
|---|---|
| 套件 | BBOB 10D |
| 函数 | F1, F7, F10, F20（split_v2 train） |
| 种子 | 11, 22, 33, 44, 55 |
| 预算 | 5,000 FE/run |
| 方向 | minimize |
| LLM | 0 |

## Stage A（基线 + 边界事件诊断）

20 runs。标准 L-SHADE + 诊断日志（不改 RNG、不改行为）。
逐位门禁：seeds 11/22/33 与 Phase-1A-6 比较 `raw_curve`/`benchmark_cost`/`n_history`/`best_raw`/FE。

## Stage B（2×2 配对实验）

| 实验臂 | Archive | Boundary repair |
|---|---|---|
| A0 | 标准档案 | clip（标准） |
| A1 | 禁用 | clip |
| A2 | 标准档案 | parent-midpoint |
| A3 | 禁用 | parent-midpoint |

`parent-midpoint`：超界坐标修复到 (bound + parent_coord) / 2。

A0 必须与标准实现逐位一致（已通过测试验证）。
80 runs = 4 arms × 4 functions × 5 seeds。

## 预注册分析

### 主效应
- A0 vs A1：clipping 下的档案主效应
- A2 vs A3：parent-midpoint 下的档案主效应

### 交互效应
`(A2 - A3) - (A0 - A1)`

差值方向定义：正值 = archive 在该条件下对 minimization 有益（best_raw 更低）。

### 机制检验
- archive 来源是否改变超界概率
- 修复后 trial 的成功率与改善幅度
- 交互是否跨函数方向一致

### 限制
5 seeds 仅提供探索性证据。逐函数报告，不跨函数平均原始目标值。F20 使用 `benchmark_cost`。
