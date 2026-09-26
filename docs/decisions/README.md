# E2 架构决策记录

本目录按“一项决策一份 ADR”维护；本索引提供查阅入口。独立文件记录决策状态、后续修订及其影响范围。

| 编号 | 决策 | 状态 | 记录 |
|---|---|---|---|
| ADR-001 | 耗时任务采用异步 Job | B11 决策草案，待 A11 确认 | [001-asynchronous-jobs.md](001-asynchronous-jobs.md) |
| ADR-002 | 用 `trace_id` 关联流程，用新 `job_id` 表示重试 | B11 决策草案，待 A11 确认 | [002-trace-and-retries.md](002-trace-and-retries.md) |
| ADR-003 | 通过逻辑 URI 传递产物 | B11 决策草案，待 A11 确认 | [003-artifact-uris.md](003-artifact-uris.md) |
| ADR-004 | 使用稳定的 `configuration_id` 标识构建环境 | B11 决策草案，待 A11 确认 | [004-configuration-id.md](004-configuration-id.md) |
| ADR-005 | 超时由调用方按任务设置 | 暂定，待 A11 确认 | [005-timeout-policy.md](005-timeout-policy.md) |
| ADR-006 | 限制 DRAFT 的迭代次数 | B11 决策草案，待 A11 确认 | [006-draft-iteration-limit.md](006-draft-iteration-limit.md) |
| ADR-007 | 只返回完整且验证通过的正式产物 | B11 决策草案，待 A11 确认 | [007-validated-artifacts.md](007-validated-artifacts.md) |
| ADR-008 | 区分执行错误与分析发现，MDFixer 只修复 MISSING | B11 规约草案，待 A11 确认 | [008-findings-and-errors.md](008-findings-and-errors.md) |
| ADR-009 | 按服务职责串联实验流程 | B11 决策草案，待 A11 确认 | [009-service-workflow.md](009-service-workflow.md) |

## 文档约定

- 每份 ADR 都包含背景、决策、备选方案分析和后果，记录回答“为什么选择该方案”。
- “备选方案分析”说明决策时可选方案及取舍。
- 字段名、状态值、错误码及请求/响应细节以 [接口契约](../interface_contract.md) 和 [Schema](../../schemas/README.md) 为准。
