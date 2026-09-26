# B11 DevOps 课程项目

B11 负责 DRAFT（生成可构建环境）和 MDFixer（修复缺失依赖）。当前处于 E2 需求与接口契约阶段，已有接口文档、Schema、人工 JSON 样例、ADR 和文件校验用例；真实服务、API 部署和构建修复实验尚未实现。

## E2 材料入口

| 材料 | 内容 |
|---|---|
| [Backlog](docs/backlog.md) | B11 任务、责任角色、交付物、验收条件和状态 |
| [接口契约](docs/interface_contract.md) | 任务模型、服务输入输出、状态和错误码 |
| [Schema 说明](schemas/README.md) | JSON 结构约束及使用方法 |
| [JSON 样例](examples/README.md) | 请求、响应、失败和产物引用演示 |
| [DRAFT 逐轮记录](docs/draft_iterations.md) | 将来每轮修改、理由和步骤结果的格式 |
| [产物交接](docs/artifact_handoff.md) | 独立服务器间的 HTTP 下载与镜像加载约定 |
| [MD/RD 报告](docs/md_report.md) | 报告字段、证据及只修复 MISSING 的规则 |
| [ADR](docs/decisions/README.md) | 设计决定、备选方案与代价 |
| [AI_USAGE](AI_USAGE.md) | AI 建议、人工决定与验证边界 |
| [文件校验记录](docs/validation.md) | 检查版本、命令、结果和未验证范围 |
| [贡献记录](docs/contributions.md) | 实际 Git 作者及提交证据 |

FULL_CHECK、INCREMENTAL_CHECK 的材料用于说明上下游交接，不代表 B11 承担 A11 的服务实现。跨组约定目前为 B11 提案，待配对确认。

## 运行文件校验

在已安装 `jsonschema[format]` 的 Python 环境执行：

```bash
python -m unittest discover -s tests -v
```

独立环境的安装步骤见 [校验记录](docs/validation.md)。这些检查只验证接口文件，不执行真实构建、检测或修复。
