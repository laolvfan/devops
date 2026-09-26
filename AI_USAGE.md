# AI_USAGE

## 使用范围

AI 协助整理 E2 接口契约、解释字段含义，并起草 ADR 与本记录。AI 输出作为建议和草稿；B 组成员结合课程要求形成接口提案，跨组字段、取值和规则待 A11 确认后定稿。未完成 A/B 确认的内容在 ADR 和契约中继续标注为暂定或待确认。

- 工具与模型：OpenAI Codex，GPT-6
- 提示摘要：依据 E2 PPT 和本地成果整理 ADR 与 AI_USAGE；将用户提供的 ADR-001 至 ADR-009 及旧 AI_USAGE 记录纳入文档，并核对状态和实现边界。
- 关联规约：[接口契约](docs/interface_contract.md)

## 建议与人工决定

| 主题 | AI 提议 | 人工决定 | 处理 |
|---|---|---|---|
| 任务执行方式 | 对耗时操作采用异步 Job，创建后返回任务编号，再查询状态和产物。 | 采用异步 Job；创建返回 HTTP 202，使用 GET 查询任务。 | 采纳；对应 ADR-001。 |
| 任务关联与重试 | 使用 `trace_id` 关联流程；重试创建新的 `job_id` 并保留 `trace_id`。 | 保留该规则，并用 `retry_of_job_id` 指向上一次任务。 | 采纳；对应 ADR-002。 |
| 执行元数据 | 用 `execution` 记录 attempt、时间戳、耗时和超时预算。 | `execution` 由服务端生成；调用方提供 `timeout_seconds`，attempt 从 1 开始。 | 采纳并明确字段责任；对应 ADR-005。 |
| 产物读取 | 使用与存储实现无关的逻辑 URI，最初映射到生产方项目目录。 | URI 不包含阶段名；当前契约映射到项目根目录 `artifacts/`，两组独立部署后补充 HTTP 下载读取层。 | 采纳并按项目命名要求调整；对应 ADR-003。该映射是契约约定，当前样例不证明产物已存在或可读取。 |
| `configuration_id` | 使用稳定命名标识构建环境，环境变化时更新。 | 采用 `cfg-系统-工具链-模式-版本`；影响构建结果的配置变化必须生成新 ID。 | 采纳；对应 ADR-004。 |
| DRAFT 迭代次数 | 建议设置默认值和上限，防止反复修复无界执行。 | 默认 20 次，允许 1 至 50 次。 | 人工确定具体值；对应 ADR-006。 |
| `timeout_seconds` | 旧记录中的 AI 初始建议是通过多次试运行估算，再按历史耗时增加余量。 | 认为试运行会增加构建成本且不能保证后续耗时；改为调用方按任务类型、项目规模和资源保守设置，不设统一默认值，计时不含排队时间。 | 拒绝初始方案，采用修订方案；ADR-005 标为暂定。 |
| 失败产物 | 失败任务只返回错误和日志引用。 | 禁止输出半成品；`FAILED`、`TIMED_OUT`、`CANCELLED` 时 `output` 为 `null`。 | 采纳并明确为强约束；对应 ADR-007。 |
| 错误码 | 按错误来源分类，区分请求、产物、环境、执行、分析和修复错误。 | 采用对应分类与错误码，并区分工具失败和正常 MD/RD 发现。 | 采纳后由人工补充具体码表；对应 ADR-008。 |

## 人工检查记录

- **决策状态：** 上表记录 B 组形成的提案和人工决定；超时策略仍为暂定。接口字段、样例及产物 URI 的读取方式待 A11 确认。
- **核对范围：** 对照 E2 需求与接口契约 PPT，检查本记录和 ADR；并阅读 `docs/interface_contract.md`、`docs/md_report.md`、`schemas/`、`examples/` 和 `tests/`，核对文档、Schema 与样例中的字段和规则。
- **ADR 整理阶段的验证边界：** 该阶段仅做文档一致性检查，未运行文件校验或 DRAFT、BuildChecker、EChecker、MDFixer。接口样例为人工构造，不代表真实构建、检测或修复结果。
- **版本与关联记录：** 整理开始时仓库 HEAD 为 `0c4162f`（`Schema, JSON examples and MD_report`）。ADR-001 至 ADR-009 的索引见 [`docs/decisions/README.md`](docs/decisions/README.md)。

## Schema、样例与报告的辅助设计

- 工具与模型：OpenAI Codex，GPT-6。
- 提示摘要：对照 E2 课件检查缺项；解释 Schema、JSON 和 MD/RD；逐步补齐 Schema、接口样例及 MD 报告。
- AI 建议：将已有接口约定转成 JSON Schema；用人工样例串联产物引用；允许 MD/RD 混合报告，MDFixer 只修复 MISSING；增加结构与一致性校验。
- 人工决定：同意依次编写上述材料，先按 B11 提案推进、之后按 A11 反馈修改；明确区分文件校验与真实服务运行；要求文档不标注日期。
- 实现边界：无 MD 时拒绝修复请求、报告字段与细节由 AI 起草并记录为 B11 提案；不能由“写好报告”的授权推断所有细节均经逐项人工审定或 A11 确认。
- 关联版本：[0c4162f](https://github.com/laolvfan/devops/commit/0c4162f618a7fcafe43660c285cec9029416a622)。产物包括 schemas/、examples/、tests/ 和 docs/md_report.md。
- 验证：完成文件结构与一致性校验；随后在 a434baa 版本再次执行，18 项全部通过。命令、范围与限制见 [校验记录](docs/validation.md)。人工样例中的成功状态不是真实执行结果。

## E2 提交材料整理

- 提示摘要：拉取 E2 最新版本后检查 B11 交付缺项，并继续补充；不确定的细节与成员讨论。
- 人工约束：只安排 B11 的工作；成员暂以 A/B/C 表示；不使用“待负责人审阅”状态；不要求每人单独提交 SHA 清单。
- AI 工作：按 Git 实际作者整理贡献证据，编写 B11 Backlog 和校验记录，修正 README 的成果描述；未将计划分工当作实际贡献。
- 关联文件：[Backlog](docs/backlog.md)、[贡献记录](docs/contributions.md)、[校验记录](docs/validation.md)。本轮变更尚未提交，后续以实际 commit 关联。

## 独立部署的产物交接

- 人工决定：两组将分别部署服务器，同意继续完善 HTTP 文件交接方案，不要求共享整个实现仓库。
- AI 补充：保留逻辑 URI，按生产任务类型配置组入口，约定 HTTP 下载路径；镜像沿用 image.tar，增加 image_ref 标签说明及导出/加载操作。镜像传输细节是 B11 当前方案，待对接确认。
- 关联材料：[产物交接说明](docs/artifact_handoff.md)、ADR-003、接口契约及 DRAFT 成功样例。
- 验证边界：核对 Docker 官方命令说明及文件一致性，不实际访问示例地址、运行 Docker 或部署下载服务。本轮改动尚未提交。

## DRAFT 逐轮记录格式

- 人工决定：明确当前尚无构建环境或真实日志，同意先定义记录格式，再由未来的真实运行生成数据。
- AI 工作：定义轮次、修改、理由、镜像构建/项目构建/验证结果，提供 MANUAL_EXAMPLE 样例和独立 Schema；成功响应通过 iteration_record_uri 引用记录。
- 关联文件：[格式说明](docs/draft_iterations.md)、[Schema](schemas/draft-iterations.schema.json)、[人工样例](examples/artifacts/draft-iterations.json)。
- 验证：当前工作区共 23 项文件校验通过，包括新增 5 项逐轮记录校验。未运行 Docker、make 或真实验证命令，未创建示例 URI 所指向的日志。
