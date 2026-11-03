# AI 使用记录

## 工具与日期

- 使用者：王炜，学号 241880326
- 工具：Codex
- 日期：2026-11-03
- 实验：E8—E10，B 组 MDfixer；本记录覆盖已完成的 E8、E9 和 E10 部分。

## 输入上下文与问题

向 Codex 提供了课程材料位置、B 组身份、服务器环境检查结果，以及 E8 样例的报告、补丁和测试输出。讨论内容包括公共准备、服务器访问 GitHub 时的网络问题、E8 版本检查、补丁生成，以及三人小组的分工。

没有在此记录 GitHub 密码、访问令牌或设备授权码。

## 模型建议与采纳情况

- 按课程 E8 B 组手册生成固定 MD 报告，核对样例版本，生成候选补丁并验证旧报告被拒绝。
- 在现有 `test_profile.py` 中增加独立测试：构造只含冗余依赖的报告，检查补丁和修改计划为空，并检查 Makefile 字节不变。
- 使用个人分支和个人报告记录贡献，保留测试日志和 E8 证据。

上述 E8 测试建议已采纳。课程原有实现负责检测、补丁生成和版本检查；个人贡献是新增测试及实验记录。Codex 提供了测试代码建议和报告草稿。

## 人工操作与实际验证

本人在服务器完成 E8 样例运行、测试代码添加和测试执行，并检查输出。固定报告包含 `MISSING main.o/config.h` 与 `REDUNDANT main.o/unused.h`；候选补丁应用检查通过；模拟旧报告时得到 `STALE_REPORT` 且源文件未改变。

服务器测试命令在课程 Docker 镜像中运行：

```bash
python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v
```

实际结果：原有 7 项及个人新增 1 项，共 8 项通过；`TEST_EXIT_CODE=0`。服务器日志为 `work/unit-tests-20261103-111321.log`，E8 证据目录为 `work/e8-B-manual.FGe5JE`。

## E9 补充：共享变量分析

Codex 协助说明三种声明风格、建议并提供共享变量分析脚本，并在课件副本上预先验证该分析逻辑。本人在服务器执行手册样例、将 macro 候选应用到独立副本，并运行该扩展分析。

实际输出显示，修改共享的 `DEPS` 后，`main.o/config.h` 的 MISSING 消除，`helper.o/config.h` 被识别为 REDUNDANT；`SHARED_VARIABLE_ANALYSIS_PASS`、`STEP_EXIT_CODE=0`。证据目录为 `work/e9-B-manual.BH10Cm`，包含前后报告、候选补丁、计划和步骤日志。

本次扩展为独立样例分析，没有修改参考修复算法，也没有额外添加仓库单元测试。

## E10 补充：候选验证与编译失败扩展

Codex 协助解释拒绝、接受和回滚场景，提供真实 BuildChecker 重检与汇总步骤，并建议和提供独立的编译失败测试脚本；本人在服务器执行并检查了各步骤的真实输出。

实际结果：三项质量判定通过；真实 BuildChecker 重检无 MISSING，仍报告 `main.o/unused.h` 为 REDUNDANT。个人扩展中补丁可应用，但有意引入的 C 语法错误导致 `make app` 失败，候选被拒绝，源 Makefile 字节保持不变；`COMPILE_FAILURE_STUDY_PASS`、`STEP_EXIT_CODE=0`。

个人测试脚本位于 `docs/students/241880326/e8-e10/e10_compile_failure_study.py`，证据目录为 `work/e10-B-manual.uR50no`。该脚本独立运行，未加入 `test_profile.py` 的自动发现范围。

## 后续记录

E8—E10 的个人实验步骤与个人扩展已完成，提交后的 CI、组内合并和证据归档按实际情况记录。论文隐式规则与 LLM 相关机制仍待研读；后续如继续使用 AI，应记录实际输入、建议、本人修改和验证结果。