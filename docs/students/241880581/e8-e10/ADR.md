# 决策记录

背景与约束：B 组 E9 要针对显式 Make 依赖，比较 direct、macro、mixed 三种声明风格；报告必须对应当前样例提交，补丁先作为候选验证，不应改动原始输入。

选择与替代方案：direct 风格在目标依赖行增加 config.h；macro 风格修改 DEPS 定义并保留目标对变量的引用；mixed 风格保留 HEADERS 宏并在目标行增加 config.h。通过临时副本运行 git apply --check 和应用演示，不直接修改原始输入。相较于统一展开变量后重写目标，按声明风格选择最小修改能保留现有结构。

代价与覆盖范围：仅覆盖课程明确支持的显式规则和简单变量形式。隐式规则与复杂 Make 语法不在本次 E9 覆盖范围内。E10 已在独立样例中验证构建、测试、头文件变化重检和失败回滚；三种判定均符合预期，证据见 `work/e10-B-manual.VooRhZ/`。

验证命令与实际证据：E9 三种风格的 `lab_python` 分步记录均为 STEP_EXIT_CODE=0；`macro.patch` 在 apply-demo 副本成功应用且原 macro 项目未改；个人测试 `StudentE9B.test_macro_style_patch_updates_definition` 通过。证据位于 `work/e9-B-manual.OTsboc/`，测试日志为 `work/unit-tests-20261103-112614.log`。
