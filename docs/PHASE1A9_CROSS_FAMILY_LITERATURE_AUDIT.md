# Phase-1A-9 Cross-Family Literature Audit

## 范围与约束

按任务书排除 PSO（避免 GLEPPO 项目混用）。已关闭路线不得换名重开：
CC-SOC/质量残差/IPW/DR、N+I 重启/状态触发、自适应种群缩减、archive×boundary 交互、F/CR 记忆平滑/零改进门控/多样性切换、p-best 最小距离选择。

## 家族 1：CMA-ES 与连续进化策略

### 1.1 CMA-ES（Hansen & Ostermeier 2001; Hansen 2003）

| 项 | 内容 |
|---|---|
| 原始论文 | Hansen & Ostermeier (2001) "Completely derandomized self-adaptation in evolution strategies"; Hansen (2003) "Reducing the time complexity of derandomized ES with CMA" |
| 核心公式 | 协方差矩阵 C 的 rank-μ 更新：`C ← (1-c1-cμ)C + c1·pσpσᵀ + cμ·Σwi(xi-x̄)(xi-x̄)ᵀ` |
| 状态变量 | m（均值向量）、C（协方差矩阵）、σ（步长）、pc（进化路径）、pσ（步长路径） |
| 状态更新 | m ← m + σ·B·D·⟨N(0,I)⟩weighted；CSA 更新 σ；rank-μ 更新 C |
| 最近邻 | sep-CMA-ES（对角 C）、VD-CMA（低秩+对角）、CMA-ES-λ |
| 证据等级 | **FULL**（Hansen 的参考实现和公式可逐项核验） |
| 已知不足 | ① C 矩阵在有限 FE 下可能未收敛（高维尤其明显）；② CSA 在选择压力单侧时步长收缩；③ 边界处理影响搜索 |
| 不足证据 | Hansen 2003 §3.2 讨论了 population size 对 C 收敛的影响；Auger & Hansen 2005 讨论了 restart 需求 |

**候选机制 A1：有限 FE 下的 C 矩阵正则化**

| 项 | 内容 |
|---|---|
| 缺陷 | 在 5,000 FE / 10D 条件下，CMA-ES 的 C 矩阵可能病态（条件数过大），导致搜索方向退化 |
| 公式改动 | 在 rank-μ 更新后对 C 做特征值裁剪：`C ← B·diag(max(λi, λmin))·Bᵀ`，其中 λmin = ε·trace(C)/n |
| 最近邻 | sep-CMA-ES（直接用对角 C，放弃非对角项）；VD-CMA（低秩+对角近似） |
| 机制区别 | sep-CMA-ES **放弃**非对角项；本候选**保留**非对角项但裁剪极端特征值。是介于 full CMA-ES 和 sep-CMA-ES 之间的中间方案 |
| 证据来源 | **待验证假设**——MetaBox CMAES 中未直接观测到 C 矩阵病态（无诊断日志） |
| 最小改动 | 在 `cma` 包的 C 更新后加一步特征值裁剪（可通过 callback 或 monkey-patch） |
| 证伪实验 | 对比 full CMA-ES vs eigenvalue-clipped CMA-ES vs sep-CMA-ES 在 3 函数 × 3 种子 |
| 消融 | A0: full CMA-ES；A1: clipped CMA-ES；A2: sep-CMA-ES；A3: 随机扰动 C 的对照 |
| 可行性 | 需 monkey-patch `cma` 包内部状态，**实现成本中等，独立验证成本高** |

**候选机制 A2：CSA 步长保护**

| 项 | 内容 |
|---|---|
| 缺陷 | CSA 在选择压力单侧时 σ 快速收缩至零（"step-size collapse"） |
| 公式改动 | 当 pσ 模长连续 k 代低于阈值时，强制 σ ← σ·increase_factor |
| 最近邻 | IPOP-CMA-ES（重启，已关闭）；TPAM-CMA-ES（目标优先级自适应） |
| 机制区别 | 不是重启，而是步长保护；但本质是**阈值调整 + 平滑系数** |
| 证据来源 | Hansen 2003 §2.2 讨论了 CSA 的局限 |
| 判定 | **ALREADY_COVERED**（CSA 的改进方案在 CMA-ES 文献中已有大量工作） |

### 1.2 其他 ES（(μ,λ)-ES, CMA-ES 变体）

| 变体 | 核心差异 | 与候选关系 | 证据等级 |
|---|---|---|---|
| sep-CMA-ES (Ros & Hansen 2008) | 对角 C，降低复杂度 | 是 A1 的最近邻 | FULL |
| VD-CMA (Akimoto 2012) | 低秩+对角 C | 是 A1 的最近邻 | PARTIAL |
| tNES (Sun et al. 2022) | 信任域 NES | 完全不同框架 | SECONDARY |
| LM-CMA (Loshchilov 2017) | 低内存 CMA | 与 A1 有重叠 | SECONDARY |

## 家族 2：遗传算法（GA）

### 2.1 GA 选择机制

| 项 | 内容 |
|---|---|
| 原始论文 | Holland (1975) "Adaptation in Natural and Artificial Systems" |
| 核心机制 | 选择（tournament/roulette）、重组（crossover）、变异（mutation） |
| 证据等级 | **FULL**（经典教材级） |

**候选机制 B1：多样性感知锦标赛选择**

| 项 | 内容 |
|---|---|
| 缺陷 | 标准锦标赛选择在晚期丢失多样性 |
| 公式改动 | 锦标赛获胜概率 ∝ fitness + α·diversity_contribution |
| 最近邻 | fitness sharing (Goldberg & Richardson 1987)；crowding (De Jong 1975)；SPEA2 |
| 机制区别 | 与 fitness sharing 的区别是不修改 fitness 本身，而是修改选择概率 |
| 判定 | **ALREADY_COVERED**（fitness sharing / crowding / niching 在 GA 文献中是成熟方向） |

**候选机制 B2：自适应重组率**

| 项 | 内容 |
|---|---|
| 缺陷 | 固定交叉率不适应搜索阶段 |
| 公式改动 | pc = f(generation, diversity) |
| 最近邻 | jGA (自适应 GA)；自适应交叉率已有大量工作 |
| 判定 | **ALREADY_COVERED**（自适应参数控制在 GA 中已有 20+ 年历史） |

### 2.2 GA 实现可行性

MetaBox **无纯 GA 实现**。`MFEA` 是多任务优化（`run_episode(mto_tasks)`），`GLPSO` 是 PSO。需要从头实现完整 GA 才能测试候选。

**实现成本评估：**
- 完整 GA（选择+重组+变异+精英）：~150-200 行
- 独立验证（FE 计数、种子复现、指标语义）：~100 行测试
- 与 MetaBox BBOB 适配：~50 行
- **总成本：~300-400 行新代码 + 测试**

## 家族 3：其他成熟基线

| 算法 | MetaBox 可用性 | 备注 |
|---|---|---|
| Random Search | ✅ | 仅作对照，无研究价值 |
| CMA-ES | ✅（有语义问题） | 见上 |
| GA | ❌（需从头实现） | 见上 |
| PSO | 已排除 | GLEPPO 项目 |

## 初筛结论

| 候选 | 家族 | Gate 1（问题真实） | Gate 2（非改名） | 初判 |
|---|---|---|---|---|
| A1 C 矩阵正则化 | CMA-ES | 待验证假设 | 与 sep-CMA-ES 有实质区别 | **待 Stage B** |
| A2 CSA 保护 | CMA-ES | 有论文依据 | ALREADY_COVERED | ❌ |
| B1 多样性选择 | GA | 有论文依据 | ALREADY_COVERED | ❌ |
| B2 自适应重组 | GA | 有论文依据 | ALREADY_COVERED | ❌ |

**唯一存活候选：A1（CMA-ES 特征值裁剪）**。需进入 Stage B 核验环境可行性。
