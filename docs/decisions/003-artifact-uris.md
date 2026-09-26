# ADR-003：通过逻辑 URI 传递产物

- 状态：B11 决策草案，待 A11 确认
- 来源：E2 需求与接口契约；A11/B11 配对组约定

## 背景

Dockerfile、镜像、依赖图、检测报告和 Patch 等产物可能较大。直接把文件内容放进任务响应不利于跨服务读取，也会绑定具体机器路径。下游还需要知道产物的来源及其对应源码和环境。

## 决策

- 使用与项目名和阶段名无关的逻辑 URI：
  ```text
  artifact://<job_id>/<artifact_id>/<filename>
  ```
- 当前实验将 URI 映射到项目根目录下的 `artifacts/`：
  ```text
  artifact://job-FULL_CHECK-001/graph-001/actual.json
  → artifacts/job-FULL_CHECK-001/graph-001/actual.json
  ```
- 产物记录 `artifact_id`、类型、URI、媒体类型、生产 Job、源码 commit 和 `configuration_id`。
- 接收方根据 URI 读取产物，不依赖绝对本地路径。
- 后续可将同一逻辑 URI 映射到产物服务或对象存储。

## 备选方案分析

- **在 Job 响应内嵌文件内容**：小文件调用方便，但响应体随产物变大，难以处理镜像、日志和图等文件。
- **使用绝对本地路径**：本机调试方便，但另一组或另一台机器不能依赖相同路径。
- **让消费者直接依赖某种对象存储 URL**：可复用现成存储，但把存储供应方和接口地址暴露给各服务。

## 后果

- Job 响应只需携带产物引用。
- A/B 组必须能通过约定 URI 访问共享文件，并核对产物元数据。
- 后续更换存储实现时，调用方接口可以保持不变。
- 当前 `artifact://` 映射是实验约定；仓库中的 URI 样例不表示文件已实际上传或可读取。

## 关联规约

- [接口契约](../interface_contract.md)
- [样例说明](../../examples/README.md)
