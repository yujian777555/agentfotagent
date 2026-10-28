# Phase-1A-6 Baseline Audit

审计对象：`experiments/metabox/agent_assisted_ec/lshade_reimpl.py`（Phase-1A-4R3 / 4R2 / 4R / 5 全部历史实验所用实现）。

审计范围：种群缩减公式、参数采样、变异/档案/选择、函数评价与 regret 语义、FE 计数与函数身份。

证据来源：
- 本仓库代码与测试；
- `results/phase1a4r3/manifest_a4r3-*.json`、`results/phase1a5/lshade_trajectory_summary.txt`；
- MetaBox `metaevobox==2.0.2`（`D:\metabox-env\Lib\site-packages\metaevobox\`，git SHA `5565a281`）；
- `bbob_numpy.py` / `basic_problem.py` 源码级核对；
- 对 F1/F6/F10/F20/F24 的独立探针（eval vs optimum vs 随机搜索可达值）。

术语约定（下文严格区分）：
- `raw_objective`：`problem.eval(x)` 的实际返回值（含 BBOB bias）。
- `optimum`：`problem.optimum` 属性值（构造时 `func(get_optimal())`）。
- `benchmark_cost`：`raw_objective - optimum`。**不是** regret。
- `regret`：仅当已验证 `raw_objective ≥ optimum` 恒成立时才允许使用。

---

## A. 种群缩减

**预期语义（Tanabe & Fukunaga, CEC 2014 L-SHADE）**

```
N_target = round(N_init + (N_min - N_init) * FE / max_FE)
```

等价形式 `round((N_init - N_min) * (max_FE - FE) / max_FE + N_min)`。端点：FE=0 → N_init；FE=max_FE → N_min。单调不增。

**实际实现**（`lshade_reimpl.py:113`）

```python
n_target = max(n_min, int(round(n_init * (1.0 - fes / max_fes))))
```

即 `max(N_min, round(N_init * (1 - t)))`，趋向 0 后被 `N_min` 截断。

**差异量化**（N_init=100, N_min=4, max_FE=5000）

| FE | t | 标准 | 现实现 | 偏差 |
|---:|---:|---:|---:|---:|
| 0 | 0 | 100 | 100 | 0 |
| 2500 | 0.5 | 52 | 50 | −2 |
| 4800 | 0.96 | 8 | 4 | −4 |
| 5000 | 1.0 | 4 | 4 | 0 |

现实现**更早**到达 N_min。取整方式不同（`int(round())` 后 `max` vs 直接 `round` 插值）。

**缩减时的删除规则**：`np.argsort(fit)[:n_target]` — 删除最差个体，符合标准。✓

**影响范围**：4R3、4R2、4R、5 全部轨迹的 N(t) 曲线均非标准 L-SHADE。`n_history` 诊断（"N 过早坍缩"）描述的是本实现的公式行为，**不能**外推为标准 L-SHADE 的算法缺陷。

**修复**：`lshade_canonical.linear_n_target()` 使用标准插值公式；回归测试覆盖端点与中点。

---

## B. 参数采样

**预期语义**

| 量 | 分布 | 边界 |
|---|---|---|
| F | **Cauchy**(M_F[ri], 0.1) | F>1 → 1；F≤0 → 重新采样（至多有限次后取 1） |
| CR | **Normal**(M_CR[ri], 0.1) | 裁剪至 [0,1] |

成功历史更新（成功集合 S 非空时）：
- 权重 `w_i = |Δf_i|`；Σw=0 时退化为均匀权重；
- `M_F ← Lehmer: Σ w·F² / Σ w·F`；
- `M_CR ← 加权算术平均: Σ w·CR / Σ w`；
- 写入 `k_pos` 后 `k_pos = (k_pos+1) mod H`；**S 为空时不更新、不推进 k_pos**。

M_F、M_CR 初始化为 0.5（H=5）。0.5 是初始化值，不是"未定义"哨兵。

**实际实现**（`lshade_reimpl.py:132-133`）

```python
F  = float(np.clip(rng.normal(M_F[ri], 0.1), 0.0, 1.0))
CR = float(np.clip(rng.normal(M_CR[ri], 0.1), 0.0, 1.0))
```

| 量 | 标准 | 现实现 | 判定 |
|---|---|---|---|
| F 分布 | Cauchy | **Normal** | **实质性差异** |
| F≤0 | 重新采样 | 裁剪为 0 | 差异 |
| F>1 | 裁剪为 1 | 裁剪为 1 | 一致 ✓ |
| CR 分布 | Normal | Normal | 一致 ✓ |
| CR 边界 | 裁剪 [0,1] | 裁剪 [0,1] | 一致 ✓ |
| M_F 更新 | Lehmer | Lehmer | 一致 ✓ |
| M_CR 更新 | 加权算术平均 | 加权算术平均 | 一致 ✓ |
| 空 S 处理 | 不更新 | 不更新 | 一致 ✓ |

**影响范围**：Cauchy 重尾 vs Normal 轻尾会改变 F 的有效分布与搜索步长；这是算法级差异，历史轨迹不能代表标准 L-SHADE 的参数自适应行为。

**修复**：`sample_f()` 用 Cauchy（`m + 0.1·tan(π(u−0.5))`）+ 标准边界规则；`sample_cr()` 保持 Normal + 裁剪。回归测试检验分布矩与边界行为。

---

## C. 变异、档案与选择

### C.1 变异算子（current-to-pbest/1/bin）

**预期**：`mutant = x_i + F·(x_pbest − x_i) + F·(x_r1 − x_r2)`
- `pbest` 从当前种群 top `max(2, ⌈p·N⌉)` 中均匀抽取；
- `r1` 从种群抽取，`r1 ≠ i`；
- `r2` 从 种群 ∪ 外部档案 抽取，`r2 ≠ i` 且 `r2 ≠ r1`。

**实际**（`lshade_reimpl.py:135-146`）：公式正确。索引排除：`a`（r1）来自 `j≠i` ✓；`b`（r2）来自 `idxs+archive`，**未排除 `b == a`**。

**判定**：**MINOR GAP** — r1、r2 可能相同，违反 `r1 ≠ r2`。

**修复**：canonical 中 r2 抽样时显式排除 r1。

### C.2 p-best 候选

现实现 `max(2, int(N * p_best))`（向下取整）。标准常用 `max(2, round(N·p))` 或 `ceil`。差异在 N 较小时可忽略；canonical 采用 `max(2, int(N * p_best))` 并在文档中标注与论文取整可能的偏差。

### C.3 外部档案

- 插入：父代被替换时入档 ✓。
- 容量：插入后 `if len(archive) > N: archive.pop(random)` — 容量为**当前** N ✓（论文 "size = NP"；部分实现固定为 N_init，此处取论文字面义并记录）。
- 缩减同步：线性缩减 N 时不主动裁剪档案，直到下次插入才生效。标准未强制要求同步；canonical 选择**缩减时同步裁剪到新 N**，使容量不变量始终成立。

### C.4 交叉

`bin` 交叉，强制至少一位来自 mutant（`cross[rng.randint(dim)] = True`）✓。

### C.5 边界处理

现实现 `np.clip(mutant, lb, ub)`。SHADE 系论文部分版本采用"在边界与父代分量之间均匀重采样"。clip 是广泛使用的简化。canonical 保留 clip 并**显式标注为与论文可能的差异**。

### C.6 父子代选择

现实现 `if tf < fit[i]`（严格小于）。论文常见 `≤`。canonical 采用 `<=`（并注明连续目标下二者几乎等价）。

### C.7 初始化与终止

- 初始化：`rng.uniform(lb, ub, (N, dim))`，N_init=100 ✓。
- 终止：`while fes < max_fes`，最后一个不完整 generation 从 `if fes >= max_fes: break` 截断 ✓。
- 初始化评价计入 FE ✓（见 E）。

---

## D. 函数评价与 regret — 阻断性门禁

### D.1 `eval` 实际返回什么

沿调用链核实（`metaevobox.environment.problem.basic_problem.Basic_Problem.eval` → `bbob_numpy.py` 各 `F*.func`）：

1. `eval(x)` 对 1D 输入调用 `func(x.reshape(1,-1))[0]`；
2. `func` 返回 **含 bias 的原始目标函数值**（例：F1 `func` = `sum(z²) + bias`，bias=700）；
3. **不减去最优值**，不做 cost/regret 变换；
4. 对确定性 BBOB（本套件）无噪声，同输入同输出（已探针验证）。

**结论：`eval` 返回 `raw_objective`。**

### D.2 `problem.optimum` 是什么

构造函数（`bbob_numpy.py:52`）：

```python
self.optimum = self.func(self.get_optimal().reshape(1, -1))[0]
```

即在 `get_optimal()`（= shift 向量）处的函数值。`bias` 字段与该值一致（F1 bias=700, F20 bias=2100, F24 bias=1200）。

### D.3 F20 负 regret 的具体原因

历史证据（`results/phase1a5/lshade_trajectory_summary.txt`）：

```
L-SHADE F20 seed=11: best_raw=2049.66 regret=-50.3409
L-SHADE F20 seed=22: best_raw=2036.14 regret=-63.8565
L-SHADE F20 seed=33: best_raw=2039.21 regret=-60.7912
```

独立探针（本审计）：

| 函数 | optimum | eval(xopt) | 2000 次随机+局部搜索 best | 可低于 optimum？ |
|---|---:|---:|---:|---|
| F1 | 700 | 700.0 | 703.98 | 否 |
| F6 | 400 | 400.0 | 465.58 | 否 |
| F10 | 600 | 600.0 | 54372 | 否 |
| **F20** | **2100** | **2100.0** | **2091.65**（历史 L-SHADE 达 2036） | **是** |
| F24 | 1200 | 1200.0 | 1300.16 | 否 |

F20 = Schwefel（`bbob_numpy.py:1539`）。其 `func` 含复杂的 shift/scale/串行耦合变换：

```python
z = 2 * sign(shift) * x
z[:, 1:] += 0.25 * (z[:, :-1] - tmp[:-1])
z = 100 * (scales * (z - tmp) + tmp)
return b - 0.01 * mean(z * sin(sqrt(|z|))) + 100*pen + bias
```

`optimum = func(xopt) = 2100`，但该实现的景观在其它点可取到 **低于 2100** 的值。因此 `optimum` **不是** `raw_objective` 的严格下界。

**原因归类**：MetaBox 2.0.2 BBOB F20 实现中，所提供的 `xopt`（= shift）并非该变换后函数的真实全局最小点（Schwefel 多峰 + 串行耦合放大了偏差）。这是 **基准套件的 optimum 语义问题**，不是 L-SHADE 优化器越界。

### D.4 指标语义规则（强制）

| 字段 | 定义 | 允许调用 "regret"？ |
|---|---|---|
| `raw_objective` | `eval` 返回值 | 否（那是原始目标） |
| `benchmark_cost` | `raw_objective − optimum` | **否**（可为负） |
| `regret` | 仅当全轨迹验证 `raw ≥ optimum` 后，才可 `:= benchmark_cost` | 是（需逐函数核验） |

历史 `regret_curve` 字段实际存储的是 `benchmark_cost`。**F20 的负值是 benchmark_cost，不是负 regret。**

**修复**：canonical 结果对象分离记录 `raw_objective` / `benchmark_cost` / `optimum`，`regret` 仅在验证非负后填入，否则为 `None`。回归测试覆盖 F20 负 cost 语义。

---

## E. FE 与函数身份

### E.1 FE 计数

| 检查项 | 结论 | 证据 |
|---|---|---|
| 初始化评价计入预算 | ✓ | `fes = N` 后才进循环 |
| 每次 trial 计 1 次 | ✓ | `counting(trial)` 后 `fes += 1` |
| 无重复计数 | ✓ | 独立 `counting` 包装只在 eval 时 +k |
| 算法 FE == 独立 FE | ✓ | 历史 manifest `fes==indep==max_fes`（10000/5000 均成立） |
| 超预算 | 无 | `while fes < max_fes` + 内层 break |

注意：MetaBox 自带 `problem.FES` **不可靠** — 构造时 `func(xopt)` 已计 1 次，且 `reset()` 只重置计时 `T1` 不重置 `FES`。项目一律使用独立 FE 计数器（`adapter.FECounter` / 内联 `counting`）。✓

### E.2 函数身份

`adapter.load_function`：`difficulty=None` + `user_train_list=[fid]` 官方过滤分支；从类名 `F{id}` 反解析 `actual_id` 并与请求比对，不一致即抛错。

本审计探针：F1→`F1`, F6→`F6`, F20→`F20`, F24→`F24`，`eval(xopt)==optimum` 均成立。✓

### E.3 train split

`adapter.SPLIT_V2_TRAIN = (1, 2, 4, 6, 7, 10, 11, 12, 15, 18, 20, 21)` — 12 个函数。
4R3 manifest `protocol.functions` 与此完全一致。✓
冻结清单以 `adapter.split_manifest("split_v2")` 为准（含 `manifest_hash`）。

---

## 差异汇总

| # | 项 | 严重度 | 影响 | 状态 |
|---|---|---|---|---|
| 1 | N(t) 公式非标准 | 高 | 全部历史轨迹非标准 L-SHADE | canonical 已修复 |
| 2 | F 用 Normal 而非 Cauchy | 高 | 参数自适应行为不同 | canonical 已修复 |
| 3 | F≤0 裁剪而非重采样 | 中 | 尾部行为不同 | canonical 已修复 |
| 4 | r1 可等于 r2 | 低 | 偶发退化变异 | canonical 已修复 |
| 5 | 缩减时档案不同步 | 低 | 容量不变量短暂破坏 | canonical 已修复 |
| 6 | 选择用 `<` 而非 `≤` | 信息 | 连续目标下几乎无差别 | canonical 用 `≤` |
| 7 | 边界 clip | 信息 | 与部分论文重采样方案不同 | 记录为约定 |
| 8 | `regret` 命名错误（实为 benchmark_cost） | 阻断级语义 | F20 出现负值 | canonical 分离字段 |
| 9 | F20 optimum 非严格下界 | 套件性质 | 该函数上 cost 可为负 | 记录；不调用 regret |

FE 计数、函数身份、train split 三项均可验证，**通过**。

---

## 修复方式

1. 新增 `experiments/metabox/agent_assisted_ec/lshade_canonical.py`
   （`canonical_reimplementation; not official code`），不动 `lshade_reimpl.py`。
2. 独立测试 `tests/test_phase1a6_lshade_canonical.py` 覆盖任务书 §4 全部 10 项。
3. 基线重建仅使用 canonical 实现，配置先冻结再执行。
4. 历史结果按 `PHASE1A6_HISTORICAL_EVIDENCE_REVIEW.md` 重分类，不删除、不覆盖。
