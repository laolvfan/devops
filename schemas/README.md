# E2 JSON Schema

`task.schema.json` 将 `docs/interface_contract.md` 已明确的结构约定转换为 JSON Schema Draft 2020-12，供 A11/B11 共用。当前为待双方确认的首版。

## 入口

- 根入口：创建请求或完整任务查询响应。
- `$defs/createRequest`：创建请求，禁止携带服务端生成的 job_id、status、execution、output、error。
- `$defs/jobResponse`：完整任务查询响应。
- `$defs/artifact`、`$defs/error`：可复用的产物元数据、系统错误结构。

四类任务根据 job_type 选择对应 input。成功响应要求相应服务的最低产物集合；失败、超时和取消响应要求 error，output 必须为 null。QUEUED/RUNNING 的 output/error 均为 null。

对象允许新增可选字段，以遵循现有兼容规则；已声明字段仍必须满足类型约束。拼错必填字段会因缺少正确字段而失败，但拼错可选字段不会被自动识别。

## 本版解释与边界

- schema_version 接受 1.x；结构采用当前 1.0.0 规则，不代表未来每个版本均已验证。
- 完整 commit 接受 40 位 SHA-1 或 64 位 SHA-256 十六进制值；不接受示例文档中的占位文字。
- configuration_id 按文档的 cfg-系统-工具链-模式-版本五段格式校验。
- DRAFT 请求可省略 max_iterations；服务端应补成 20 并在响应中返回。Schema 的 default 只提供说明，不修改数据。
- 日期与 URI 校验需显式启用格式检查器。
- `task.schema.json` 只检查产物元数据；MD/RD 文件内容由新增的 `md-report.schema.json` 单独校验，详见 [报告契约](../docs/md_report.md)。图、构建验证结果、修复声明风格等内部结构仍待补充。
- 简短 HTTP 202 回执的字段尚未完全约定，不属于根入口；不能用完整查询响应的规则校验它。

以下仍需业务程序检查：baseline.commit 等于 base_commit、基线配置匹配环境、报告版本匹配源码、execution/input 超时一致、时间先后及实际时长、任务编号唯一、幂等行为、状态转换、URI 可读取、修复只消费 MD，以及构建/测试/重检真正通过。结构校验通过不等于业务验收通过。

## 验证

在仓库根目录执行（建议使用独立虚拟环境）：

```bash
python -m pip install 'jsonschema[format]>=4,<5'
python -m unittest discover -s tests -v
```

校验一份完整请求或查询响应：

```python
import json
from jsonschema import Draft202012Validator, FormatChecker

with open('schemas/task.schema.json') as f:
    schema = json.load(f)
with open('request.json') as f:
    data = json.load(f)

Draft202012Validator.check_schema(schema)
Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
```

`tests/test_task_schema.py` 中的数据仅供 Schema 回归测试，不是实际构建、检测或配对验收证据。完整演示样例见 `examples/README.md`，其中未定稿字段明确标为提案；validate.py 留待后续校验工具任务完成。

参考：[条件校验](https://json-schema.org/understanding-json-schema/reference/conditionals)、[default 等注解](https://json-schema.org/understanding-json-schema/reference/annotations)。
