# B11 响应格式

本页补齐现有 E2 提案中的 HTTP 回执、请求错误和 B11 成功结果。当前仍为未发布的 1.0.0 初稿，不表示 A11 已确认；若之后对已发布契约增加必填字段，按主版本变更处理。

## 按场景选择校验入口

所有入口位于 `schemas/task.schema.json` 的 `$defs`。根入口仍只校验创建请求或完整查询响应，避免将一个简短回执误当成完整 Job。

| HTTP 场景 | Schema 入口 | 必填字段 |
|---|---|---|
| 首次创建任务被接受，202 | acceptedResponse | schema_version、trace_id、job_id、status |
| 请求无效，400 | badRequestResponse | schema_version、trace_id、error |
| 查询成功，200 | jobResponse | 原有完整 Job 字段 |

HTTP 状态属于响应头，不在 JSON 中重复保存。查询返回 HTTP 200，只表示查询成功，后台任务可能为 FAILED 等状态。

## 202 创建回执

status 固定为 QUEUED。job_id 由服务端生成，trace_id 与创建请求一致。回执不携带 input、execution、output 或 error；详情通过查询接口获取。

这是首次受理响应；同一幂等键再次请求的返回策略仍需后续明确，不能将本节视为已经实现了幂等存储或重放。

## 400 请求错误

error 使用公共错误结构；code 为 REQUEST_1001（字段或前置条件无效）或 REQUEST_1002（版本/配置不匹配），retryable=false。details 说明具体字段或拒绝原因。

无有效 trace_id 可返回时，trace_id 为 null，例如请求缺少该字段或 JSON 无法解析。schema_version 填服务端用于生成错误响应的版本。不得原样回显任意无效值以制造一个也不合法的错误响应。

400 不创建 Job，不包含 job_id、status、execution 或 output。任务已接受后发生的执行错误属于完整查询响应中的 error，不能改成创建请求的 400 回执。

## DRAFT 成功 output

| 字段 | 规则 |
|---|---|
| artifacts | 至少包含 DOCKERFILE、DOCKER_IMAGE、BUILD_LOG |
| build_result | command 为非空命令文本，exit_code 必须为 0 |
| verification_result | command 为非空命令文本，exit_code 必须为 0 |
| iterations | 实际轮数，1～50；业务程序还需确认不超过输入 max_iterations |
| iteration_record_uri | 合法 artifact URI，指向已登记的逐轮 JSON 记录 |

DOCKER_IMAGE 元数据中的 image_ref 仍为可选字段，但提供时必须是非空字符串；本组当前 image.tar 交接方案要求生产者实际提供它，供消费者识别加载后的镜像。镜像标签是否可用由运行时验证。

逐轮记录 JSON 使用独立 Schema，详见 [逐轮格式](draft_iterations.md)。URI 与产物列表对应、轮数与记录条数一致、结果命令与输入一致仍需跨字段/文件校验，不由单个 Schema 证明。

## MDFixer 成功 output

| 字段 | 规则 |
|---|---|
| artifacts | 至少包含 PATCH、BUILD_LOG、TEST_RESULT、ERROR_REPORT |
| patch_accepted | 必须为 true |
| declaration_style | 非空文本，说明补丁沿用或采用的声明方式 |
| validation.build_exit_code | 必须为 0 |
| validation.test_exit_code | 必须为 0 |
| validation.remaining_missing | 必须为 0 |
| validation.workspace | 非空文本，说明验证对象为哪个源码版本加哪个补丁 |

没有要求剩余 RD 数量为零，因为 MDFixer 只修 MD。补丁未接受、构建/测试失败或仍有 MD 时，不能生成 SUCCEEDED 响应，应使用 FAILED / REPAIR_6001，output=null。Schema 只核对报告的数据，不能证明真实执行成功。

## 直接校验回执

```python
import json
from jsonschema import Draft202012Validator, FormatChecker

with open('schemas/task.schema.json') as f:
    schema = json.load(f)
with open('examples/draft/accepted.json') as f:
    data = json.load(f)

entry = {
    '$ref': '#/$defs/acceptedResponse',
    '$defs': schema['$defs'],
}
Draft202012Validator(entry, format_checker=FormatChecker()).validate(data)
```

400 使用 badRequestResponse，完整查询结果使用 jobResponse。所有人工响应样例的文件校验通过 `python -m unittest discover -s tests -v` 执行，不调用服务。
