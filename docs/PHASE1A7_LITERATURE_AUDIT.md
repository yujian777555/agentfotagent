# Phase-1A-7 Literature Audit

## 检索方法

本次文献审计通过 Phase B 提案中的 `nearest_neighbor` 字段与 Phase C 审查中的 `novelty_rating` 联合判定。每项标注证据等级（FULL / PARTIAL / SECONDARY）。

## 候选与最近邻

### 1. DGDD（Diversity-Gated Differential Direction）

| 项 | 内容 |
|---|---|
| 声称机制 | 多样性低时将差分方向 x_r1−x_r2 替换为随机方向 x_rand−x_i |
| 最近邻 | current-to-pbest/1/bin (Zhang & Sanderson 2009)；jSO (Brest et al. 2017)；多样性控制 DE |
| 审查判定 | **MINOR_VARIANT** |
| 证据等级 | SECONDARY |
| 核心问题 | 将 diversity-based switching 调整为 g-gating，本质是已有多样性自适应 DE 的参数化重写 |

### 2. FMF-DC（F-Memory Floor with Directional Compensation）

| 项 | 内容 |
|---|---|
| 声称机制 | F 下限 + 方向补偿 |
| 最近邻 | SHADE/L-SHADE F 记忆 (Tanabe & Fukunaga 2014)；jSO；固定 F=0.5 |
| 审查判定 | **ALREADY_KNOWN** |
| 证据等级 | SECONDARY |
| 核心问题 | "F floor" 在多个 DE 变体中已有实现；补偿项是已知 scaling trick |

### 3. Zero-Δf Success Veto

| 项 | 内容 |
|---|---|
| 声称机制 | Δf=0 时不更新成功记忆 |
| 最近邻 | SHADE success-history (Tanabe & Fukunaga 2014) |
| 审查判定 | **ALREADY_KNOWN** |
| 证据等级 | SECONDARY |
| 核心问题 | 多个 SHADE 变体已有 strict-improvement gating；不是新机制 |

### 4. CR Memory Drift Dampening

| 项 | 内容 |
|---|---|
| 声称机制 | 指数平滑 / 偏差惩罚权重 |
| 最近邻 | SHADE weighted mean for M_CR；jSO |
| 审查判定 | **MINOR_VARIANT** |
| 证据等级 | SECONDARY |
| 核心问题 | 在已有加权平均上加 smoothing 因子，属参数调整 |

### 5. SIG-SM（Strict-Improvement-Gated Success Memory）

| 项 | 内容 |
|---|---|
| 声称机制 | 分离生存选择（≤）与记忆更新（严格改进） |
| 最近邻 | SHADE success-history；多篇 DE 变体已有 strict-improvement gate |
| 审查判定 | **FAIL**（3/3 审查中 2 个标注 ALREADY_KNOWN，1 个 MINOR_VARIANT） |
| 证据等级 | SECONDARY |
| 核心问题 | "split survival from memory update" 在 SHADE 改进文献中已有 |

## 结论

所有 5 个候选在独立审查中被评为 **MINOR_VARIANT** 或 **ALREADY_KNOWN**。没有任何候选达到 **NOVEL_MECHANISM** 评级。文献证据等级均为 SECONDARY（仅有二手描述、公式层面的对比，无 FULL 论文复现验证）。

**判定：NO_GO_NEW_MECHANISM**
