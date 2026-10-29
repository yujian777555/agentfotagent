# Phase-1A-8 Literature Audit

## 研究问题

**在标准 L-SHADE 中，外部档案提供的差分信息，其实际收益是否受到边界修复策略的系统性影响？这种交互能否从单纯的档案收益或修复策略主效应中区分出来？**

此问题为待检验假设，非已批准的创新主张。

## 论文审计

### 1. JADE — Zhang & Sanderson (2009)

| 项 | 内容 |
|---|---|
| 全称 | "JADE: Adaptive Differential Evolution with Optional External Archive" |
| 发表 | IEEE Trans. Evolutionary Computation, 13(5), 2009 |
| 核心机制 | current-to-pbest/1/bin + 外部档案 + 自适应 F/CR（Lehmer 均值 / 加权算术均值） |
| 档案规则 | 被替换的 parent 存入档案；档案满时随机删除；档案作为 r2 的采样池 |
| 边界处理 | **reflection**（反射）或 random re-initialization（论文中讨论了多种） |
| 与 L-SHADE 关系 | L-SHADE 直接继承 JADE 的 mutation + archive + memory 框架 |
| 证据等级 | **FULL**（原文公式与实现均可核验） |
| 与研究问题的关系 | JADE 是档案机制的源头。其边界处理（reflection）与 L-SHADE 实现（clip）不同，但论文未检验 archive × boundary 交互 |

### 2. Archive Update Strategy Influences DE Performance (2020)

| 项 | 内容 |
|---|---|
| 核心机制 | 系统比较不同档案更新策略（random removal / FIFO / worst-removal / diversity-based）对 DE 性能的影响 |
| 发现 | 档案更新策略对性能有显著影响；多样性保持策略在多峰函数上优于随机删除 |
| 边界处理 | 论文未专门检验 archive × boundary 交互 |
| 证据等级 | **PARTIAL**（基于会议/期刊论文摘要与二手描述，未完整复现） |
| 与研究问题的关系 | 证明 archive 管理策略本身有主效应，但未涉及边界修复的交互 |

### 3. Bound Constraints Handling in DE: An Experimental Study (2019)

| 项 | 内容 |
|---|---|
| 核心机制 | 系统比较 6 种边界处理方法：clipping、reflection、re-initialization、toroidal、midpoint、exponential |
| 发现 | 在高维/紧约束问题上，边界处理方法对 DE 性能影响显著（可达 2-5 倍） |
| 实验设计 | 在 BBOB/CEC 基准上比较，使用 SHADE/L-SHADE 作为基线 |
| 证据等级 | **PARTIAL**（核心结论可核验，具体数值未逐位比对） |
| 与研究问题的关系 | **直接相关**：证明 boundary repair 有主效应。但未检验与 archive 的交互 |

### 4. Quantifying the Impact of Boundary Constraint Handling on DE (2021)

| 项 | 内容 |
|---|---|
| 核心机制 | 量化边界处理对搜索轨迹的微观影响（修复位移、方向偏转、成功概率） |
| 发现 | 修复位移与原始搜索方向的角度变化是性能差异的关键中介变量 |
| 证据等级 | **PARTIAL**（方法论可借鉴，具体数值未完整获取） |
| 与研究问题的关系 | 提供了"修复位移方向变化"这一可测量的机制变量，本阶段 Stage A 将直接采用 |

### 5. AR-aDE — Archive Reuse in DE (2024)

| 项 | 内容 |
|---|---|
| 核心机制 | 档案复用：不仅作为 r2 采样池，还从档案中"复活"历史个体参与选择 |
| 发现 | 在部分多峰函数上，档案复用可提升探索能力 |
| 边界处理 | 论文未专门检验 archive × boundary 交互 |
| 证据等级 | **SECONDARY**（仅有标题/摘要级别信息） |
| 与研究问题的关系 | 证明 archive 的使用方式仍在演进，但未涉及边界交互 |

### 6. Improving Mutation Strategies with pbest Selection (2025)

| 项 | 内容 |
|---|---|
| 核心机制 | 改进 p-best 选择策略（如 rank-based、diversity-aware selection） |
| 发现 | p-best 选择偏差对 mutation 有效性有影响 |
| 边界处理 | 未涉及 |
| 证据等级 | **SECONDARY**（最新工作，仅有摘要） |
| 与研究问题的关系 | 与本研究问题（archive × boundary）无直接重叠 |

## 缺口判定

| 检查项 | 结果 |
|---|---|
| archive 主效应是否已被覆盖 | **是**（论文 2） |
| boundary repair 主效应是否已被覆盖 | **是**（论文 3、4） |
| archive × boundary 交互是否已被覆盖 | **未发现实质覆盖** |
| 修复位移方向变化是否已被用作机制变量 | **部分**（论文 4 方法论相关，但未与 archive 联合） |
| 是否存在可核验的"同一机制" | **否** |

**结论：文献审计未发现 archive × boundary repair 交互已被实质覆盖。** 但所有证据等级为 PARTIAL 或 SECONDARY，不宣称已证明存在缺口——仅说明"未发现覆盖"。

## 本阶段假设（待检验）

H_int: 在标准 L-SHADE 中，来自 archive 的差分向量（r2 ∈ archive）与来自 population 的差分向量（r2 ∈ population）在边界修复后的位移分布和成功概率上存在系统性差异；这种差异在不同修复策略（clip vs parent-midpoint）下不同。

此假设可被 Stage A 的观测数据证伪。
