# B11 E3 贡献记录

按实际任务参与和材料来源登记。Git 作者名保留原记录；成员负责的工作与提交作者字段分别说明。

| 成员 | 已完成工作 | 可追溯证据 |
|---|---|---|
| 杨晨昊 | 准备 DRAFT Tiny Greeting 源码、Makefile、失败 Dockerfile 与参考 Dockerfile；保存失败排查、目标失败和成功运行记录 | 主仓库 `e3-killy` 分支的 [输入提交](https://github.com/laolvfan/devops/commit/c70c1d5f827de0e6a519cd7fb0a4aaed261d54ab)、[失败实验提交](https://github.com/laolvfan/devops/commit/42b1b7d444ca83332d44832e302f08e2bfd04bdd)、[参考成功提交](https://github.com/laolvfan/devops/commit/4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3)；原 Git 作者为杨晨昊 |
| 王炜 | 在独立实验仓库准备 MDFixer 固定源码、Oracle MD 报告、修复前旧值实验和四种参考补丁 | [源码基线](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f)、[材料版本](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/1efc4381cb1b5f5f8212c93cf082461eece50bb1)、[原始归档](evidence/mdfixer-original/)；该仓库材料提交的 Git 作者显示为 `CodexAI`，王炜为本组沟通中对应的 MDFixer 同学 |
| 阳旅帆 | 使用 Codex 辅助检查两条样例材料，补充四种参考补丁的实际行为验证与拒绝恢复实验，整理证据、重跑说明及待补项 | [验证脚本](../../scripts/e3/verify_mdfixer.py)、[实际运行结果](evidence/mdfixer-validation-001/summary.json)、[材料索引](README.md)、[检查清单](review.md) |

## AI 辅助范围

本次 Codex 辅助工作包括课程要求与材料核对、验证脚本编写和本机执行、原始证据归档、文档整理与概念解释。四种参考补丁来自同学提供的实验仓库；本机验证另行构造了用于拒绝实验的无效候选。

AI 整理的说明、课程人工 Oracle 和真实运行日志分别保存。没有根据历史结果补造环境、源码 SHA、运行命令或个人提交；最终材料提交的 SHA 应取实际 Git 记录。
