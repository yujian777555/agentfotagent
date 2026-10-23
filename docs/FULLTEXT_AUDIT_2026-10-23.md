# 相关工作机制审查：2026-10-23（第一轮）

## 结论先行

当前最初的 H1 和 H3 都不能作为独立创新主张。H1“Agent 观察演化状态并在线改进算子”与 LLM4EO、LAOS、EoH、LLaMEA、AwesomeDE/LMCOEA 明显重叠；H3“Agent 与改进机制递归地互相改进”与 Hyperagents、DGM/HGM、CoCoEvolve、RSI-Router 等存在高重叠。H2“将 MetaBox 数值优化中得到的同一个控制对象迁移到结构化 Agent-genotype 搜索空间”仍可作为候选研究问题，但新颖性风险很高，尚未证实。

## 已核验的最近邻

| 工作 | 研究对象与机制 | 对本项目的限制 |
|---|---|---|
| EoH, ICML 2024 | LLM 在演化循环中同时改进启发式思路和可执行代码，使用变异/交叉和候选选择。论文与官方代码可访问。 | “LLM + 演化搜索来改进启发式”不是创新。 |
| LLaMEA / LLaMEA-HPO | LLaMEA 官方实现支持完整算法生成、变异/交叉、父代选择、多目标 Pareto archive、novelty/niching、adaptive mutation 与 feature-guided mutation；HPO 版本将结构设计和数值参数优化分离。 | 算法级进化、分离结构搜索与参数调优不能单独作为创新。官方代码已检查；LLaMEA PDF 在本轮读取器中超过内容限制。 |
| LLM4EO | 从演化状态、算子表现和停滞信息诊断搜索，按需进行算子级 meta-evolution；在柔性作业车间调度上评估。 | 直接否定泛化的“Agent 看轨迹、诊断停滞、在线修改算子”新颖性主张。 |
| LAOS (GECCO 2025) | 出版记录/摘要说明使用状态信息构建 LLM meta-prompt，做自适应算子选择。 | 与状态依赖 LLM 控制直接重叠。正文与官方代码本轮未获取，奖励定义、回放更新和详细消融仍待核验。 |
| AwesomeDE | 用 MetaBBO 元训练构建 LLM meta-optimizer，为约束演化算法生成更新规则，并跨约束问题族评估。 | “在 MetaBox/MetaBBO 上让 LLM 设计 EA 更新规则”并不足以区分。 |
| LMCOEA (ESWA 2026) | 出版记录/摘要说明 LLM 生成约束 EA 更新规则，并通过 evolutionary-learning Meta-BBO 迁移跨问题知识。 | 是高风险近邻；正文和官方代码本轮未获取，不能凭摘要推断细节。 |
| EvoAgent (NAACL 2025) | 演化专门化 Agent，并通过变异/交叉和质量检查生成多 Agent 系统。 | “EA 用于优化 Agent”不新。 |
| ARTEMIS | 将 Agent 当作黑盒，联合搜索混合类型配置，使用语义感知遗传算子和运行日志。 | Agent genome、prompt/configuration 的遗传搜索不新。 |
| GEPA | 反思式 prompt 变异、系统感知 merge、基于 Pareto 的候选 illumination。 | 反思、轨迹反馈和多任务 Pareto 保留不能单独作为贡献。 |
| DGM / HGM | DGM 维护自修改 coding-agent archive；HGM 估计谱系/后代生产力并以 Thompson sampling 选择扩展对象。 | archive-based RSI、谱系价值/后代生产力需直接对比。 |
| Hyperagents | task agent 与 meta-agent 组成可编辑程序，改进过程本身可被修改；报告 meta-level 改进跨域迁移。 | 通用递归自改进和“改进如何改进”不能单独作为 H3 创新。 |
| AIDE² / MASS | AIDE² 使用私有/留出评分接受自修改研究 Agent；MASS 交替进行演化式多 Agent workflow 优化与轨迹 SFT。 | 隐藏评估、递归工作流优化和交替自改进已有直接相关工作。 |
| Harmony Harness | 多目标组合式 harness 演化，分解通用机制与基准特定适配，报告跨基准迁移。 | 通用/特定机制分解、跨 benchmark transfer、Pareto harness evolution 都不是充分创新。 |
| RSI-Router / CoCoEvolve | 前者演化路由和技能并复用历史经验；后者检索完整进化历史、探测目标系统并验证候选修改。 | 历史检索、负经验、Pareto、验证式变异不能单独作为创新。 |

## 仍可审查的候选问题 H2

候选研究问题应缩窄为：**一个在数值优化域中学习/选择的明确控制对象，能否在不重新手写其策略语义的前提下，迁移到表示结构不同的 Agent-genotype 演化，并在独立任务上优于目标域直接自适应？**

这里“控制对象”尚未定义。它可能是：
1. 可执行的状态—动作规则；
2. 策略参数；
3. 学到的控制表示。

三者不能混为一谈。应先选一种，并说明哪些对象保持不变、哪些目标域映射需要学习，以及迁移收益如何与目标域训练区分。

### 最低区分性对照

- 目标域原始 EA；
- 目标域强传统自适应控制器；
- 目标域仅用开发集直接调优的控制器；
- 源域迁移的同一控制对象；
- 打乱 source-state → target-state/action 映射的负对照；
- 随机搜索；
- 固定通用控制器。

若“迁移”只是人工把 explore/exploit 等概念重新命名为 Agent 操作，或由 LLM 在目标域重新生成一套策略，就不构成强迁移证据。

## 证据限制与下一步

- LLM4EO、EoH、Harmony Harness、Hyperagents 等方法论文正文已检查；EoH、LLaMEA 官方代码已检查，但没有独立复现这些论文。
- LAOS 目前仅核验官方出版记录/摘要，未获取正文和官方实现。
- LMCOEA 目前仅核验 Elsevier 出版记录/摘要，未获取正文和官方实现。
- MetaBox-v2 官方 README/API 和 v2.0.0 版本入口已检查，但本项目尚未安装或执行。
- 下一步必须先补齐 LAOS/LMCOEA 的正文级机制差异审查，再审计候选 Agent 环境的可执行 genotype、评分器和真正的随机搜索基线。若无法定义非平凡的控制迁移对象，应在编码前调整或放弃 H2。
