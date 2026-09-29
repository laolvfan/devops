# DRAFT 逐轮记录格式

状态：B11 接口设计，待 A11 确认。本文只规定将来运行时如何记录，不提供真实构建日志。

Schema 见 [draft-iterations.schema.json](../schemas/draft-iterations.schema.json)，人工样例见 [draft-iterations.json](../examples/artifacts/draft-iterations.json)。样例中的命令、结果和 URI 均为演示数据；没有执行命令，也没有生成所引用的日志文件。

## 一轮是什么

一轮是生成或修改 Dockerfile 后，依次尝试构建镜像、构建项目、运行验证。前一步没有通过，后续步骤标为 NOT_RUN。只有全部通过，该轮才可被选为成功结果；失败后可以在迭代次数和任务超时预算内继续下一轮。

iteration 从 1 开始连续编号，表示同一个 Job 内的生成尝试。它不同于 execution.attempt（任务执行尝试次数）；失败重试产生的新 Job 使用自己的逐轮记录。

## 顶层字段

| 字段 | 含义 |
|---|---|
| schema_version | 当前逐轮记录版本 1.0.0 |
| source | MANUAL_EXAMPLE 表示人工演示，DRAFT_EXECUTION 才表示真实运行采集 |
| producer_job_id | 所属 DRAFT Job |
| repository | 构建目标仓库及完整 commit，与 Job 输入一致 |
| rounds | 已结束或被中断的轮次记录，按 iteration 升序排列 |

若在第一轮开始前失败，rounds 可为空。运行中的步骤不写成 PASSED；记录在每轮结束或任务中断时保存。最终记录只描述实际发生的尝试，不为未发生的轮次补造结果。

## 每轮字段

| 字段 | 含义 |
|---|---|
| iteration | 第几轮，正整数，不超过本次 max_iterations |
| changes | 非空修改列表，每项有 path、summary，说明修改文件及内容；首次生成也算一次修改 |
| reason | 为什么进行本轮修改，应引用构建说明或上一轮失败原因 |
| image_build | 构建 Docker 镜像的步骤结果 |
| build | 在该镜像环境中执行项目 build_command 的结果 |
| verification | 执行 verify_command 的结果 |

summary 和 reason 记录可供复核的修改依据，例如上一轮缺少工具、此次补装该工具，不要求记录模型内部推理。当前 DRAFT 只修改环境构建文件，不在此阶段修改项目依赖声明。

## 步骤结果

每个步骤都有 command、status、exit_code、log_uri：

| status | exit_code | 含义 |
|---|---|---|
| PASSED | 0 | 该步骤正常成功 |
| FAILED | 非零整数或 null | 执行失败；进程未成功启动或未取得退出码时用 null |
| NOT_RUN | null | 前一步未通过或任务已停止，本步骤没有执行；log_uri 也为 null |
| INTERRUPTED | 实际退出码或 null | 执行中因超时、取消等中断，不等于成功 |

已有日志时填写 artifact URI，无日志时填写 null，不能编造路径。command 是所执行或原计划执行的命令文本，不表示接收方应自动执行它。NOT_RUN 的 command 仍可以记录原计划。

## 与 Job 输出的关系

成功的 DRAFT 响应新增 `output.iteration_record_uri`，指向本记录 JSON；同时在 output.artifacts 登记为 BUILD_LOG、media_type=application/json，复用现有产物类型。原有文本 BUILD_LOG 可继续保存整体日志。

- output.iterations 等于 rounds 条数。
- 成功任务至少有一轮，最后一轮三个步骤均为 PASSED。
- 最后一轮 build/verification 的命令及退出码与最终 build_result/verification_result 对应。
- 所属 job_id、repository 与 Job 输入一致。
- 每个非空 log_uri 在真实运行时都必须可通过产物下载接口读取；生产方需要登记相应日志，人工样例不声称它们存在。

失败、超时或取消的 Job 继续保持 output=null。若已保存逐轮记录，可在 error.details.iteration_record_uri 中提供诊断引用；error.log_uri 可以指向实际错误日志。诊断记录不能作为成功环境交给下游。

该记录跨越多轮环境变化，不为每轮声称已有最终 configuration_id；成功记录的产物元数据关联最终选定的配置，失败候选不作为正式环境发布。

## 文件校验与实际验证

Schema 检查字段、步骤状态、退出码，以及前一步未通过时后续不得执行。轮次连续性、预算限制、跨文件一致性及来源真实性需由后续程序保证；当前样例校验覆盖与成功 Job 的基本对应关系。

现有样例仅演示一轮成功；校验用例另外构造失败后跳过验证的对象，检查格式能表达该情况。两者都没有调用 Docker 或运行 make。
