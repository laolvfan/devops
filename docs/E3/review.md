# B11 E3 提交清单核对

## 范围

按本机 devops_resources 中 E3 课件的“B 组本次清单”和“E3 提交要求”核对，范围为 DRAFT 和 MDFixer。操作附录用于理解实验方法，不将其中的扩展示例追加为本次提交任务。

杨晨昊的 DRAFT 资料来自 origin/e3-killy，检查版本为 `4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3`。MDFixer 来自独立实验仓库，检查版本为 `1efc4381cb1b5f5f8212c93cf082461eece50bb1`。

## 提交清单与材料对应

| 清单内容 | 提交材料 | 状态 |
|---|---|---|
| DRAFT 项目与功能验证条件 | [源码与 Dockerfile](evidence/draft-original/fixtures/draft/)、[构建与功能验证说明](draft.md) | 已整理：`make`；`./hello` 输出 `hello E3`、退出码 0 |
| 可定位的构建失败日志 | [目标失败日志](evidence/draft-original/evidence/draft-broken-004/build.log)、[退出码](evidence/draft-original/evidence/draft-broken-004/exit_code.txt) | 已保存 `make: not found` 和整体构建退出码 1 |
| 固定 MD 报告及修复样本 | [固定报告](evidence/mdfixer-original/oracle/mdfixer/md-report.json)、[对应源码](evidence/mdfixer-validation-001/source/)、[参考补丁](evidence/mdfixer-validation-001/patches/)、[验证说明](mdfixer.md) | 已具备固定输入、参考答案和实际修复验证 |
| 项目、预期结果与实际观察分别保存 | [材料索引](README.md)、两条样例说明及 `evidence/` | 已区分人工 Oracle/参考答案与真实运行记录 |
| README、命令与日志 | [DRAFT 说明](draft.md)、[MDFixer 说明](mdfixer.md)、各原始及验证证据目录 | 重跑命令已整理，已有实际日志保留；DRAFT 原始完整命令未留存，见下方说明 |
| 环境信息 | [MDFixer 原环境](evidence/mdfixer-original/evidence/20260929T104529-b2/observations.json)、[本机验证环境](evidence/mdfixer-validation-001/summary.json)、[DRAFT 日志可提取信息](draft.md#固定材料与原始结果) | MDFixer 已记录；DRAFT 仅有部分信息，历史宿主环境缺口已列明 |
| 仓库、SHA 与个人贡献 | [仓库和固定版本](README.md#仓库分工与固定版本)、[贡献记录](contributions.md) | 已记录真实来源与成员工作；DRAFT 材料 SHA 与运行时 SHA 的区别已说明 |
| 未完成项、当前记录、卡点与下一步 | [已知缺口](#已知缺口)、原始代码和失败记录 | 按现状记录，保留可核对证据与后续获取方式 |

现有实验结果和说明按以上清单提交。DRAFT 信息不完整的部分作为已知缺口随材料保留，不以补跑全部实验或另建四种故障基线作为提交前提。

## DRAFT 检查结果

| 项目 | 观察 | 结论 |
|---|---|---|
| 源码和 Makefile | main.c 输出 hello E3；Makefile 编译为 hello | 输入代码符合课件小样例 |
| 故意失败 | draft-broken-004/build.log 含 make: not found；记录构建退出码 1 | 符合目标失败；日志中的步骤退出码 127 与整体构建退出码 1 不矛盾 |
| 参考成功 | draft-reference-002 构建退出码 0、运行输出 hello E3、运行退出码 0 | 已保存两层成功证据 |
| 基础镜像 | 失败与成功日志均解析到同一 python 基础镜像 digest | 可从日志追溯基础镜像内容 |
| 其他失败尝试 | broken 为联网超时；broken-002 为 COPY 找不到 Makefile；broken-003、reference-001 为 Docker 权限失败 | 应保留并分类，但不能充当缺工具链的目标失败 |

这些是对同学已提交日志的检查，本次没有重新运行 Docker 或确认原服务器状态。

## DRAFT 可重复性信息

1. 原 `E3实验包/fixtures/draft/README.md` 只写到 make 命令，代码块未闭合。本次已在 [DRAFT 说明](draft.md) 补齐 ./hello、预期输出、退出码、Docker 重跑命令、构建上下文和证据位置；原始归档不改写。
2. 缺独立的环境记录：操作系统、CPU 架构、Docker、编译器和 GNU Make 版本。部分 apt 版本可从已有日志提取，但不能用当前本机环境冒充历史运行环境。
3. 缺每次运行的命令及输入 SHA 对应关系。Git 提交证明文件何时纳入历史，但不能自动证明运行时工作区干净或使用了哪次提交。固定输入应分别说明源码提交与完整 Dockerfile 所在提交。
4. `image_id.txt` 内容与构建日志的 manifest list 摘要相同；日志另有 config 摘要。缺采集命令，暂不能据此断言错误，也不能直接认定为已核实的 Docker image inspect .Id。提交时保留原文件，并按日志中可确认的标识类型说明。

已提交素材可追溯到：

- 输入源码：`c70c1d5f827de0e6a519cd7fb0a4aaed261d54ab`。
- 失败 Dockerfile、大小写路径修正和失败日志：`42b1b7d444ca83332d44832e302f08e2bfd04bdd`。
- 参考 Dockerfile 与成功日志：`4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3`。

以上 SHA 为素材提交，不补造运行时 SHA。

## MDFixer 固定输入与完成情况

`https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit` 的版本 `1efc4381cb1b5f5f8212c93cf082461eece50bb1` 包含固定报告、四种补丁及旧值复现记录。标记 `e3-mdfixer-md-v1.0.0` 为 annotated tag，解引用后的源码 commit 为 `4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f`，与报告一致。

本次继续检查与验证：报告版本对应源码、Oracle 来源明确、只改 config.h 能复现旧值、每个补丁的目标文件和风格正确。随后在独立副本执行 git apply --check、应用补丁、clean 输出 2、再次修改头文件后非 clean 输出 3；保存无效候选拒绝与恢复验证。

同学原始证据、本机新增运行及人工预期已分别保存。现有四种参考补丁的本机实际验证已完成，证据目录、重跑说明和贡献记录已整理。DRAFT 历史环境和运行命令的缺口在下方如实记录。

## MDFixer 补充检查与结果

独立仓库 README 明确定位为样例、Oracle 和证据仓库，服务代码留在本组工程；不需要将两个仓库合成一个才能验证。所有来源 URL、基线与实验包版本分别记录。

四种补丁都是从同一个显式 Target 基线转换为四种目标声明风格。按提交清单，它们作为已验证的修复样本归档；另建 Macro、Hybrid、Implicit 原始故障基线不列为本次提交任务。材料只说明已实际验证的输入与结果。

本机 GCC 9 / GNU Make 4.2.1 与原记录 GCC 13 / GNU Make 4.3 不同，新增结果仅证明该独立环境中的行为，未覆盖原配置下的重复运行。

Target、Macro、Hybrid、Implicit 均通过：旧值 1 → 修复后 clean 输出 2 → 再改头文件后非 clean 输出 3；Implicit 的 main.d 包含 config.h。每种还验证了无效候选失败、原始 Makefile 字节恢复、clean 构建和功能运行成功。恢复的是原始缺依赖版本，不表示恢复后缺陷被修复。

详见 [证据索引](README.md)。[贡献记录](contributions.md) 按实际任务沟通登记成员工作，并保留独立仓库 Git 作者显示为 CodexAI 的事实。

## 已知缺口

以下按课件“未完成也要记录”的要求随现状提交。

| 项目 | 已有记录与卡点 | 后续获取方式 |
|---|---|---|
| DRAFT 原运行环境 | 已检查构建日志并提取容器包版本和基础镜像摘要；原宿主 OS、架构、Docker 版本没有单独记录 | 原运行者若能找回历史环境记录，可补入材料；当前本机信息不能冒充原环境 |
| DRAFT 运行输入与命令 | 已追溯输入及 Dockerfile 的素材提交，补写重跑说明；原始完整命令和运行时工作区状态未留存 | 若原运行者保留终端记录，可补命令、工作目录和源码对应关系；重跑说明明确作为后续执行方法 |
| DRAFT 镜像标识来源 | 已比对 `image_id.txt` 与日志中的 manifest list 摘要；未记录采集命令 | 如仍保留原镜像或采集记录，可补标识来源；现有文件按已知类型说明 |

后续若选择重跑，可使用 [DRAFT 重跑说明](draft.md#重新执行并留证) 另建目录保存新证据。现有缺口已登记，不自动追加重跑任务。
