# E13–E14 成员三运行记录

学号：241880100；小组：B11；本轮职责：四服务导入、固定样例与 CI 准备。
仓库：https://github.com/laolvfan/devops.git
个人分支：`student/241880100/e13-e14`；[PR #14](https://github.com/laolvfan/devops/pull/14)。

## 工作范围与版本

复用已合入 main 的 E11–E12 实现，增量导入教师发放包中的四角色 HTTP 服务、编排入口、报告交接工具、运行日志扫描器、交接测试和 CI。四服务配置及编排来自课程材料；本轮补充报告传输哈希校验测试，并修复 CI 用户映射及产物归档问题。

|提交|内容|
|---|---|
|`7734241b4df0a8ba2d6b16aa7622466a91b639d9`|导入四服务/CI；补齐可选 fixed_report_sha256 校验及回归测试|
|`39ac3934b7bd18f9ce9c9f239191b88b820c9b5b`|CI 仓库处理服务按宿主 UID/GID 运行|
|`f177a5f0ed96d5beb9a93ffb5a26ea9cc8bfdd41`|产物上传包含隐藏文件，并排除 Git 内部数据|

服务器固定样例在 7734241 上运行；最终 CI 在 f177a5f 上运行。后续配置修复不改写此前实验的提交和原始证据。

## 四服务配置与职责

配置位于 `labs/e13e14/compose.yaml`，编排入口为 `labs/e13e14/orchestrate.py`。

|角色|作用|服务器监听端口|
|---|---|---|
|DRAFT|构建候选镜像并运行程序验证|127.0.0.1:18083|
|BuildChecker|检查基线、目标及修复后的全量依赖|127.0.0.1:18081|
|EChecker|使用基线图检查目标提交，并对照目标全量结果|127.0.0.1:18082|
|MDFixer|校验本轮报告身份及哈希，生成补丁并验证|127.0.0.1:18084|

Compose 项目为 `e14-241880100`，四容器共用 `course-e11e12:241880100` 镜像，镜像 ID 为 `sha256:3192a6ae9ee0e3006e6ba33bf8029fa5c9504d1be8e8badb8dc96cdf933bb65b`。仅 DRAFT 挂载 Docker socket。端口绑定服务器本机地址。

## 服务器固定样例

在 `/root/241880100/devops` 使用以下入口运行，输出目录为首次创建：

```bash
export E14_ROOT="$PWD"
export E14_IMAGE=course-e11e12:241880100
docker compose -f labs/e13e14/compose.yaml -p e14-241880100 up -d --wait
python3 labs/e13e14/orchestrate.py \
  --request data/integration-sample/e12.json \
  --out work/e14-compose-241880100-sample-01
```

当前未找到该轮单独保存的控制台日志；结果以 result.json、各阶段原始日志和四服务日志核验。四容器均 healthy，四个 /health 接口均返回 HTTP 200。完整执行结果为 SUCCEEDED。

- base：`ee881a6f52311250ef9694df6058064f40466a24`。
- target：`655b87109388e30d71772ed06839df7472112101`。
- job_id：`job-46a812f717504e7c995da990643ab651`。
- trace_id：`trace-ff222a34b37248d5a4eb9b22fe183323`。

draft → full-check → incremental-check → repair → recheck 五阶段成功。五阶段的 job_id/trace_id 一致；full-check 对应 base，其余阶段对应 target。四角色处理日志包含同轮任务编号，证明实际经服务接口执行。

MDFixer 将 `main.o: main.c unused.h` 修复为 `main.o: main.c unused.h config.h extra.h`。补丁应用、构建、功能测试、头文件变化重编译及无 MISSING 五项验证均通过。最终只保留 unused.h 的 REDUNDANT，符合只修复 MD 的范围。

独立核验了 162 个清单产物的大小和 SHA256，并核验增量报告哈希。运行证据及四服务日志扫描退出码为 0，扫描输出为 text_files=152、hits=0、errors=0；该结论仅覆盖所扫描目录和日志。

## 故障与修复

### CI 用户所有权不一致

首次 [CI 运行 44004702497](https://github.com/laolvfan/devops/actions/runs/44004702497) 在 7734241 上失败，已记录 [Issue #13](https://github.com/laolvfan/devops/issues/13)。

四容器健康，draft/full-check 完成，但 EChecker 执行 git rev-parse 时出现 dubious ownership，端到端退出码为 1。原因是 GitHub runner 创建的仓库属于普通用户，原 Compose 使用 root 访问；服务器目录与容器均由 root 使用，因此服务器运行未暴露该问题。

修复为：Compose 支持 E14_UID/E14_GID，CI 传入 runner 的 UID/GID；BuildChecker、EChecker、MDFixer 与宿主身份一致，DRAFT 独立保留 root 以访问 Docker socket，各角色 HOME 设置为 /tmp。保留 Git 所有权检查，没有设置全局 safe.directory 通配例外。

修复后的 39ac393 CI 四服务检查通过：[运行 44005159619](https://github.com/laolvfan/devops/actions/runs/44005159619)。

### 下载包遗漏隐藏文件

39ac393 的四服务任务通过，但下载产物中，162 个清单文件缺少 7 个 .gitignore；已有文件哈希匹配。原因是 upload-artifact 默认忽略隐藏文件。

在 f177a5f 中增加 include-hidden-files=true，并通过路径规则排除 work/**/.git/**。新一轮 CI 通过；下载包包含全部 162 个文件，7 个 .gitignore 均存在，没有 Git 内部文件，逐文件大小及哈希全部匹配。

## 最终 CI 与完整产物核验

最终四服务工作流：[运行 44009099347](https://github.com/laolvfan/devops/actions/runs/44009099347)；源码提交为 f177a5f。contracts、four-services 及原有 E7、E8–E10、E11–E12 相关检查均成功。

CI 从 prepare 重新生成课程样例，因此其样例提交与服务器轮次不同：

- base：`cc0c45155635615f3a26b81828c77aa60311e8ad`。
- target：`82ed10eeb59665da8b02c8ad12546fd620244a74`。
- job_id：`job-703419f4c4e945108711d286fffd8343`。
- trace_id：`trace-e7f3f482c9274892988dcbc18a9ecfda`。

五阶段成功、补丁 accepted，验证五项全部通过，最终 remaining_missing=0。四服务日志与同轮身份一致，阶段描述符哈希、增量报告哈希及全部 162 个产物均核验通过。CI 同时执行证据目录和服务日志扫描。

本机原始包：`~/devops_resources/e13e14-evidence-44009099347-1.zip`。
整包 SHA256：`8847ed6e18d031f0cb3ec1e4820f1cdee963664bc2335f8111ceae406648e313`。

## 证据索引

|内容|位置|
|---|---|
|服务器原始结果、阶段报告、补丁、请求和日志|`work/e14-compose-241880100-sample-01/`|
|服务器控制台输出|当前未找到独立文件；已保留各阶段和服务日志|
|服务器独立核验、Compose 状态、服务日志及扫描|`work/e14-compose-241880100-sample-01-checks/`|
|哈希校验失败前后测试日志|`work/e13-import-check/`|
|最终 CI 原始产物|本机上述 ZIP，含 `ci-e14/` 及 `ci-e14-services.log`|
|失败 CI 日志及产物|44004702497 的 four-services 任务及其 Artifact；已下载至本机 `~/devops_resources/B11_E13-E14_成员三/CI失败证据/`|
|实现和新增测试|`labs/e11e12/pipeline.py`、`test_fixed_report_hash.py`；`labs/e13e14/`；`.github/workflows/e13e14.yml`|

data/、work/ 及下载 ZIP 不随 Git 源码提交，最终作业需单独归档原始证据。本报告不将仅出现过的启动截断错误归因于已确认原因：该错误未复现，随后四服务创建和健康检查成功。

## 阶段结论

成员三的四服务固定样例与 CI 准备已完成，证据完整性已核验。本记录没有代替成员一、成员二负责的双方项目交叉测试、C1–C8 矩阵、三个新项目及完整扫描门禁。

E13 汇总和必要修复合并后，仍需在门禁通过的候选提交上执行配对实际项目四服务验证、受控故障恢复及发布前核对。本轮未选择候选提交，也未创建 v0.9-rc 标签。
