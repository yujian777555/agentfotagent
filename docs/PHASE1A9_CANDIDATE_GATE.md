# Phase-1A-9 Candidate Gate

## 门禁判定

| 候选 | Gate 1（问题真实） | Gate 2（非改名） | Gate 3（独立归因） | Gate 4（可执行） | 判定 |
|---|---|---|---|---|---|
| A1: C 矩阵特征值裁剪 | ✅ C 矩阵病态有文献依据 | ❌ **ALREADY_COVERED** | — | — | **REJECT** |
| A2: CSA 步长保护 | ✅ CSA 局限有文献依据 | ❌ **ALREADY_COVERED** | — | — | **REJECT** |
| B1: 多样性锦标赛选择 | ✅ GA 多样性丢失有文献依据 | ❌ **ALREADY_COVERED** | — | — | **REJECT** |
| B2: 自适应重组率 | ✅ 固定参数局限有文献依据 | ❌ **ALREADY_COVERED** | — | — | **REJECT** |

**0 个候选通过全部四道门。**

## 逐候选 Gate 2 详析

### A1: C 矩阵特征值裁剪

**最接近的三种方法：**

| 方法 | 更新公式 | 状态变量 | 决策规则 | 适用条件 |
|---|---|---|---|---|
| **conditioncov_alleviate**（cma 内置） | `alleviate_conditioning_in_coordinates(1e8)` + `alleviate_conditioning(1e12)` — 将 C 的条件数传递到 sigma_vec / gp | C, σ_vec, gp | 条件数 > 阈值时触发 | 通用 |
| **sep-CMA-ES**（Ros & Hansen 2008） | C = diag(C)，放弃非对角 | 对角 C | 始终 | 高维、FE 紧张 |
| **VD-CMA**（Akimoto 2012） | C = D + VVᵀ（低秩+对角） | D, V | 始终 | 高维 |

**本候选**：`C ← B·diag(max(λi, ε·tr(C)/n))·Bᵀ`（特征值下界裁剪）

**判定理由**：与 `conditioncov_alleviate` 解决同一问题（C 矩阵病态），机制是"条件数缓解"的另一种数学形式。与 sep-CMA-ES 的区别（保留非对角）已由 VD-CMA 覆盖。属于**已有机制的参数化重写**。

### A2: CSA 步长保护

最接近：TPAM-CMA-ES、restart strategies（已关闭）、各种 CSA 改进。核心是阈值 + 缩放因子 = **参数调整**。

### B1: 多样性锦标赛选择

最接近：fitness sharing（Goldberg 1987）、crowding（De Jong 1975）、SPEA2 的 density estimation。修改选择概率 = **fitness sharing 的变体**。

### B2: 自适应重组率

最接近：jGA、自适应交叉率（Davis 1989）、AGA（Srinivas & Patnaik 1994）。自适应参数控制 = **已有 30 年历史**。

## Gate 3 与 Gate 4 状态

由于 Gate 2 全部失败，Gate 3（独立归因）和 Gate 4（实验可执行）不进入评估。即使通过 Gate 4（CMA-ES 可运行），也无法区分机制贡献与已有方法。

## 已关闭路线的核对

| 关闭路线 | 是否被候选触碰 | 判定 |
|---|---|---|
| CC-SOC / 质量残差 / IPW/DR | 否 | 安全 |
| N+I 重启 / 状态触发 | 否（A2 不是重启） | 安全 |
| 自适应种群缩减 | 否 | 安全 |
| archive × boundary repair | 否 | 安全 |
| F/CR 记忆平滑 / 零改进门控 / 多样性切换 | 否 | 安全 |
| p-best 最小距离选择 | 否 | 安全 |

**无候选触碰已关闭路线。问题在于所有存活候选被已有方法覆盖。**

## 结论

**NO_GO_PHASE1A_ALGORITHM_DISCOVERY** — 没有候选通过创新性审查。所有候选被已有方法覆盖（ALREADY_COVERED 或 MINOR_VARIANT）。
