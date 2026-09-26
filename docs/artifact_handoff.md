# B11 产物交接约定

状态：B11 方案，待 A11 确认。本文定义后续部署的读取方式，不表示下载服务已经实现。

## 部署与共享范围

两组分别部署服务器、维护自己的实现仓库，不要求共用代码仓库或挂载同一目录。双方共享接口契约、Schema 和样例；运行时通过 HTTP 文件下载交接报告、日志、Patch、Dockerfile 和镜像归档。

B11 提供 DRAFT/MDFixer 的任务查询和产物下载入口。A11 的报告下载入口是 B11 的外部依赖，需双方确认，本文件不替 A11 安排实现工作。

## 逻辑 URI 如何变成下载地址

Job 中继续使用已有格式，不改变现有 JSON 字段：

```text
artifact://<job_id>/<artifact_id>/<filename>
```

部署时配置双方对外入口 `B11_BASE_URL` 和 `A11_BASE_URL`，例如 `https://b11.example.com` 和 `https://a11.example.com`。示例域名不是已部署地址。

按生产 Job 的服务类型确定入口：

| 生产任务类型 | 读取入口 |
|---|---|
| DRAFT、REPAIR | B11_BASE_URL |
| FULL_CHECK、INCREMENTAL_CHECK | A11_BASE_URL（对接提案） |

job_id 按现有 `job-<job_type>-<唯一标识>` 解析。下载端点约定为：

```text
GET {BASE_URL}/v1/artifacts/{job_id}/{artifact_id}/{filename}
```

例如：

```text
artifact://job-DRAFT-demo001/image-001/image.tar
→ https://b11.example.com/v1/artifacts/job-DRAFT-demo001/image-001/image.tar

artifact://job-INCREMENTAL_CHECK-demo001/report-001/md-report.json
→ https://a11.example.com/v1/artifacts/job-INCREMENTAL_CHECK-demo001/report-001/md-report.json
```

逻辑 URI 中的 job_id 是大小写敏感标识，不是 DNS 主机名；解析器不得将其中的 DRAFT 等转换成小写。构造 HTTP 地址时逐段编码并保持标识原值，拒绝路径穿越和无效标识。不得根据报告提供的任意服务器地址发起下载，只使用已配置的配对入口。

每组可在入口后转发到自己的多个服务。若后续各服务使用不同地址，可将入口配置细分到服务类型，逻辑 URI 保持不变。

## 文件存储与响应

B11 可以将逻辑 URI 对应文件存放到自己服务器的：

```text
artifacts/<job_id>/<artifact_id>/<filename>
```

该目录是 B11 的内部存储位置，另一组通过 HTTP 获取字节内容，不直接读取 B11 文件系统。下载接口按已登记产物查找文件，不开放整个仓库或任意目录。

| 下载结果 | HTTP 状态 | 内容 |
|---|---|---|
| 成功 | 200 | 原始文件字节，Content-Type 与产物 media_type 一致 |
| 产物不存在 | 404 | 错误信息，不返回伪装成文件的成功响应 |
| 暂时无法读取 | 503 | 错误信息，调用方记录原因后按重试策略处理 |

若部署启用身份认证，401/403 表示凭据或访问权限问题，不能当作有效产物。实际认证方式、地址、端口及网络可达性在部署前确认；凭据放在部署配置中，不写入 URI 或提交到仓库。

同一个 URI 发布后内容不覆盖；新的产物使用新标识。生产方在文件完整写入、该任务所需验证通过后发布正式 output；失败任务的诊断日志可由 error.log_uri 引用，但不能当作正式成功产物。联调期间保留交接文件，清理前通知消费者。

接收方先读取生产任务的完整查询响应及产物元数据，核对 job_id、artifact_id、类型、源码版本和配置，再下载文件。URI 已知但元数据未随请求提供时，按生产入口查询 `GET /v1/jobs/{job_id}` 获取对应记录。报告内容还需通过报告 Schema 和版本一致性检查。文件下载成功不等于内容有效。

下载失败时，已创建的消费任务按契约返回 FAILED / ARTIFACT_2001，并在 error.details 中记录下载状态与原因；明确为暂时性基础设施问题时才允许 retryable=true。

## Docker 镜像交接

当前选择 HTTP 传输 `image.tar`，不要求额外部署镜像仓库。每份归档只包含本次成功环境的一个明确镜像标签，生产方在 DRAFT 的 DOCKER_IMAGE 产物记录中附加可选 `image_ref`，标明加载后使用的标签。标签在联调期间不得重用为不同镜像；接收方同时核对 configuration_id。

`image_ref` 是本次新增的 B11 交接字段，属于 DOCKER_IMAGE 元数据，不是 artifact URI，也不是要求联网拉取的地址。当前允许扩展字段的任务 Schema 可接受它；字段专用约束在后续完善结果结构时补齐。

以下仅为操作说明，没有在本项目执行。假设成功镜像已有标签 `b11/draft:demo001`，B11 导出：

```bash
docker image save --output image.tar b11/draft:demo001
```

B11 将完整归档登记为产物并通过下载端点提供。接收方下载成功后加载：

```bash
curl --fail --show-error --output image.tar https://b11.example.com/v1/artifacts/job-DRAFT-demo001/image-001/image.tar
```

上一步成功后再执行：

```bash
docker image load --input image.tar
docker image inspect b11/draft:demo001
```

接收方确认镜像平台与运行服务器相容；加载失败不能继续构建。镜像用于提供工具链环境，执行器必须准备请求 repository.url 和完整 commit 指定的源码，并在约定项目目录执行构建命令。复用 C0 的镜像分析 C1 时，不能继续使用镜像内的 C0 源码。

Docker 镜像归档与加载命令依据官方文档：[image save](https://docs.docker.com/reference/cli/docker/image/save/)、[image load](https://docs.docker.com/reference/cli/docker/image/load/)。

## E2 与后续验收

E2 提供 URI 到 HTTP 的映射、下载约定、镜像加载步骤和样例即可。本次没有共享代码仓库、部署服务器或上传镜像。

后续联调需用真实入口证明：另一台服务器能查询生产任务、下载文件、读取报告、加载镜像并使用指定源码；失败下载会被识别。实际域名、认证及服务器架构尚未确认，不以文档示例冒充运行证据。
