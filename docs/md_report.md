# MD/RD 报告契约

- 版本：1.0.0 初稿。
- 状态：B11 当前设计，待 A11 确认；后续按反馈同步修改文档、Schema 和样例。
- 用途：定义 ERROR_REPORT 产物的文件内容，供 BuildChecker/EChecker 输出、MDFixer 读取。
- Schema：[`md-report.schema.json`](../schemas/md-report.schema.json)。
- 样例：[`md-report.json`](../examples/artifacts/md-report.json)、[`mixed-report.json`](../examples/artifacts/mixed-report.json)。

## 报告表示什么

MISSING（MD）表示实际需要但未声明的构建依赖；REDUNDANT（RD）表示当前构建配置下声明了但未使用的依赖。报告发现属于正常分析结果，不是系统执行错误。即使发现 MD，检测 Job 仍可为 SUCCEEDED、error=null。

样例中的仓库、SHA、源码行号和证据均为人工设定，detector 为 MANUAL_EXAMPLE，不代表工具已经运行。mixed-report.json 是与纯 MD 样例二选一的独立场景，不是同一任务的第二份真实产物。

## 顶层字段

| 字段 | 必填 | 含义 |
|---|---|---|
| schema_version | 是 | 本报告格式版本，当前为 1.0.0 |
| repository.url | 是 | 被检测仓库的地址 |
| repository.commit | 是 | 被检测源码完整 SHA，不能使用分支名或缩写 |
| configuration_id | 是 | 本次构建配置，与报告元数据、修复环境一致 |
| producer_job_id | 是 | 生成本报告的任务，与产物元数据一致 |
| detector | 是 | BUILDCHECKER、ECHECKER、INSTRUCTOR_ORACLE 或 MANUAL_EXAMPLE |
| findings | 是 | 当前源码版本的全部发现；无发现时为 [] |
| delta | 否 | 增量报告必须提供；全量报告和修复后重检可省略 |

producer_job_id 表示负责产出报告的 Job，detector 表示实际检测来源。修复后重检可由 REPAIR Job 产出报告，但 detector 应填实际使用的检测器，不能将 MDFixer 冒充为检测器。

## 每条 finding

| 字段 | 规则 |
|---|---|
| finding_id | 非空字符串，报告内唯一；同一问题跨提交保持稳定 |
| type | MISSING 或 REDUNDANT |
| target | 构建目标，例如 main.o |
| dependency | 对应依赖，例如 config.h |
| commit | 与 repository.commit 一致 |
| location.path | 声明文件相对仓库根目录的路径，例如 Makefile；使用 /，不包含 .. 路径段 |
| location.line | 目标规则所在行，从 1 开始；MD 指向待补依赖的规则位置 |
| evidence | 非空证据数组，解释为什么认定此依赖缺失或冗余 |

文件型 target/dependency 优先使用仓库根目录相对路径；非文件构建目标保留原始名称。系统文件可使用绝对路径，但修复器不能直接将未经分析的系统路径写入 Makefile。

finding_id 由生产方维护。同一配置下 type、target、dependency、声明文件和规则标识相同的问题应沿用 ID；行号移动或 commit 改变本身不应改变 ID。类型或配置改变则重新识别。具体 ID 生成算法由 A11 实现，接收方将 ID 当作不透明字符串。

## 证据格式

每条证据必填 kind 和 description，其他字段按证据内容提供：

| kind | 含义 | 常用字段 |
|---|---|---|
| FILE_READ | 构建过程中读取依赖的依据 | path、command |
| DECLARATION | 当前目标实际声明的依赖 | path、declared_dependencies |
| ANALYSIS | 图比较、跟踪结果或其他分析依据 | description |

MD 应解释“实际使用了什么”与“声明中缺少什么”，可使用 FILE_READ + DECLARATION，也可提供能说明二者的 ANALYSIS。RD 应解释当前配置下的声明与使用差异，不意味着其他配置也不需要此依赖。

description 必须说明依据；人工样例应明确写“人工设定”，不能写成真实抓取的构建日志。Schema 只能检查结构，证据是否充分、真实仍需要业务验证。command 是证据文本，不是要求接收方执行的指令。

## 增量 delta

- base_commit：比较基线的完整 SHA，应等于 INCREMENTAL_CHECK 输入的 base_commit。
- added：本次新增的 finding_id，必须存在于当前 findings。
- resolved：基线中存在、本次已消除的 finding_id，不得存在于当前 findings。
- added/resolved 内各自不可重复，两者不能重叠。
- 当前仍存在但没有变化的发现留在 findings 中，不进入 added/resolved。

resolved 中的 ID 需要结合基线报告解释。本字段只描述分析发现变化，不是 MDFixer 的待修列表；MDFixer 从当前 findings 中选择全部 MISSING，包括以前已存在的 MD。

## MDFixer 读取与处理规则

1. 读取报告并校验整体结构。未知 type、缺少证据等属于报告格式错误，不能当成 RD 静默忽略。
2. 检查报告与请求的 repository.url、commit、configuration_id 一致；每条 finding.commit 与报告 commit 一致；报告元数据与文件内容一致。URL 在本版按精确字符串比较，由双方统一地址写法。
3. 校验 finding_id 唯一、delta 引用关系等跨字段约束。
4. 从 findings 中选择 type=MISSING 的条目；REDUNDANT 保留在原报告中，不生成删除依赖的补丁。
5. 若选不到 MD，调用方应跳过 REPAIR。若仍提交此类请求，创建接口在报告预检后返回 HTTP 400 / REQUEST_1001，details.reason 为 NO_MISSING_FINDINGS，不创建 Job。
6. MD 位置超出本次请求的 makefile_path 时，本版不静默漏修：预检返回 HTTP 400 / REQUEST_1001，details.reason 为 UNSUPPORTED_DECLARATION_FILE。多 Makefile 修复另行扩展。
7. 修复完成后重新构建、测试和检测。仍有 MD 或验证失败则拒绝候选，使用 REPAIR_6001；RD 存在本身不判定修复失败。

版本或配置不匹配沿用 REQUEST_1002。报告不可读取、格式错误或产物元数据错误沿用 ARTIFACT_2001（已创建任务后为 FAILED）。已接受的 Job 不能追溯地变成 HTTP 400；执行时才发现无 MD、位置不支持或前置条件失效的，返回 Job FAILED / REPAIR_6001，并在 details.reason 记录原因。

这些是后续服务实现要求，本次只交付文档、Schema、样例和文件校验。

## 校验边界

JSON Schema 检查字段、类型、完整 SHA、行号、证据非空和 delta 的基本结构；跨字段相等、ID 唯一性与引用关系、增量报告必须包含 delta、报告是否真的对应源码、MD 筛选及无 MD 时的 HTTP 行为由后续程序实现。

空 findings 是合法检测结果，但不是有效修复输入。MD 和 RD 混合报告也是合法检测结果。

从仓库根目录运行全部文件校验：

```bash
python -m unittest discover -s tests -v
```

需先在 Python 环境安装 `jsonschema[format]`。校验通过不代表检测、构建或修复已经实现。
