# B11 DevOps 课程项目

B11 负责 DRAFT（生成可构建环境）和 MDFixer（修复缺失依赖）。E2、E3 已完成，E4 已完成可重复工程环境与组内验收。

## E3 测试基线

见 [B11 E3 材料索引](docs/E3/README.md)。已完成 DRAFT 失败与参考成功验证、MDFixer 四种补丁及拒绝恢复验证；环境、命令、源码版本、镜像信息和贡献记录均已归档。
## E4 可重复工程环境

见 [B11 E4 环境与验收](docs/E4/README.md)。已导入教师 B-draft 模板至 `services/draft/`，三个学号目录均有构建、测试、冒烟和密钥检查记录，`241880100` 与 `241880581` 的同 SHA 重跑对照通过。

## E5–E7 DRAFT 工程

见 [B11 E5–E7 DRAFT 工程](docs/E5/README.md)。已整合候选构建验证、故障测试及 CI 配置；统一运行入口为 `python3 scripts/lab_cloud.py`。
