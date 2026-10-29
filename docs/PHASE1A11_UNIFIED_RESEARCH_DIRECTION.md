# Phase-1A-11：统一研究主线与双路线执行计划

- 仓库：`yujian777555/agentfotagent`
- 本计划分支：`phase1a-phase11-unified-agent-ec-roadmap`
- 起始证据提交：`3c3c6293aefa4861047b56d2c4d1057feb6a9b7c`（Phase-1A-10 Corrective + Stage B）
- 状态：研究计划已记录；本文件本身不代表任何新算法或性能结果已经成立。
- 本阶段预算：0 真实 LLM API 调用；0 MetaBox 性能实验；0 AES 科学性能实验；0 test split 访问。

## 1. 锁定的项目目标

本项目的主线是 **LLM 赋能演化计算，并将演化计算用于改进大模型 Agent**。不是以数值基准分数为最终应用目标，也不是把 Agent 生成算法代码本身当成创新。

研究闭环分为三层：

1. **LLM → EC：** LLM/Agent 根据真实优化轨迹诊断问题，提出有证据挂钩、可执行、可否证的演化机制或高层搜索控制改进。
2. **EC → Agent：** 将经审计、经验证的演化搜索或高层控制策略用于本仓库自有的 Agent Evolution Sandbox（AES），优化 Agent 的策略基因型和任务表现。
3. **双向反馈（条件性）：** 只有前两层各自得到独立证据后，才检验 Agent 进化轨迹能否进一步改进演化控制器。

**应用目标固定为 Agent 改进；性能收益仍是需要实验检验的假设。** 不得因为第一层某个候选失败就永久放弃第二层；也不得因为项目目标是应用到 Agent 就预先宣称迁移或收益必然成立。

## 2. 当前已知证据与边界

### Phase-1A-10 的结果

根据 `docs/PHASE1A10_DECISION.md` 及 Stage B/C 报告：

- 24/24 次真实请求使用 `deepseek-flash`；该轮预算已耗尽。
- A（trace）预筛通过 5/12，B（blind）3/12，C（random）12/12。
- 36 个候选无一通过独立审查；Stage D 未启动。
- 结论是 `NO_GO_AGENT_DESIGN_ADVANTAGE`：在当前协议下没有证明 Agent 设计优势，不等于证明 Agent 永远不可能有价值。
- 当前候选没有性能提升证据。

### 已关闭的算法主张

不得直接重开 CC-SOC/质量残差/IPW-DR、旧 N+I 重启、状态触发优越性、进度自适应种群缩减、Archive × Boundary 交互等已否证路线。若有新证据，只能作为独立新假设重新审计，不能复用旧结论冒充新证据。

### AES 的现状要求

项目自己的 AES 是目标域，不得用其他独立仓库替代。此前状态记录显示：小型 pilot 的 16 个 genotype 在 6 个小型 train task 上均达到 1.0 success，平均步数约 9.83–13.0；该 pilot 使用手写 surrogate/Mock backend，不能作为真实 Agent 能力或演化收益证据。执行者必须回到当前源码、任务配置和报告核验此事实及其适用版本，不能把历史摘要直接当作当前代码状态。

MetaBox 是标准化数值优化实验基础设施，不是研究贡献。canonical L-SHADE 是当前可信算法基线；旧实现和旧实现上的性能结论必须保持历史标记。

## 3. 两条并行研究工作

### Track A — LLM 赋能演化计算：机制缺口审计

目标不是立即生成更多候选，而是审计 Phase-1A-10 四个尚未解决的新颖性候选及相关原始文献/实现：

- `per-dimension-F-floor-with-memory-reset`
- `repair-aware-mutation-resample`
- `repair_aware_resampling`
- `repair-aware-mutation-reflect`

要求恢复原始候选与 SHA-256、定位机制对应源码、核验原始论文和作者实现、判断是否已有覆盖，并从可信轨迹确认问题是否真实存在。

只有候选同时满足以下条件，才可进入新的实验设计：
1. 存在可核验的真实失败模式；
2. 数学规则/算法行为明确；
3. 与最近邻方法存在具体而非命名层面的机制差异；
4. 有可能在相同 FE 预算下检验；
5. 预注册了强基线、人工规则、随机修改/映射对照、消融和停止规则。

若四个候选都不成立，关闭这批候选，但不关闭整个项目，也不自动触发新一轮 API 生成。

### Track B — 演化计算用于改进 Agent：AES 目标域基线审计

此轨道是项目核心目标的一部分，不需要等待 Track A 宣布算法创新成功才开始做可行性工作；但在环境/评估器未通过审计前，不开展科学性能实验。

首先核验：
- AES 当前分支、源文件、基因型 schema、genotype→phenotype/runtime；
- 每个基因是否真实改变运行行为；
- 任务是否非平凡、可验证、存在可观测的性能差异；
- 任务分割、泄漏防护、缓存隔离、trace 和 provenance 是否可靠；
- random search、固定配置和 conventional EA 是否共享同一评估器、相同有效搜索空间及评价预算；
- 当前 pilot 饱和的根因，以及是否需要改造任务难度或基因语义。

通过工程审计后，再冻结一个最小 Agent 进化实验：在固定 backbone、任务环境和预算下比较：
- 固定/不进化 Agent；
- 随机搜索；
- 常规 EA（如 DE/GA/NSGA-II/III 中经公平性审计后适用者）；
- LLM 赋能的 EC 控制/搜索策略；
- 必要的人工规则与 shuffled 控制。

不要一次比较所有算法。根据目标 Agent 基因型和任务指标选取最有解释力的少量基线。

Mock backend 仅用于工程验证，不能支持 Agent 能力或真实任务收益主张。真实 LLM/工具环境实验需单独预算批准；所有真实 LLM 请求必须使用 `deepseek-flash`，不得使用 `deepseek-v4-pro`。

## 4. 连接两条轨道：需要明确的迁移对象

不要把数值 DE 的 F/CR、差分向量等低层操作直接映射到 Agent 提示词或工具调用。

若要验证项目原始 H2，应明确一个可跨域表达的**高层演化控制对象**，并在实验前给出：
- 源域（MetaBox 数值优化）的状态特征、动作、反馈和适用边界；
- 目标域（AES Agent genotype）的对应状态、动作、反馈和映射规则；
- 哪些语义保持不变，哪些由 adapter 转换；
- 对照：目标域独立调优、随机/打乱映射、固定控制器，以及目标域常规 EA；
- 失败判据：若迁移不优于目标域独立调优或 shuffled mapping，则不宣称迁移成功。

迁移控制器是待研究对象，不能预设已有一个已验证的通用控制器。

## 5. 研究决策门

- `GATE-A`：候选的机制差异与文献覆盖已审计；不通过则不跑候选性能实验。
- `GATE-B`：AES 环境、任务难度、基因效应、评估器与公平基线通过独立工程审计；不通过则先修环境。
- `GATE-C`：两条轨道各自的实验协议、预算、指标、种子、统计方法、最小实际效应与停止规则预先冻结。
- `GATE-D`：仅在授权后运行真实实验；报告所有结果和失败，不访问未授权 test split。
- `GATE-H2`：只有明确迁移对象并通过独立目标域确认，才讨论跨域迁移成立。
- `GATE-H3`：只有 H2 得到可重复证据后才研究双向反馈。

## 6. 当前阶段允许和禁止的工作

允许：
- 只读核验文献、源码、候选、轨迹与状态；
- 修正状态文件和交接文档；
- 对 AES 现状做静态/离线工程审计；
- 编写候选机制的可证伪规格和后续实验草案。

禁止：
- 真实 LLM API 调用；
- 未经批准的 MetaBox/AES 科学性能实验；
- 访问 test/held-out split；
- 重启已关闭路线并根据旧结果宣称成功；
- 将工程测试、Mock backend 分数或 Agent 生成的机制描述当作性能证据；
- 把 H1/H2/H3 的研究假设写成已证实结论。

## 7. 本轮交付

1. 修正 `status.json`，使其反映 Phase-1A-10 最终决策及本计划分支/阶段。
2. 完成四个候选的原始产物和文献审计，产出 `docs/PHASE1A11_CANDIDATE_AUDIT.md` 与 `docs/PHASE1A11_LITERATURE_MATRIX.md`。
3. 完成 AES 当前状态和目标域实验准备度审计，产出 `docs/PHASE1A11_AES_READINESS_AUDIT.md`。
4. 产出 `docs/PHASE1A11_DECISION.md`，分别给出 Track A 与 Track B 的决定；不可用单个 NO-GO 把两条轨道一起关闭。
5. 更新交接提示词，记录真实 HEAD、预算边界、尚未执行的事项。
6. 运行可运行的离线测试（若只读审计未改代码，不应为追求测试数字而改动源码），检查 diff、commit 和远端同步。

本计划分支不代表候选已通过，也不授权任何真实 API 或性能实验。

## Phase-1A-11 clarification (2026-10-29): transfer is optional

The non-negotiable target is applying LLM-empowered evolutionary computation to improve Agent task performance. MetaBox-to-AES transfer is one possible experimental route, not the project objective itself and not a mandatory architecture. After Phase-1A-10/11 failed to validate a source-domain controller, the next design phase must compare the transfer route against direct LLM-assisted EC on AES Agent policies, with prior-art and negative-control audits for both. Neither route is presumed novel or effective. See `docs/PHASE1A11_DECISION.md` and `planner/phase1a12_executor_handoff.md`.
