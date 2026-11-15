# E11–E12 个人报告

学号：241880100；小组：B11；轨道：DRAFT → MDFixer。
仓库：https://github.com/laolvfan/devops.git
分支：`e11-e12-integration`。
测试贡献提交：`7b45b9c04686f3aefe861bb1d8a17aa63c969f23`（已推送）。
E11 基础运行及扩展执行的源码基线：`859b1fd8178a0b8084545bdc3e3feecada0a35f7`；扩展测试执行时为新增文件，随后原样提交为上述测试贡献。

## E11 轨道集成

复用课程编排及已有 scan/patch/validate，通过 DRAFT 实际镜像构建与程序验证后，读取固定 MD 输入，生成 Makefile 补丁并做动态复验。DRAFT 重放预先保存的候选 Dockerfile，本次命令没有在线调用模型。

样例 base：`ee881a6f52311250ef9694df6058064f40466a24`。
target：`655b87109388e30d71772ed06839df7472112101`。

执行命令：

```bash
python3 run_e11e12.py run --request data/integration-sample/e11-b.json --out work/e11-b-241880100-02
```

实际退出码 0，result.json 为 SUCCEEDED。
job_id：`job-c5178313018a4233931a2e293e678b0f`。
trace_id：`trace-17686af7b6794f1884d717ca1b59c3ff`。

- DRAFT 首次构建退出码 1，识别 MISSING_MAKE；候选构建退出码 0。
- 最终镜像 ID：`sha256:2b3cea60c2d479f0164f0be9686bb9280b8f0ef282dc61daa50cfc56e87277a6`；运行输出 1，退出码 0。
- 固定 MD 的封装及 data.commit 均对应 target；schema_version=e11e12-1，kind=fixed-md。
- MDFixer 将 `main.o: main.c unused.h` 改为 `main.o: main.c unused.h config.h extra.h`。
- repair.input_report 的 URI/SHA256 指向本轮 fixed-md.json；阶段使用本轮 job_id/trace_id。
- 补丁应用、构建、功能测试、头文件变化重编译、无 MISSING 五项全部通过。
- 最终只保留 unused.h 的 REDUNDANT，符合只修 MD 的范围；96 个清单产物哈希核验一致。

E11 的输入是固定报告，不把它表述为 A 组本轮实时检测输出。

## 测试贡献

新增 `labs/e11e12/test_member100.py`，在已有补丁位置测试上增加真实行为验证：

|场景|独立预期|实际结果|
|---|---|---|
|macro|补到 DEPS，保留目标对宏的引用，两个头文件都能触发重编译|通过|
|mixed|补到目标依赖行，保留 HEADERS，两个头文件都能触发重编译|通过|
|过期报告|外层 commit 或内部 data.commit 不匹配，停止修复|均返回 STALE_REPORT，无补丁，源 Makefile 与目标快照均不变|

macro/mixed 中，修复前将 config.h 改为 2，程序仍输出旧值 1；修复后改动 config.h 输出 2，再将 extra.h 的 EXTRA 改为 3，输出 5，构建日志确认 main.c 被重编译。测试样例显式使用 VALUE+helper()+EXTRA，确保第二个头文件影响可观察输出。

过期报告测试为隔离版本检查，模拟了 DRAFT 成功及其结果文件，随后执行实际编排检查；不把该测试算作真实 Docker 构建证据。真实构建由上述 E11-B 运行提供。

容器内运行完整 unittest discover，21 项全部通过、退出码 0。命令、源码基线、测试文件 SHA256 见 `work/e11-extensions-241880100-02/run.json`；常规复跑入口为 `python3 run_e11e12.py test`。

## E12 跨组 API 验证

按 A11 交接包建立仅本机可访问的 SSH 隧道，核对主机指纹后访问 /health，并使用其课程样例请求。操作结束关闭隧道。

- 性质：课程参考连通性验证；未确认远端部署的是 B11 的上述提交。
- job_id：`job-795094e399a34f43baa58b13cae15352`。
- trace_id：`trace-767a015f0c6d4fddac41f0a46d3830ed`。
- 配置：`cfg-e11e12-bc70f4e9e436d256`。
- 远端样例 base：`6b33188cb464514c6a2baae75a8cedffb2ee4bc2`；target：`b091fc6f4ce391b2b50f79d983a25ebf5e3d8639`。
- draft/full-check/incremental-check/repair/recheck 五阶段成功；补丁 accepted；最终无 MD。
- 重复同键同输入复用任务、同键不同输入返回 409；184 项客户端检查通过，87 个产物下载哈希校验通过。
- 核验 repair 输入是本轮 incremental-check.json，五阶段 job_id/trace_id 一致。

原始记录在本机 `~/devops_resources/B11给A11交接/课程参考联调结果/`，包含客户端生成的 ZIP、回执、健康检查和控制台日志。B11 SHA 客户端参数仅记录版本，不执行部署。

## 真实项目与贡献边界

小组已有 241880326 完成的 cJSON 适配及本地 E12 结果，本人核查并整理为对外交接输入，不将其实现或运行记作本人独立完成。

项目：https://github.com/DaveGamble/cJSON；历史缺陷 PR #380。
base：`359567fdde253f311545a6c80b0fa6fb62e8ff09`；
target：`cf0d87a095becada87336ed786f11070e9a037b5`；
上游参考修复：`20cffa37a8f2d5d4811bb1dbba693c35c0d7f4a6`。

cJSON_Utils.o 缺少 cJSON.h 依赖。cjson_profile.py 提供该目标的映射、检测、补丁和验证，支持范围限定于此目标。326 的本地 E12 五阶段成功、补丁 accepted、最终 findings 为空，1650 个产物哈希核验一致。详细报告见 [cJSON 报告](https://github.com/laolvfan/devops/blob/7b45b9c04686f3aefe861bb1d8a17aa63c969f23/docs/students/241880326/e11-e12/cjson-report.md)。

后续已按 A11 新版交接完成下述真实项目跨组 API 验证；项目选题适用性仍需按课程要求确认。仅选取有真实历史的上游项目，不自动等同于满足“本组实际维护”的要求。

## 故障与处理

1. 环境构建访问 Docker Hub 超时，将 Docker CLI 镜像入口换为镜像站，保留原 tag/digest；构建和环境测试通过。
2. 首次 E11 候选构建下载 Debian 索引缓慢，停止该次构建并保留 work/e11-b-241880100-01。仅修改样例候选的 Debian HTTPS 镜像源及 apt update 超时，不更改共享服务器全局代理；-02 重跑成功。调整记录见 data/integration-sample/candidate-mirror-adjustment-100.json。
3. 首轮新增测试的 DRAFT 替身漏写结果文件，未进入版本检查；补齐夹具后完整套件通过。两轮证据分别保存在 work/e11-extensions-241880100-01 与 -02。

## 交付索引

|任务|证据位置|结果|
|---|---|---|
|E11-B|work/e11-b-241880100-02/：result.json、draft.json、fixed-md.json、repair.json、recheck.json、draft-build/、candidate.patch、validation/、final-full/|通过|
|扩展测试|labs/e11e12/test_member100.py；work/e11-extensions-241880100-02/：tests.log、run.json、cases/|21 项通过|
|接口决策|[ADR](ADR.md)|版本校验、MD 范围与行为验证|
|课程 API 联调|本机资料目录的原始 ZIP 和回执|通过，仅参考验证|
|cJSON|326 工作区 work/e12-cjson-241880326-02/，及小组交接包 evidence/ 同名目录|本地及跨组 API 技术验证通过；选题口径另确认|

data/、work/ 被 Git 忽略，运行证据单独归档；仅提交报告不会携带这些原始产物。

## cJSON 跨组 API 验证补充

采用新版真实项目交接请求，在本机独立提交、轮询、下载一轮任务，实际服务指纹与约定相符。A11 保留其编排/API 并接入 B11 适配；不是直接部署 B11 整个仓库。

- 服务源码 SHA：`47fe83823f24c04e5bad36467f453a3296b1eed0`；B11 来源 SHA：`7b45b9c04686f3aefe861bb1d8a17aa63c969f23`。
- 实现指纹：`dd0d81c2e44ea829a18a7502470ce576ded6e1db7724ce7ce29e18b9e62762a8`，服务 health 和本轮 manifest 均通过比对。
- job_id：`job-80afbdd237724fd19cb49db9ec23b147`；trace_id：`trace-7c270c4ae26845b7aeb7ce766b1fac9b`。
- cJSON base/target 与前述约定一致；五阶段成功，补丁 accepted，全部五项验证通过，最终 findings 为空。
- 210 项客户端检查通过，89 个产物传输 SHA256/大小均匹配；同时核对本轮基线缓存、增量/全量一致性、修复输入和阶段身份。
- 证据：本机 `~/devops_resources/B11给A11交接/cJSON正式联调结果/`，包含原始 ZIP 和回执。本轮未修改自动生成的证据，结束后关闭隧道。

这是第三方开源项目历史缺陷的功能/接口复现，不声明本组原本维护 cJSON，也不把技术验证通过等同于老师已认可选题例外。新交接包清单列出的“联调全景与提交材料.md”未附带；实际脚本和输入哈希均匹配，缺失文件不参与执行。
