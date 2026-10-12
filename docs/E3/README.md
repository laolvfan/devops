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
| 未完成项、卡点与下一步 | 下方已知缺口 |

## 来源与版本

主仓库保存项目和提交材料，MDFixer 实验仓库独立维护样例。以下链接包含各材料的完整 commit SHA。

| 材料 | 固定版本 | 归档 |
|---|---|---|
| DRAFT 源码、Dockerfile 与日志 | [devops / e3-killy：4ddc1f9](https://github.com/laolvfan/devops/commit/4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3) | [draft-original](evidence/draft-original/) |
| MDFixer 报告、补丁与修复前记录 | [DevOps-E3-Lab-Kit：1efc438](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/1efc4381cb1b5f5f8212c93cf082461eece50bb1) | [mdfixer-original](evidence/mdfixer-original/) |
| MDFixer 固定源码 | [4fdc623](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f)，tag `e3-mdfixer-md-v1.0.0` | [验证输入](evidence/mdfixer-validation-001/source/) |
| MDFixer 本机补充验证 | 使用上述源码和补丁 | [实际运行结果](evidence/mdfixer-validation-001/summary.json) |

两份原始归档的 `provenance.json` 和补充验证的 `sha256.json` 保存文件摘要。原始文件的时间、日志及旧 README 原样保留；当前状态以本目录说明为准。

## 已知缺口

DRAFT 原始记录存在以下缺口，按课件“未完成也要记录”的要求随材料提交：

| 缺口 | 已核对内容 | 后续获取方式 |
|---|---|---|
| 宿主 OS、架构与 Docker 版本 | 构建日志可提取容器包版本和基础镜像摘要 | 原运行者若保留环境记录，可补入 |
| 原始完整命令及运行时源码状态 | 已记录素材提交；它不能代替运行时 SHA/工作区状态。文档中的重跑命令为后来整理 | 原运行者若保留终端记录，可补运行上下文 |
| 镜像标识的采集方式 | `image_id.txt` 与日志中的 manifest list 摘要相同，未保留采集命令或 inspect 输出 | 如仍保留原镜像或采集记录，可补来源说明 |
