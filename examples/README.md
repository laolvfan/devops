# A11/B11 E2 接口样例

这些文件是人工构造的接口演示，不是工具运行结果，也不是双方已确认的接口。仓库使用 example.com，提交 SHA、时间、退出码和发现均为虚构数据，不可据此宣称构建或修复成功。

## 阅读顺序

| 目录 | 创建接口 | 演示内容 |
|---|---|---|
| draft | POST /v1/dockerfile-jobs | 在 C0 生成环境；请求省略 max_iterations，查询结果补为 20 |
| full_check | POST /v1/full-check-jobs | 使用环境在 C0 生成依赖图 |
| incremental_check | POST /v1/incremental-check-jobs | 使用 C0 基线检测 C1，发现一条 MD |
| repair | POST /v1/repair-jobs | 在 C1 消费该 MD 报告，输出补丁和验证结果 |

每个目录包含：

- `request.json`：POST 请求体，Content-Type 为 application/json。
- `accepted.json`：HTTP 202 响应体，尚未执行完成。
- `succeeded.json`：GET /v1/jobs/{job_id} 的 HTTP 200 完整成功响应。
- `failed.json`：另一个独立失败任务的 HTTP 200 查询响应；任务失败不表示查询 HTTP 失败。失败任务使用单独的 job_id/trace_id，不是成功任务后续状态。

`draft/queued.json`、`draft/running.json` 展示同一个 DRAFT 任务的中间状态。

`invalid/` 中两份请求分别演示非法 job_type 和缺少 baseline，必须被 Schema 拒绝。对应 `http-errors/` 文件是 HTTP 400 响应提案，不创建 Job、不返回 job_id。

## 演示流程中的版本与产物

- C0：`0123456789abcdef0123456789abcdef01234567`
- C1：`89abcdef0123456789abcdef0123456789abcdef`
- 成功流程 trace_id：`trace-pair11-demo-001`
- 配置：`cfg-ubuntu22-gcc12-release-v1`

FULL_CHECK 使用 DRAFT 返回的 image URI；INCREMENTAL_CHECK 使用 FULL_CHECK 的 actual graph URI，baseline.commit 等于 C0；REPAIR 使用增量任务返回的 MD report URI，目标源码为 C1。C1 复用 C0 的工具链镜像；提案约定镜像负责环境，执行器另行检出请求指定的源码版本，不将镜像内旧源码作为 C1。

修复产物的 commit 表示补丁应用前的 C1。验证在“C1 + Patch”的工作区进行，样例不虚构一个新的修复提交。后续需由双方确认该语义。

产物 URI 是交接引用，除下述报告内容示例外，本目录没有创建镜像、图、日志或 Patch 文件，不声称 URI 已可读取。

## 待 A11 确认的具体提案

1. HTTP 202 回执包含 schema_version、trace_id、job_id、status=QUEUED；HTTP 400 包含 schema_version、trace_id、error。查询响应仍使用现有完整 Job 结构。
2. DRAFT 输出新增 build_result、verification_result（command 和 exit_code），iterations 记录实际迭代次数；逐轮修改、理由和步骤结果已定义于 [逐轮记录格式](../docs/draft_iterations.md)，人工样例为 `artifacts/draft-iterations.json`，通过 iteration_record_uri 关联成功响应。样例引用的日志未实际生成。
3. REPAIR 输出新增 patch_accepted、declaration_style、validation；验证失败时 output=null，拒绝原因放入 error.details。
4. `artifacts/md-report.json` 对应增量响应中的 `artifact://job-INCREMENTAL_CHECK-demo001/report-001/md-report.json`。这是报告内容提案，未放入仓库根目录 artifacts/，若演示本地解析需将它复制到 `artifacts/job-INCREMENTAL_CHECK-demo001/report-001/md-report.json`。
5. 报告的 findings 表示当前发现，delta.added/resolved 使用 finding_id；人工来源为 MANUAL_EXAMPLE。纯 MD 样例只含 MISSING；另有 `artifacts/mixed-report.json` 演示混合报告。B11 初稿规定校验完整报告后只修复 MISSING，RD 保留不修改；见 [报告契约](../docs/md_report.md)。
6. 两组独立部署，image.tar 经 HTTP 下载后使用 docker image load 加载；DRAFT 镜像产物中的 image_ref 指明镜像标签。URI 映射、文件读取和加载流程见 [产物交接约定](../docs/artifact_handoff.md)。真实地址与部署配置待确定。

检测发现 MD 时，增量分析任务仍为 SUCCEEDED、error=null。MD 属于报告内容，不能放进系统执行 error。

## 校验范围与命令

安装 `jsonschema[format]` 后，在仓库根目录执行：

```bash
python -m unittest discover -s tests -v
```

测试使用现有 task.schema.json 校验四类请求、完整查询响应和非法请求，同时检查演示中的跨任务 URI、基线、版本和报告引用衔接。MD/RD 报告内容另由 `md-report.schema.json` 校验。accepted、HTTP 错误封装和新增输出字段尚无正式 Schema；相关测试只检查提案的基本一致性，不表示双方已经确认。正式 validate.py 属于后续校验工具任务。
