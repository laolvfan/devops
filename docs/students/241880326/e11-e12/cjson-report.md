# E11–E12：cJSON 真实项目接入

## 基本信息

- 学号：241880326
- 小组：B 组
- 个人分支：`student/241880326/e11-e12-cjson`
- 真实项目：[DaveGamble/cJSON](https://github.com/DaveGamble/cJSON)
- 上游缺陷与修复：[PR #380](https://github.com/DaveGamble/cJSON/pull/380)

## 实验对象

- 基线提交：`359567fdde253f311545a6c80b0fa6fb62e8ff09`
- 待修复目标提交：`cf0d87a095becada87336ed786f11070e9a037b5`
- 上游参考修复：`20cffa37a8f2d5d4811bb1dbba693c35c0d7f4a6`

目标版本的 `cJSON_Utils.o` 实际依赖 `cJSON.h`，但 Makefile
未声明该依赖。工具生成的补丁在 `$(UTILS_OBJ)` 规则中补充
`cJSON.h`，与上游修复内容一致。

## 个人工作

- 增加针对 cJSON 的目标映射、依赖检测和补丁生成。
- 将 cJSON 适配接入 E12 编排，增加真实项目的构建、测试、
  头文件变化重编译和动态重检。
- 增加测试，覆盖变量形式的目标、旧报告拒绝、补丁验证、
  快照接入、候选约束和 API 输入路径限制。
- 保存实验用 Dockerfile，并使用可访问的 Debian 镜像源。
- 使用 Codex 协助代码实现、命令编写和结果分析；实际服务器
  命令及输出由本人执行和核对。

## 真实项目运行结果

- 状态：`SUCCEEDED`
- job_id：`job-3b64006307384552bcdb63809baa1750`
- trace_id：`trace-e99cf992e4514189aa9c6e5bb6abefb9`
- 阶段：draft、full-check、incremental-check、repair、recheck
- 补丁验证：`accepted=True`
- 验证项：`{'patch_applies': True, 'build': True, 'test': True, 'header_change': True, 'no_missing': True}`
- 服务器证据目录：`work/e12-cjson-241880326-02/`
- 控制台日志：`work/e12-cjson-241880326-02-console.log`

## 固定样例回归

- E11-A：`SUCCEEDED`
- E11-B：`SUCCEEDED`
- E12：`SUCCEEDED`
- 证据目录：`work/cjson-regression-e11-a/`、
  `work/cjson-regression-e11-b/`、`work/cjson-regression-e12/`
- 契约及新增测试：16 项通过。

## 故障与处理

首次真实项目运行在 DRAFT 的依赖下载步骤达到 600 秒超时。
检查日志后，保留原有记录，使用 Debian 镜像源生成新候选并
重新运行，五个阶段成功。首次证据目录：
`work/e12-cjson-241880326-01/`。

## 范围

cJSON 适配限定于 `cJSON_Utils.o`，每次对目标进行新的 GCC
依赖观察；完整的 A/B API 联调和远端 CI 状态以实际记录为准。
`data/` 和 `work/` 为本地忽略目录，证据需按课程要求另行归档。
