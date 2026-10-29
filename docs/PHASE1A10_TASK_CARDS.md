# Phase-1A-10 Design Task Cards

6 张任务卡，来源均为 Phase-1A-7/8 的真实诊断轨迹。每张覆盖不同的机制现象，不重复同一问题。

---

## TASK-01: 成功率-改进脱钩（零改进"成功"污染记忆）

**task_id**: `TASK-01-zero-improvement-success`
**轨迹来源**: `results/phase1a7/diagnostic_traces/F07_s22.json`, `F07_s33.json`, `F21_s*.json`
**代码 SHA**: `8d5af7f` (lshade_canonical.py)
**manifest**: `results/phase1a7/diag_manifest.json`

**现象**: F7 s=22 最后 20 代成功率 0.824 但 stall_gen=53；F21 全部种子成功率 1.000 但 best 纹丝不动（786.565）。大量 trial 满足 `trial ≤ parent` 但 Δf≈0，污染 M_F/M_CR 记忆。

**设计目标**: 减少零改进样本对成功记忆的影响，使记忆更新反映真实改进。

**已关闭机制**: F/CR 记忆平滑、零改进门控（Phase-1A-7 审查判定 ALREADY_COVERED）。**注意：仅"gate Δf>0"已被覆盖；需要更实质的机制差异。**

**可观测预期**: 晚期 M_F/M_CR 不被 Δf≈0 样本拉偏；最终 best 改善。

**否证条件**: 若在 F7/F21 上候选机制与标准 L-SHADE 的最终 best 无差异（配对 p>0.05），或在 F1（控制组）上退化。

---

## TASK-02: CR 记忆正反馈漂移至极端

**task_id**: `TASK-02-cr-memory-drift`
**轨迹来源**: `results/phase1a7/diagnostic_traces/F01_s*.json`, `F06_s*.json`, `F10_s*.json`
**代码 SHA**: `8d5af7f`
**manifest**: `results/phase1a7/diag_manifest.json`

**现象**: 9/12 函数 CR_mean 从 ~0.5 漂移到 >0.85 或 <0.05。F1: 0.52→0.85, F6: 0.51→0.95, F10: 0.50→0.98, F20: 0.52→0.02。正反馈机制。

**设计目标**: 打破 CR 记忆的正反馈循环，使 CR 保持在有效范围。

**已关闭机制**: F/CR 记忆平滑（Phase-1A-7 审查判定 ALREADY_COVERED）。**注意：简单的指数平滑已被覆盖；需要不同的机制。**

**可观测预期**: 晚期 CR_mean 保持在 [0.2, 0.8]；多样性下降速率减缓。

**否证条件**: 若 CR 仍漂移至极端，或性能下降。

---

## TASK-03: F 记忆坍缩致差分向量消失

**task_id**: `TASK-03-f-collapse`
**轨迹来源**: `results/phase1a7/diagnostic_traces/F04_s*.json`, `F11_s11.json`, `F15_s*.json`
**代码 SHA**: `8d5af7f`
**manifest**: `results/phase1a7/diag_manifest.json`

**现象**: F4: F_mean 0.58→0.06-0.13, F11 s=11: 0.53→0.08, F15: 0.59→0.15-0.32。F→0 使差分向量消失，搜索退化为微小扰动。

**设计目标**: 保持 F 在有效范围，防止差分向量消失。

**已关闭机制**: F floor + 补偿（Phase-1A-7 审查判定 ALREADY_KNOWN）。**注意：简单 F floor 已被覆盖。**

**可观测预期**: 晚期 F_mean 不低于 0.1；差分向量 L2 保持有效。

**否证条件**: 若 F 仍坍缩，或强行保持 F 导致收敛变慢。

---

## TASK-04: 修复 trial 成功率系统性偏低

**task_id**: `TASK-04-repair-success-gap`
**轨迹来源**: `results/phase1a8/stage_a_traces/F*_s*.json`（boundary 诊断）
**代码 SHA**: `354b7f9` (lshade_boundary_diag.py)
**manifest**: `results/phase1a8/stage_a_manifest.json`

**现象**: 全函数全种子一致：修复 trial 成功率低于未修复 trial（F1: 0.30 vs 0.48, F7: 0.12 vs 0.36, F10: 0.12 vs 0.33）。修复位移 cosine ≈ -0.4 至 -0.65（与搜索方向相反）。

**设计目标**: 减少边界修复对 trial 质量的损害，或利用修复事件信息改进搜索。

**已关闭机制**: archive×boundary 交互（Phase-1A-8 NO_GO）。**注意：2×2 交互实验已关闭；但修复 trial 的成功率问题是独立观测。**

**可观测预期**: 修复 trial 成功率提高至接近未修复 trial。

**否证条件**: 若修复 trial 成功率无改善，或改善仅来自减少超界次数。

---

## TASK-05: 种子间行为分裂

**task_id**: `TASK-05-seed-bifurcation`
**轨迹来源**: `results/phase1a7/diagnostic_traces/F11_s11.json` vs `F11_s22.json` vs `F11_s33.json`
**代码 SHA**: `8d5af7f`
**manifest**: `results/phase1a7/diag_manifest.json`

**现象**: F11 s=11: 多样性 0.175（未坍缩）、成功率 0.041、stall=6；s=22/33: 多样性 0.000、收敛到 <1000。同一函数不同种子进入完全不同搜索状态。

**设计目标**: 降低种子敏感性，使算法行为更一致。

**已关闭机制**: 无直接覆盖。但"降低种子敏感性"过于泛化，需要具体机制。

**可观测预期**: F11 三种子最终 best 方差降低。

**否证条件**: 若种子间方差不降低，或平均性能下降。

---

## TASK-06: 高成功率与大 regret 并存

**task_id**: `TASK-06-success-regret-gap`
**轨迹来源**: `results/phase1a7/diagnostic_traces/F10_s*.json`
**代码 SHA**: `8d5af7f`
**manifest**: `results/phase1a7/diag_manifest.json`

**现象**: F10 晚期成功率 0.21-0.62（高于早期），但 best_raw 仍 2.4e4-1.7e5。高条件数景观中"成功"不代表有意义的改进。

**设计目标**: 区分有意义改进与微小改进，使搜索资源集中在有效改进上。

**已关闭机制**: 质量残差 credit（Phase-1A-3N2 NO_GO）。**注意：credit 估计已关闭；但"成功≠改进"的观测是独立的。**

**可观测预期**: 在 F10 上最终 best 改善，同时在 F1（控制组）上不退化。

**否证条件**: 若 F10 无改善，或 F1 退化超过 5%。
