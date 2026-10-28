# Phase-1A-6 Historical Evidence Review

本文件对 Phase-1A-4R3、4R2、4R、5 的既有结果进行重分类。**不删除、不覆盖任何历史 manifest、轨迹或报告。**

## 1. 原始实验记录仍然存在

| 阶段 | 分支 | 核心产物 | 状态 |
|---|---|---|---|
| 4R3 | `phase1a-phase4r3-lshade-restart-benchmark` | `results/phase1a4r3/manifest_*.json`（600 runs） | 完整保留 |
| 4R2 | `phase1a-phase4r2-matched-control-fix` | `results/phase1a4r2/` | 完整保留 |
| 4R | `phase1a-phase4r-attribution-audit` | `results/phase1a4r/` | 完整保留 |
| 5 | `phase1a-phase5-evidence-guided-mechanism` | `results/phase1a5/` | 完整保留 |

以上产物均为 `lshade_reimpl.py`（当时称 "canonical L-SHADE reimplementation"）上产生的真实运行数据，**作为该实现的历史数据依然有效**。

## 2. 哪些结果不能再用于支持"标准 L-SHADE"的比较

由于 `lshade_reimpl.py` 与 Tanabe & Fukunaga 标准算法存在以下实质差异（详见 `PHASE1A6_BASELINE_AUDIT.md`）：

1. **N(t) 公式**：更早到达 N_min（非线性插值）；
2. **F 采样**：Normal 而非 Cauchy；
3. **F≤0 处理**：裁剪而非重采样；
4. **r1 可等于 r2**。

**影响判定**：

| 结论类别 | 可否外推到标准 L-SHADE | 说明 |
|---|---|---|
| "N+I 重启有害"（4R3: 3–107 vs L-SHADE） | **否** | 对照臂 `L_SHADE` 是旧实现，不是标准 L-SHADE |
| "线性 N 与进度脱钩是缺陷"（5 的动机） | **否** | 脱钩程度取决于旧公式；标准公式下 N(t) 更平缓 |
| "自适应 N = 改名"（5: NO_GO_NEW_MECHANISM） | **部分保留** | "改名"判定针对具体实现的触发器设计，逻辑不依赖 N(t) 公式；但数值阈值需重验 |
| "状态触发 ≤ 随机匹配"（4R/4R2） | **部分保留** | 控制实验设计（matched random）方法论成立；绝对数值不可外推 |
| "质量残差无益/有害"（3N2: 0–10） | **是** | 与 L-SHADE 无关，结论独立成立 |
| "LLM 不能做轨迹条件参数控制"（P1A-0/1） | **是** | 与 L-SHADE 无关 |
| "baseline-subtraction ≡ bucket UCB"（3R） | **是** | 数学恒等，与 L-SHADE 无关 |

## 3. 哪些轨迹诊断需要在修复后重新验证

| 诊断 | 来源 | 重验要求 |
|---|---|---|
| "N 过早坍缩到 4 限制探索" | 5/F10 轨迹摘要 | **必须**用标准 N(t) 重跑后判断 |
| "F1 约 1500 FE 收敛后仍继续缩 N" | 5 | **必须**重验（标准公式下 N 在 5000 FE 末端才到 4） |
| "F20 regret 为负" | 5 | **已定性**：非负 regret，是 optimum 非下界；新实现已分离字段 |
| "F21 三种子完全相同的 best" | 新基线（canonical）观察 | 需确认 F21 景观特性，非历史问题 |

## 4. 哪些结论与实现细节无关，仍然成立

1. **LLM 提示词回声/单吸引子行为**（Phase-1A-0/1）：纯模型行为，与优化器无关。
2. **质量残差 credit 估计在 best-arm 独立于 q 时无益/有害**（3N2）：基于仿真构造的统计事实。
3. **bucket-baseline subtraction 与 bucket UCB 排序恒等**（3R）：数学证明。
4. **matched-random 实验设计原则**（4R2）：方法论层面，任何实现上都应做此对照。
5. **FE 精确计数、函数身份核验流程**（adapter + 测试）：基础设施，与算法实现正交。
6. **MetaBox `Config()` 覆写 maxFEs、`difficulty='all'` 忽略用户列表** 等集成事实：平台行为。

## 5. 重新分类后的证据状态总结

```
仍然可信（跨实现）：
  ├── LLM 能力边界（P1A-0/1）
  ├── 质量残差 credit 方法论（3N2）
  ├── bucket-UCB 恒等（3R）
  ├── matched-random 对照设计（4R2 方法论）
  └── 平台/FE/身份基础设施

仅对 lshade_reimpl 实现有效（历史数据）：
  ├── 4R3: N+I vs 旧 L-SHADE 的 W-L-T（3-107）
  ├── 4R2: state vs matched（5-4）
  ├── 4R: N+I best / M harmful / stall dead
  └── 5: adaptive-N = renaming（数值阈值部分）

已废弃的解释：
  └── "标准 L-SHADE 线性 N 与进度脱钩是算法缺陷"
      （脱钩程度来自旧公式；标准公式下需重测）

已修正的指标语义：
  └── F20 "regret" 负值 → 实为 benchmark_cost；optimum 非严格下界
```

## 6. 后续使用规则

1. 引用 4R3/5 数值时，必须标注 **"基于 lshade_reimpl（非标准公式）"**。
2. 不得将 "N+I 有害" 直接表述为 "对标准 L-SHADE 加 N+I 有害"。
3. 新的机制比较必须以 `lshade_canonical.py` 为基线臂。
4. F20 上的指标一律称 `benchmark_cost`，不得称 `regret`。
