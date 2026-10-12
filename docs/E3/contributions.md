# B11 E3 贡献记录

| 成员 | 已完成工作 | 提交证据 |
|---|---|---|
| 杨晨昊 | 准备 DRAFT Tiny Greeting 源码、Makefile 和初始 README | [c70c1d5](https://github.com/laolvfan/devops/commit/c70c1d5f827de0e6a519cd7fb0a4aaed261d54ab) |
| 杨晨昊 | 编写缺少工具链的 Dockerfile，修正文件名大小写，保存失败排查及 `make: not found` 的目标失败记录 | [42b1b7d](https://github.com/laolvfan/devops/commit/42b1b7d444ca83332d44832e302f08e2bfd04bdd) |
| 杨晨昊 | 编写参考 Dockerfile，保存成功构建、镜像标识、`hello E3` 输出和退出码 | [4ddc1f9](https://github.com/laolvfan/devops/commit/4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3) |
| 杨晨昊 | 在个人 E3 汇总仓库整合王炜提供的 MDFixer 源码、报告、补丁和原始实验记录 | [ccab50a](https://github.com/killyagt/devops-e3-a11-b11/commit/ccab50ab76bc8fa64e19ba9339a0c644002f8f90) |
| 王炜 | 建立 MDFixer 缺失头文件依赖的源码基线，包含 `main.c`、`config.h`、Makefile 和样例说明，供固定报告引用 | [4fdc623](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f) |
| 王炜 | 整理实验仓库与固定 MD 报告；准备 Target、Macro、Hybrid、Implicit 四种参考补丁；完成修复前旧值复现，保存命令、环境、文件状态、输出和实验脚本 | [2c2e3d7](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/2c2e3d7067522569a8b6bb534cf5e12fabcec5d0) |
| 王炜 | 将复现实验脚本的 Python 入口改为 `python3`，去除对主仓库虚拟环境路径的依赖 | [d11188a](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/d11188acb4d8dd17af0b66c7bd0c5b8786385165) |
| 王炜 | 补充四种参考补丁通过 `git apply --check` 的检查说明 | [1efc438](https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit/commit/1efc4381cb1b5f5f8212c93cf082461eece50bb1) |
| 阳旅帆 | 核对并归档两条样例的输入版本和原始证据；编写验证脚本，完成四种补丁的应用、clean/增量行为验证及无效候选拒绝恢复实验；整理提交清单、重跑说明和贡献记录 | [c6f659d](https://github.com/laolvfan/devops/commit/c6f659da2fd8cdddb5343c0617a2bd1b0a5bf9b2)、[验证结果](evidence/mdfixer-validation-001/summary.json) |
| 阳旅帆 | 合并重复的核对说明，精简 E3 文档，保留实验步骤、证据入口及当时的缺口记录 | [9948e55](https://github.com/laolvfan/devops/commit/9948e55ca5d384cae7ce0736f9cd96f8a84a359b) |
| 阳旅帆 | 编写 DRAFT 复跑脚本，解决本机实验联网问题；从固定提交重跑失败构建、参考构建和功能验证，补齐环境、实际命令、源码状态及镜像信息；核对并补全三位成员的贡献证据 | [验证脚本](../../scripts/e3/verify_draft.py)、[实际结果](evidence/draft-validation-005/summary.json) |
