# Phase-1A-10 Experiment Protocol

## 核心研究问题

在固定基线、任务、模型、预算和评价协议下，**真实轨迹证据是否能提高 Agent 提出的演化算法改动的有效率？**

## 三组对比

| 组 | 名称 | 输入 | LLM |
|---|---|---|---|
| A | Trace-grounded Agent | 真实诊断轨迹 + 算法源码 + 任务卡 | `deepseek-flash` |
| B | Trace-blind Agent | 算法源码 + 问题描述（无轨迹） | `deepseek-flash` |
| C | Random-valid | 预定义随机改动生成程序 | 无 |

三组使用**相同**冻结基线（`lshade_canonical.py` @ `8d5af7f`）和任务范围（6 张任务卡）。

## Stage A（已完成，无 LLM）

| 子项 | 状态 | 产物 |
|---|---|---|
| A1 任务卡（6 张） | ✅ | `PHASE1A10_TASK_CARDS.md` |
| A2 输出协议 | ✅ | 11 字段 JSON schema |
| A3 候选评估器 | ✅ | `candidate_evaluator.py` |
| A4 离线验证 | ✅ | `test_phase1a10_evaluator.py`（31 项） |

## Stage B（等待预算审批）

### 预检（≤3 次请求）
- 验证模型身份为 `deepseek-flash`
- 验证返回合法完整
- 验证不同任务产生可解析方案
- 验证账本准确

### 正式生成
- 6 张任务卡 × A/B 各 2 个独立候选 = 最多 24 个生成请求
- 每次输出 ≤800 tokens
- 总 token 硬上限 120,000
- 固定模型版本、系统提示、生成参数
- 随机化请求顺序
- 保留原始请求/响应、提示词哈希、代码 SHA、token 账本

### C 组
- 离线随机改动生成程序（`generate_random_valid`）
- 数量与 A/B 实际有效候选匹配

## Stage C：独立候选审查

对去除组别标签的候选做三步审查：
1. 合法性（输出符合协议、不违反硬约束）
2. 新颖性（与最近邻逐项比较，不足时标 `NOVELTY_UNRESOLVED`）
3. 可实现性（映射到源码修改点，通过单元测试）

## Stage D：性能实验（仅通过审查时）

- 隔离分支实现
- 冻结 train split
- 对比：标准 L-SHADE vs 候选机制 vs 配对随机改动
- 同种子、同函数、同 FE 配对

## 统计与停止条件

主指标：各组通过全部门禁的候选比例；A vs B 配对差异。

停止条件：
- A 组未显示优于 B 组的可复核趋势
- 候选大多被已有方法覆盖
- A 组候选未超过 C 组
- 性能收益依赖单一种子/函数

## 评估器指标

1. 结构合法率
2. 证据可追溯率
3. 算法规则可实现率
4. 已有机制重复率
5. 通过独立审查的比例（Stage C）
6. 进入性能实验的比例（Stage D）
7. 性能收益与不确定性（Stage D）
8. token/API/FE 成本
