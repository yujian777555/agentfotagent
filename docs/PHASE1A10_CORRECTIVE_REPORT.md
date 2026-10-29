# Phase-1A-10 Corrective Report

## 修复内容

### A. 修复已有机制误判

**问题**: `check_known_mechanism()` / `check_closed_mechanism()` 扫描所有字段，候选在 `nearest_known_methods` 中引用 L-SHADE/SHADE 时被误判为重复。

**修复**: 仅扫描 `MECHANISM_FIELDS = ["algorithmic_change", "mathematical_rule"]`。引用/比较/反驳字段（`nearest_known_methods` 等）不参与判定。

**回归测试**: 3 项新增——引用 L-SHADE 不误拒绝、实际重提关闭机制被拒绝、已知机制在 mechanism 字段中被标记。

### B. 修复随机对照伪证据

**问题**: `generate_random_valid()` 编造函数编号和指标值。

**修复**: 使用冻结模板库（6 个真实算法组件 + 真实修改点）和 `REAL_EVIDENCE` 注册表（真实诊断值）。`observed_evidence` 改为结构化 dict（task_id, trace_path, function, seed, metric, observed_value）。

**回归测试**: 8 项新增——结构化证据验证、无伪造值、模板多样性。

### C. 修复重复检测

**问题**: `content_hash` 包含 `mechanism_id`，不同 ID 的相同机制不被识别为重复。

**修复**: `normalized_mechanism_hash` 排除 `mechanism_id`、`group`、`nearest_known_methods` 等非机制字段。

**回归测试**: 4 项新增——同机制不同 ID 检出重复、归一化哈希忽略 ID。

### D. 任务卡审计

TASK-04 代码 SHA 已修正：诊断工具 `354b7f9` vs 基线 `8d5af7f` 分别标注。全部 15 个轨迹文件引用已验证存在。

## 测试结果

| 项 | 修复前 | 修复后 |
|---|---|---|
| 评估器测试 | 31 | **39** |
| 全量测试 | 425 | **433** |
| exit code | 0 | **0** |
