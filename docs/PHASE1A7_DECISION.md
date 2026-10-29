# Phase-1A-7 Decision

## 决策

**NO_GO_NEW_MECHANISM**

5 个候选在 3 次独立审查中全部 FAIL（0 PASS）。没有任何候选达到 NOVEL_MECHANISM 评级。按协议停止算法实验，不启动 100-run pilot。

## 门禁核对

| 门禁 | 状态 | 证据 |
|---|---|---|
| Phase A 逐位一致性 | ✅ | 36/36 bitwise identical |
| Phase B 提案（3 请求） | ✅ | 5 个完整候选，引用真实轨迹证据 |
| Phase C 独立审查（3 请求） | ❌ | 0 PASS / 5 FAIL |
| 最近邻可核验 | ❌ | 全部 SECONDARY 证据 |
| 可消融独立贡献 | ❌ | 审查判定 UNCONTROLLABLE 或 PARTIALLY |
| LLM 预算 | ✅ | 6/6 请求，未超 |
| 历史结果覆盖 | ✅ | 无 |
| main 修改 | ✅ | 无 |

## 审查结果摘要

| 候选 | novelty | verdict |
|---|---|---|
| DGDD | MINOR_VARIANT | FAIL |
| FMF-DC | ALREADY_KNOWN | FAIL |
| Zero-Δf Veto | ALREADY_KNOWN | FAIL |
| CR Drift Dampening | MINOR_VARIANT | FAIL |
| SIG-SM | MINOR_VARIANT / ALREADY_KNOWN | FAIL |

## 有价值的副产物

**Phase A 诊断轨迹**（36 runs × 166 gens × 24 metrics）保留为后续研究基础：

1. **成功率-改进脱钩**：F7/F21 中大量 Δf≈0 的"成功"污染记忆
2. **CR 记忆正反馈漂移**：9/12 函数 CR → 极端值
3. **多样性不可逆坍缩**：与 N→4 叠加
4. **F 记忆坍缩**：差分向量消失
5. **种子行为分裂**：F11 不同种子进入不同搜索状态
6. **高成功-大 regret 悖论**：F10 中成功≠有意义改进

这些模式是**真实轨迹观测**，不依赖任何新算法主张。

## 下一步

1. 基于已识别的 6 个机制模式，从**不同角度**（非 DE 参数控制）审视改进空间
2. 考虑文献中较少被关注的机制（如 archive 语义、p-best 选择偏差、边界处理交互）
3. 如再次动用 LLM，需为每视角提供更具区分性的轨迹证据，避免输出落入已知变体
4. **不得重开**已关闭路线（CC-SOC、质量残差、IPW/DR、N+I、自适应 N）

## 元数据

| 项 | 值 |
|---|---|
| 分支 | `phase1a-phase7-trace-guided-mechanism` |
| 基线 SHA | `8d5af7f` |
| LLM 请求 | 6（3 提案 + 3 审查），模型 `deepseek-flash` |
| Pilot 运行 | 0（未执行） |
| validation/test 访问 | 无 |
