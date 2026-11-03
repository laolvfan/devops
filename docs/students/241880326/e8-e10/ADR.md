# 决策记录：E8 候选补丁与版本保护

- 姓名：王炜
- 学号：241880326
- 轨道：B 组（MDfixer）
- 阶段：E8
- 日期：2026-11-03

## 背景与约束

教学样例中，`main.c` 包含 `config.h`，但 `main.o` 的 Makefile 依赖声明缺少该头文件；报告还发现 `unused.h` 是冗余依赖。课程参考实现处理受限 C/Make 样例，E8 使用直接枚举声明风格。

本次 E8 需要依据与样例版本匹配的固定报告生成候选补丁，并保存原始输入、计划、补丁和拒绝案例的证据。

## 选择与替代方案

本次沿用课程参考实现的策略：

1. 对报告中标记为 `MISSING` 的依赖生成候选补丁，在 `main.o` 的依赖列表中增加 `config.h`。
2. 保留 `REDUNDANT` 依赖，不自动删除 `unused.h`。
3. 比较报告记录的 commit 与样例项目当前 Git HEAD；不匹配时以 `STALE_REPORT` 拒绝生成候选。
4. 生成补丁时保留原始 Makefile，使用 `git apply --check` 检查补丁是否能应用。

另一种方案是同时自动删除冗余依赖；本次没有采用，需要另行验证删除对项目构建行为的影响。

## 代价与覆盖范围

保留冗余依赖可能导致不必要的重新构建。本次测试的输入覆盖直接枚举风格和仅含冗余依赖的报告；共享变量、混合风格和复杂 Make 规则需要后续单独验证。

版本检查比较报告中的 commit 和当前 HEAD。本次实验在干净样例上进行；只有 commit 相同并不能单独证明工作区文件未发生未提交修改。

`git apply --check` 验证补丁的适用性；补丁后的构建、功能测试、头文件变化和动态重检留待 E10。

## 验证命令与实际证据

- 证据目录：`work/e8-B-manual.FGe5JE`
- 输入报告：`fixed-md-report.json`
- 输出：`candidate.patch`、`patch-plan.json`
- 计划风格：`direct`；补丁给 `main.o` 增加 `config.h`
- 应用检查：`APPLY_CHECK_PASS_SOURCE_CLEAN`
- 不匹配报告：`EXPECTED_REJECTION STALE_REPORT`，并确认 `SOURCE_BYTES_UNCHANGED`
- 个人测试：`Student241880326E8.test_redundant_only_does_not_remove_dependency`
- 个人测试结果：课程测试集共 8 项通过，`TEST_EXIT_CODE=0`；日志 `work/unit-tests-20261103-111321.log`

本记录聚焦已完成的 E8。E9 的共享变量处理和 E10 的候选验证、接受与回滚，在对应实验完成后补充。