# B11 E7 实验结果

学号：241880326；GitHub：WwNotVvvv；轨道：B / DRAFT。

## 输入、实现与个人工作

使用 P1 已完成 E5 的 `work/candidate/error-mirror/Dockerfile`，候选 SHA256 为 `5d4f3abf8f5aeb7907bb89baa9f94341af0ba4b3415cde3db21b07bab03c9f96`。来源记录 `work/candidate/provenance.json` 保存 ChatGPT 错误驱动回复及人工换源调整。E7 读取保存的候选执行验证，模型回复生成与 E5 手工构建归属 P1。

核心 auto-build 实现与原始五场景 runner 来自教师参考及小组 main。E7 新增：多阶段候选提前拒绝的自主测试、六项独立判定测试、CI 交接检查和原始证据归档；实际执行失败与恢复的版本退出码测试。

## 服务器验证

|项目|实际结果|
|---|---|
|服务器|Ubuntu 22.04.5 LTS，x86_64，2 CPU，3.5 GiB 内存|
|Docker / Compose / Buildx|29.1.3 / 2.40.3 / 0.30.1|
|宿主 Python / Make / Git|3.10.12 / 4.3 / 2.34.1|
|源码|`dbc1278d421a5d8b0441e800a8684a5a9d590eda`，服务器 `/root/devops-e7.d149Jj`|
|服务镜像|`e7-draft:241880326`；完整 inspect 保存在构建证据的 image/stdout.log|
|独立判定测试|6 项通过|
|服务测试|26 项通过；构建测试阶段退出码 0|
|完整门禁|六项检查全通过，整体退出码 0|

环境记录为 `work/e7-env-241880326.json`；构建记录为 `work/e7-build-20261020-112001/`；完整门禁目录为 `work/e7-gate-20261020-112209/`。以上路径相对于服务器仓库。用户提供的终端结果摘录见 `server-evidence/gate-user-summary.json`，原始 JSON、CSV、镜像信息和日志以服务器上述目录为准。

|场景|工具状态 / 退出码|实际判断|
|---|---|---|
|正常候选|SUCCEEDED / 0|两轮构建完成，按构建镜像 ID 运行，输出 hello E3|
|输出不符|FAILED / 1|输出与故意错误的预期不匹配，场景通过|
|无效候选|FAILED / 1|修改 CMD 的候选在构建前被拒绝，场景通过|
|候选构建失败|FAILED / 1|第二轮失败后停止程序验证，场景通过|
|运行超时|TIMED_OUT / 1|第二轮已构建成功，运行超时后容器清理检查通过|

## 正常 CI 与分支保护

功能 [PR #2](https://github.com/laolvfan/devops/pull/2) 已合并，合并提交为 `89c34c249562b19f321fa51696cb9f6c8d6f83cb`。

正常 CI 为 [39362321293](https://github.com/laolvfan/devops/actions/runs/39362321293)。head 是 `dbc1278`，实际检出 PR 合并测试提交 `7cd47ad59e3a9b5dfa8909bbef56f5447aba1f59`；两者分别记录。独立判定、源码与镜像扫描、服务构建及完整六项 gate 均通过。原始 artifact、gate JSON、CSV 和运行元数据保存在 `ci-evidence/normal/`。

main 的分支查询返回 protected=true，必需检查 `e7-b-quality-gate` 绑定 GitHub Actions App ID `15368`，状态检查对所有角色执行。可见字段见 `ci-evidence/protection-observed.json`。所有者通过界面配置保护；现已补充实际完整保护配置 `ci-evidence/protection-full.json`，确认 strict=true、enforce_admins=true、审批人数为 0。

## 同一 PR 的失败与恢复

演示 [PR #3](https://github.com/laolvfan/devops/pull/3) 从已合并的 E7 功能版本建立。故意把 version 的成功退出码预期写成 1，实际返回 0；生产实现未修改。

- 失败提交：`6944e887fd422ebf7d272cf399a5fa2e00316cb7`。
- 失败 CI：[39396123591](https://github.com/laolvfan/devops/actions/runs/39396123591)，服务测试为 `1 failed / 26 passed`，断言 `assert 0 == 1`。
- PR 状态：OPEN / BLOCKED。普通 REST 合并请求返回 HTTP 405，消息为 `Required status check "e7-b-quality-gate" is failing.`；执行进程退出码为 1。
- 合并请求使用预期 head SHA 与正常 merge 方法，没有管理员绕过。请求与响应保存在 `ci-evidence/rejection/merge-attempt.json`，原始失败 artifact 和断言日志同目录保存。
- 修正提交：`cef2d97d91a380eb6fcfd15362f0301a5d1a2089`，将预期恢复为 0。本地完整相关测试为 33 项通过（27 项服务测试、6 项判定测试）。

恢复 CI 为 [39396645261](https://github.com/laolvfan/devops/actions/runs/39396645261)，27 项服务测试及全部五个真实场景通过，六项 gate 检查全部 passed=true。原始 artifact、JSON、CSV 和提交元数据保存在 `ci-evidence/recovery/`，ZIP 哈希与 GitHub 返回的 digest 一致。

最后的报告与归档脚本提交晚于上述恢复执行，运行输入保持一致；保护规则还会要求最新提交的 CI 通过后才能合并。最终合并状态以 PR #3 的实际记录及服务器提交目录中的 merge 记录为准。

## 验证范围与交付

最终 E6/E7 整合运行版本为 `691826bf6dbb78b284e88c7df0ad4d6c5b6a04cf`，已纳入成员 E6 分支的来源标记、候选原始字节哈希和固定摘要修复。服务器在独立目录 `/root/241880100/devops-final-e67` 构建服务镜像，32 项服务测试通过；E6 两轮构建及证据校验通过，E7 服务测试与五个真实场景全部通过。新证据为 `work/final-e67-build/`、`work/final-e6/`、`work/final-e7/`，版本和镜像 ID 汇总见 `docs/E6/final-validation.json`。历史 CI、失败拒绝及 PR #3 合并记录继续保留，不替换为新版运行记录。

main 的实际完整保护配置已补存到 `ci-evidence/protection-full.json`，核实 strict=true、enforce_admins=true，必需检查为 `e7-b-quality-gate`，审批人数为 0。最终整合 PR 仍遵守相同门禁。

整合 PR 的首次 CI（运行 `39597617741`）因 runner 无法解析 DaoCloud 域名而在服务镜像元数据拉取处失败，没有执行目标场景。CI 改为通过构建参数从 Docker Hub 拉取相同摘要的 Python 和 Docker CLI 镜像；服务器 Dockerfile 默认值不变。该网络调整没有改变基础镜像摘要或服务实现，失败日志保存在 `ci-evidence/integration-infrastructure-failure.log`。

两次集成独立审查覆盖 CI 权限、交接契约、shell 与判定；归档专项检查发现完成条件不足，已补充 CI 结论、恢复 gate 与运行输入等价验证。真实 CI 包的临时目录归档通过，失败恢复包会被拒绝；检查未访问真实 `/root/submit`。服务器的相同生产逻辑场景不重复运行，恢复由完整 CI 验证。

候选及下载 artifact 的哈希用于输入来源和传输完整性；普通源码未另外计算哈希。历史根目录契约测试的路径问题与 E7 改动分开记录，未重复运行已有失败记录的无关测试。

统一提交根目录为 `/root/submit`，E7 使用 `/root/submit/E7`。`scripts/submit_e7.sh` 在验证最终合并提交、原始服务器 gate、三份 CI 的结论、ZIP digest、恢复 gate 和运行输入一致性后整理产物；服务器输出 `ARCHIVE_COMPLETE=/root/submit/E7` 时才确认最终交付。提交目录内的 CSV、报告及交接 JSON 会补齐实际 MERGED 记录。
