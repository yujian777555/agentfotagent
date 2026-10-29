# Phase-1A-7 Method Selection

## 提案与审查过程

| 阶段 | 请求数 | 模型 | 结果 |
|---|---|---|---|
| Phase B 提案 | 3 | deepseek-flash | 5 个完整候选（mutation 2, memory 2, selection 1） |
| Phase C 审查 | 3 | deepseek-flash | **0 个 PASS，全部 FAIL** |
| **总计** | **6** | | 预算耗尽 |

## 候选汇总

| # | 候选 | 视角 | novelty_rating | verdict | 核心问题 |
|---|---|---|---|---|---|
| 1 | DGDD | mutation | MINOR_VARIANT | FAIL | 多样性 DE 参数重写 |
| 2 | FMF-DC | mutation | ALREADY_KNOWN | FAIL | F floor 已有 |
| 3 | Zero-Δf Veto | memory | ALREADY_KNOWN | FAIL | strict gate 已有 |
| 4 | CR Drift Dampening | memory | MINOR_VARIANT | FAIL | smoothing 参数化 |
| 5 | SIG-SM | selection | MINOR_VARIANT / ALREADY_KNOWN | FAIL | 已有 SHADAD 改进 |

## 判定依据

1. **3/3 独立审查均不通过**（0 PASS）——满足停止条件。
2. 所有候选的 `novelty_rating` 为 MINOR_VARIANT 或 ALREADY_KNOWN，无 NOVEL_MECHANISM。
3. 文献证据等级均为 SECONDARY，无法宣称创新性。
4. 按协议：不得再消耗 LLM 请求以诱导不同答案。

## 未执行的实验

Phase D 的 100-run pilot **未启动**。原因：门禁未通过。如果强行执行，结果只能反映已知机制的变体表现，不构成"具有明确机制差异的算法改进"。

## 有价值的副产物

Phase A 的 36 条细粒度诊断轨迹（24 指标/代 × 166 代 × 36 runs）为后续机制研究提供了**可信的证据基础**。6 个可观测模式（成功率-改进脱钩、CR 漂移、多样性坍缩、F 坍缩、种子分裂、高成功-大 regret 悖论）值得在下一阶段从不同角度重新审视。
