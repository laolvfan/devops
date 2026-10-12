# B11 E3 并行测试基线

## 提交范围与当前状态

本次按课件“B 组本次清单”和“E3 提交要求”整理材料：DRAFT 项目与功能验证条件、固定 MD 报告及修复样本，以及 README、环境、命令日志、仓库 SHA 和个人贡献。操作附录中的扩展示例不追加为提交任务。

DRAFT 已有目标失败与参考成功记录；MDFixer 固定报告、参考补丁及补充验证均已归档。现有材料可按提交清单汇总；DRAFT 历史环境与运行对应关系的缺口，按课件“未完成也要记录”的要求如实说明。

## 阅读入口

| 文档 | 内容 |
|---|---|
| [DRAFT 样例与重跑说明](draft.md) | 项目输入、失败原因、成功判据、Dockerfile 差异与重跑命令 |
| [MDFixer 样例与验证说明](mdfixer.md) | 固定 MD 报告、四种参考补丁、行为验证与拒绝恢复 |
| [贡献记录](contributions.md) | 成员工作、文件与已有提交证据 |
| [提交清单核对](review.md) | 逐项对应提交材料，并记录已知缺口 |

## 仓库分工与固定版本

保留两个仓库：主仓库维护项目实现及课程材料，MDFixer 实验仓库维护样例、Oracle 和参考补丁。这里归档选定版本的证据，通过 URL、commit 和文件摘要建立对应关系。

| 材料 | 固定版本 |
|---|---|
| DRAFT 素材 | [主仓库 e3-killy 材料提交](https://github.com/laolvfan/devops/commit/4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3) |
| MDFixer 报告、补丁与修复前记录 | [实验仓库材料提交](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/1efc4381cb1b5f5f8212c93cf082461eece50bb1) |
| MDFixer 固定源码 | [源码提交](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f)，对应 tag `e3-mdfixer-md-v1.0.0` |

DRAFT 的材料提交证明归档文件的来源，不能直接认定为历史运行时的源码 SHA。

## 来源与实际结果

| 材料 | 位置 | 性质 |
|---|---|---|
| DRAFT 同学提交的源码和日志 | [draft-original](evidence/draft-original/) | 从 e3-killy 的 4ddc1f9 原样导出，未重跑 Docker |
| MDFixer 同学提交的 Oracle、补丁和旧值记录 | [mdfixer-original](evidence/mdfixer-original/) | 从独立仓库 1efc438 原样导出 |
| MDFixer 本次新运行 | [summary.json](evidence/mdfixer-validation-001/summary.json) | 本机实际运行；记录操作系统、架构及工具版本 |
| 提交清单核对 | [review.md](review.md) | 清单与材料对应关系、已知缺口 |

原样导出的文件可能保留作者记录中的日期或时间，这是原始证据，未作改写。各原始材料目录中的 provenance.json 保存来源与逐文件 SHA-256。新运行目录的 sha256.json 保存输入快照、补丁和各步骤输出的摘要。

归档 README 中的旧状态描述属于原材料版本，汇总状态以本目录说明为准。固定 MD 报告标明 `INSTRUCTOR_ORACLE`，四种参考补丁是人工预期答案，不代表自动检测器或修复器已经实现。

## DRAFT 实际结果

| 场景 | 预期 | 实际观察 | 证据 |
|---|---|---|---|
| 故意失败 | 缺少 make，构建非零退出 | `make: not found`，整体构建退出码 1 | [失败日志](evidence/draft-original/evidence/draft-broken-004/build.log)、[退出码](evidence/draft-original/evidence/draft-broken-004/exit_code.txt) |
| 参考成功 | 构建退出码 0；运行输出 `hello E3`、退出码 0 | 与预期一致 | [成功构建](evidence/draft-original/evidence/draft-reference-002/build.log)、[运行输出](evidence/draft-original/evidence/draft-reference-002/run.log)、[运行退出码](evidence/draft-original/evidence/draft-reference-002/run_exit_code.txt) |

这些结果来自同学保存的原始日志，本次整理未重新执行 Docker。其他联网、文件名和权限失败按原因保留，详见 [检查结果](review.md)。

## MDFixer 补充验证

| 风格 | 修复前非 clean | 修复后 clean | 再改头文件非 clean | 无效候选 | 恢复原文件后的运行 |
|---|---|---|---|---|---|
| Target | 1 | 2 | 3 | 拒绝 | 3 |
| Macro | 1 | 2 | 3 | 拒绝 | 3 |
| Hybrid | 1 | 2 | 3 | 拒绝 | 3 |
| Implicit | 1 | 2 | 3，main.d 含 config.h | 拒绝 | 3 |

每种使用独立临时副本，先检查补丁再应用。commands.json 记录命令、退出码和预期输出，每个步骤的标准输出与错误输出单独保存。header-change 记录验证头文件确实比目标新；不依靠 clean build 单独宣称 MD 修复有效。

四种补丁共用同一个 Target 基线，各自得到一种修复后声明方式，详见 [样例说明](mdfixer.md#四种参考补丁及覆盖范围)。这些已验证的补丁作为清单中的“修复样本”提交。

无效候选是额外构造的 Makefile 补丁，在 all 中执行 false；检查其语法可应用后，以构建非零退出拒绝，再按字节恢复原始 Makefile 并重新构建。原始 Makefile 仍有 MD，恢复验证只证明回到可构建状态。

## 重跑方法

先克隆 MDFixer 实验仓库，并检出 `1efc4381cb1b5f5f8212c93cf082461eece50bb1`，确保基线 tag 也已获取。在本组仓库根目录执行（路径替换为实际克隆位置，输出目录必须尚不存在）：

```bash
python3 scripts/e3/verify_mdfixer.py \
  --lab-repo /tmp/b11-e3-mdfixer-review \
  --output work/e3-mdfixer-new-run
```

需要 Git、GCC、GNU Make 和 Python 3。脚本仅对本次已审阅的小样例运行构建命令，不修改输入仓库。完整克隆和重跑步骤见 [MDFixer 说明](mdfixer.md#重跑命令)，Docker 实验步骤见 [DRAFT 说明](draft.md#重新执行并留证)。每次使用新的输出目录。

原 MDFixer 记录使用 Ubuntu 24.04 / GCC 13 / Make 4.3，本机补充验证使用 Ubuntu 20.04 / GCC 9 / Make 4.2.1。新环境与原 `cfg-ubuntu24-gcc13-debug-v1` 不同，应单独保留环境，不把原 Oracle 的配置 ID 当成本机运行配置。

## 提交材料状态

统一索引、两条样例的重跑说明、预期与实际结果、固定输入版本及贡献记录已整理。各项材料的对应位置见 [提交清单核对](review.md#提交清单与材料对应)。

DRAFT 的历史环境、运行输入对应关系及镜像标识采集方法尚未完整记录，已在 [已知缺口](review.md#已知缺口) 说明。提交时保留这些说明，不用当前环境或新编写的重跑命令冒充历史记录。
