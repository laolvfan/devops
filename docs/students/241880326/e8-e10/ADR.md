# 决策记录：E8—E10 候选补丁与版本保护

- 姓名：王炜
- 学号：241880326
- 轨道：B 组（MDfixer）
- 阶段：E8、E9、E10
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

保留冗余依赖可能导致不必要的重新构建。E8 阶段覆盖直接枚举风格和仅含冗余依赖的报告；E9 的混合风格和共享变量分析见下方补充，复杂 Make 规则仍需单独验证。

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

## E9 补充：共享变量的影响范围

在独立的 macro 样例中，让 `main.o` 和 `helper.o` 共同引用 `DEPS`。报告的唯一 MISSING 是 `main.o/config.h`；参考实现将 `config.h` 添加到 `DEPS` 定义。

该修改修复了目标的缺失依赖，也使 `helper.o` 获得 `config.h` 声明；重新扫描将后者识别为新的冗余依赖。分析的 `SHARED_VARIABLE_ANALYSIS_PASS` 和退出码 0 表明预期的影响已被观察到，不表示问题已修复。

可考虑在识别共享变量时为目标选择更局部的声明位置，但该替代方案尚未实现；需要对目标依赖、声明风格和构建行为进一步验证。原始样例、补丁及前后报告保存在 `work/e9-B-manual.BH10Cm`。

## E10 补充：候选验证与失败保护

对候选先在验证副本中执行补丁应用、构建、功能测试、头文件变化和缺失依赖重检；这些检查全部通过后才将 Makefile 写回样例源项目。这样便于保留失败案例及其证据，代价是执行构建和验证需要额外时间与空间。

本次分别验证：故意设置错误功能测试预期时拒绝；所有检查通过时接受；无效补丁在应用检查阶段拒绝。两次拒绝都确认源 Makefile 字节保持不变。独立扩展还验证了补丁可应用但编译失败时会拒绝，源文件保持不变。

最终的独立 direct 样例通过真实 BuildChecker 重检，未发现 MISSING；本次构建配置下仍报告 `main.o/unused.h` 为 REDUNDANT。报告与日志位于 `work/e10-B-manual.uR50no`。这些结果的范围为课程受限样例，不能替代对其他 Make 规则和项目的验证。