# E2 文件校验记录

## 检查对象与结论

基线提交：[`a434baa`](https://github.com/laolvfan/devops/commit/a434baae185e4794fa9c4df0e8d45dd05003510e)。

在该版本执行 18 项自动化文件校验，全部通过；Markdown 本地文件链接检查未发现失效链接。检查覆盖 Schema、JSON 样例和引用一致性，没有启动 API，也没有执行真实 Docker 构建、依赖检测或修复。

## 复现方式

在仓库根目录使用独立 Python 环境：

```bash
python -m venv /tmp/devops-e2-check
/tmp/devops-e2-check/bin/pip install 'jsonschema[format]>=4,<5'
PYTHONDONTWRITEBYTECODE=1 /tmp/devops-e2-check/bin/python -m unittest discover -s tests -v
```

通过摘要：

```text
Ran 18 tests
OK
```

## 已检查内容

| 文件 | 项数 | 范围 |
|---|---:|---|
| tests/test_task_schema.py | 6 | 四类任务输入和状态、缺 baseline、非法类型、成功/失败产物规则、默认值不自动填充 |
| tests/test_examples.py | 5 | 磁盘样例、HTTP 提案的基本一致性、跨任务 URI/版本衔接、报告与 REPAIR 输入匹配 |
| tests/test_md_report_schema.py | 7 | MD 与混合报告结构、必填位置/证据、非法字段、空报告、增量基线、人工来源标记 |

这些校验中的 FULL_CHECK、INCREMENTAL_CHECK 仅用于验证共享交接格式，不代表 B11 实现或验证了 A11 的服务。

## 未验证与后续工作

- Schema 不能证明证据真实、产物可读取或补丁有效。
- 202 回执、HTTP 错误封装和新增结果字段尚未完整纳入独立 Schema。
- 混合报告筛选、版本比较、幂等请求、跨字段约束仍需后续服务实现与验证。
- 没有真实 DRAFT/MDFixer 运行结果、跨组读取或联调证据。
- 后续修改 Schema 或 JSON 样例时重新执行上述命令；更新本记录时关联实际受检版本。

## 工作区补充校验

在 a434baa 基础上的未提交工作区补充产物 HTTP 交接说明、DRAFT 人工样例和逐轮记录 Schema 后，执行同一 unittest 命令，共 23 项通过。新增 `tests/test_draft_iterations.py` 的 5 项检查覆盖逐轮结构、缺少修改理由、成功退出码、失败后跳过验证及样例与 Job 的对应关系。

此结果关联当前工作区变更，不归属于尚未包含这些文件的 a434baa；提交后再补充真实 SHA。检查仍只针对文件，不生成运行日志。
