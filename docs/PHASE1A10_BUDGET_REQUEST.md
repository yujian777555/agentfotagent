# Phase-1A-10 Budget Request

## 状态

**等待审批。未获批准不调用真实 API。**

## 申请额度

| 项 | 上限 |
|---|---|
| 真实 API 请求总数 | **24** |
| A 组（Trace-grounded）请求 | 12 |
| B 组（Trace-blind）请求 | 12 |
| 单次输出 token 上限 | 800 |
| 总 token 硬上限 | 120,000 |
| 自动重试 | **不允许** |
| 预检请求 | ≤3（计入总额度） |
| 模型 | `deepseek-flash`（禁止 `deepseek-v4-pro`） |

## 成本估算

### 价格依据

DeepSeek API 定价（deepseek-flash）：
- 输入：~¥0.1 / 百万 tokens（缓存未命中）
- 输出：~¥0.2 / 百万 tokens

**注意**：以上为公开参考价。API 响应中 **不返回实际费用字段**（`usage` 仅含 `prompt_tokens`、`completion_tokens`、`total_tokens`）。无法直接核实费用。

### 估算

| 项 | 估算 |
|---|---|
| 每次请求输入 tokens | ~1,500（任务卡 + 源码摘要 + 协议） |
| 每次请求输出 tokens | ~600（<800 上限） |
| 24 次请求输入总计 | ~36,000 |
| 24 次请求输出总计 | ~14,400 |
| 总 tokens | ~50,400（远低于 120,000 上限） |
| 估算费用（参考价） | ~¥0.01 |

### 费用无法核实时的处理

1. 如实记录 API 返回的 `usage` 字段（prompt_tokens、completion_tokens、total_tokens）
2. 在结果报告中注明"实际费用未由 API 返回，以 token 计量为账本"
3. 不声称费用已被验证或保证

## 记录字段

每次 API 调用记录：
- `request_id`（组 + task_id + 序号）
- `model`（精确版本标识）
- `prompt_hash`（提示词 SHA-256）
- `input_tokens`（API 返回的 prompt_tokens）
- `output_tokens`（API 返回的 completion_tokens）
- `api_calls`（=1）
- `timestamp`
- `response_raw`（完整响应，未修改）
- `parse_status`

## 预检计划

预检 ≤3 次请求，验证：
1. 模型标识为 `deepseek-flash`（检查响应 `model` 字段）
2. 返回合法 JSON 且包含全部 11 个必填字段
3. 不同任务卡产生不同的可解析方案

预检失败时立即停止，不消耗剩余额度。

## 审批条件

- [ ] 预算上限确认
- [ ] 价格依据确认
- [ ] 模型限制确认（仅 `deepseek-flash`）
- [ ] 停止条件确认

**审批人签字后方可启动 Stage B。**
