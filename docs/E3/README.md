# B11 E3 提交材料

按课件 B 组提交清单归档 DRAFT 与 MDFixer 的样例、人工参考答案和实际运行记录。

## 提交清单

| 内容 | 材料入口 |
|---|---|
| DRAFT 项目、功能验证条件和失败日志 | [DRAFT 实验说明](draft.md) |
| 固定 MD 报告、参考补丁和修复验证 | [MDFixer 实验说明](mdfixer.md) |
| 环境、命令、预期与实际结果 | 上述两份实验说明及链接的原始记录 |
| 仓库与 SHA | 下方版本表 |
| 个人贡献 | [贡献记录](contributions.md) |
| 完成状态与下一步 | 下方完成状态 |

## 来源与版本

主仓库保存项目和提交材料，MDFixer 实验仓库独立维护样例。以下链接包含各材料的完整 commit SHA。

| 材料 | 固定版本 | 归档 |
|---|---|---|
| DRAFT 源码、Dockerfile 与日志 | [devops / e3-killy：4ddc1f9](https://github.com/laolvfan/devops/commit/4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3) | [draft-original](evidence/draft-original/) |
| DRAFT 本机补充验证 | 从上述提交直接导出输入，构建前后摘要一致 | [实际运行结果](evidence/draft-validation-005/summary.json) |
| MDFixer 报告、补丁与修复前记录 | [DevOps-E3-Lab-Kit：1efc438](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/1efc4381cb1b5f5f8212c93cf082461eece50bb1) | [mdfixer-original](evidence/mdfixer-original/) |
| MDFixer 固定源码 | [4fdc623](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f)，tag `e3-mdfixer-md-v1.0.0` | [验证输入](evidence/mdfixer-validation-001/source/) |
| MDFixer 本机补充验证 | 使用上述源码和补丁 | [实际运行结果](evidence/mdfixer-validation-001/summary.json) |

两份原始归档的 `provenance.json` 和补充验证的 `sha256.json` 保存文件摘要。原始文件的时间、日志及旧 README 原样保留；当前状态以本目录说明为准。

## 完成状态

按 B 组 E3 提交清单，当前没有已知未完成项，可提交本目录材料。

DRAFT 已通过一次完整复跑补齐宿主与容器环境、固定源码、实际命令、退出码及镜像采集记录，详见 [DRAFT 实验说明](draft.md)。本次复跑作为完整验收记录，原始日志保留作为历史材料。
