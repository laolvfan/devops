# E7 准备与交接检查记录

## E5 已完成后的 main 同步

- 已同步 main 合并提交 `6600fe78347af499417ab7eab69832c568135a88`；E5 产物提交为 `a28e3a0ffefdbf0900c606d01b97fc4c18803a90`。
- P1 最终候选为 `work/candidate/error-mirror/Dockerfile`，来源为 ChatGPT 错误驱动回复加记录过的阿里云换源调整。候选哈希与 `work/candidate/provenance.json` 一致，保存的运行日志输出 `hello E3`。本次读取并核对 P1 原始结果，未重跑 E5 构建。
- main 已接入基础 `autobuild.py`、CLI、服务测试和修正后的初始样例。原 E4 镜像命名差异已解决，真实 `prepare_candidate` 接受当前初始样例与 P1 最终候选。
- 使用仓库实际实现运行 `services/draft/tests` 与 `tests/e7`：**32 passed**，其中服务测试 26 项（上游 25 项加 E7 自主测试 1 项），独立判定测试 6 项。原先仅对教师参考验证的扩展测试现已在小组实际代码上通过。
- workflow 和 handoff.json 均切换为 P1 最终候选，并保留手动触发。YAML/JSON、CLI 解析、候选兼容性与 `/root/submit` 路径记录检查通过。
- 源码与 Git 历史扫描通过，覆盖 634 个跟踪文件。本次合并的 P1 原始日志保留原始字节和已有哈希，空白检查限定为 E7 自己的改动；shell 内容未变，复用此前语法检查。本次采用自查及实际接口测试，未另开独立审查。
- 对应输出保存在 `main-sync-evidence/`。真实 Linux/Docker 五场景、E6 自动运行验收与 GitHub CI 继续按版本推进。
- 服务器最终提交根目录为 `/root/submit`，E7 产物建议归档至 `/root/submit/E7`，详见 submission.md；尚未连接服务器或执行上传。

以下记录保留初始准备提交 `a2afae8` 的检查背景；E6 是否存在及候选兼容性的当前状态以上述 main 同步结果为准。

## 输入与范围

- 仓库基线：`b9dc5ff1c5d233433ced0be257d50ef284795a18`。
- 本地目录：`D:\aaaWW\DevOps\devops-e7`；分支：`feat/e7-quality-gate`。
- 第一阶段交付仅新增 E7 测试、runner、候选回放、CI/保护配置、演示模板和文档；E4 核心实现及镜像配置保持基线内容。
- 环境：Windows，仓库独立虚拟环境，Python 3.13、pytest 8.4.2；PyYAML 6.0.3 用于读取 workflow，Git Bash 用于 shell 语法检查。
- 因仓库 `paper/` 含 Windows 不支持的 `:Zone.Identifier` 文件名，本地稀疏检出实验所需目录；这些文件仍保留在 Git 历史和索引中。

## 已执行

|检查|结果|目的|
|---|---|---|
|现有 `services/draft/tests`，新增文件前运行|4 项通过|确认 E4 服务基线正常|
|`python -m unittest discover -s tests/e7 -v`|6 项通过|验证门禁判断能接受正确场景并拒绝镜像错配、基础设施错误和构建超时冒充运行超时|
|自主扩展 `test_multistage_candidate_is_rejected`|教师参考实现上 1 项通过|核对候选约束测试兼容性；正式 E6 结果待交接|
|新增 Python 源码 AST 解析|通过|检查 runner 和新测试语法|
|workflow YAML、JSON、CSV 结构和关键配置|通过|检查只读权限、手动触发、归档条件、保留期及证据表格式|
|workflow 的 bash run 脚本 `bash -n`|通过|检查 shell 语法；未执行 Docker 或 CI|
|回放候选 SHA256|与来源记录一致|确认候选复制完整性|
|根目录历史测试 `python -m pytest tests --import-mode=importlib -q`|3 个文件收集失败，退出码 2|检查仓库级现状，识别既有路径问题|
|工作区与 Git 历史密钥扫描|通过，归档证据后扫描 540 个跟踪文件及历史|检查本阶段交付和基线的密钥泄露风险|

候选 SHA256 为 `ede21b0fab394071641526e2fccefc41565efb00de6fb54d9d5b906aebeb535d`。

实际输出保存在 `preparation-evidence/`，归档副本统一为 LF 换行；`summary.json` 区分 E4 基线、参考兼容性、人工输入的判定测试与待执行的真实实验。Windows 下使用 `python -X utf8 scripts/secret_scan.py . --history`；默认 GBK 解码曾使历史读取失败，改用 UTF-8 模式后扫描通过，未修改扫描器源码。首次扫描 533 个文件，加入七个证据文件后进行最终扫描，覆盖 540 个文件。

自主扩展测试的兼容性命令为：

```powershell
.\.venv\Scripts\python.exe -m pytest -c services/draft/pytest.ini `
  -o pythonpath=D:/aaaWW/DevOps/devops-e7/work/e7-prep/reference-service `
  services/draft/tests/test_team_extensions.py -q --import-mode=importlib
```

其中 `work/e7-prep/reference-service/draft/` 是从教师包复制到忽略目录的参考模块，仅用于准备期验证。交付代码中没有替换 E6 核心、自动回退或跳过缺少的 `autobuild`。该测试覆盖已有约束，参考实现直接通过，未为制造红灯修改生产代码。

## 初始准备阶段的待验证项（a2afae8 时点）

- 根目录 `tests/test_examples.py`、`tests/test_response_formats.py`、`tests/test_task_schema.py` 读取根目录 `schemas/task.schema.json`，而当前文件位于 `contract/schemas/task.schema.json`。这是仓库基线的目录迁移遗留问题，失败日志为 preparation-evidence/existing-contract-tests.log。本次未修改历史契约测试；仓库完整测试目前尚未通过。
- E6 的 autobuild.py 与 CLI 尚未接入。正式服务测试、镜像构建、五场景 Docker gate 均在交接后执行。
- 当前 E4 初始 Dockerfile 使用 DaoCloud 摘要镜像，与教师回放候选的 python:3.13-slim 基础镜像命名不一致。教师 `prepare_candidate` 对这一实际组合返回 `Candidate changed the original base image tag`。E6 同学需按 handoff.json 提供兼容的初始样例与候选；CI 在构建前调用该校验，提前发现交接错误。
- workflow 已编写，目前只支持手动触发；GitHub Actions 实际运行、main 保护、失败与恢复 PR 留待后续阶段。
- 无重复执行已覆盖且输入未变的基线检查。文档以人工内容核对；源码未计算哈希。候选哈希用于来源和复制完整性。
- 普通服务测试从 `services/draft` 执行；门禁判定测试单独从根目录 `tests/e7` 收集。演示模板采用 `.example` 后缀，防止故意失败用例被正常收集。

## 来源与 AI 协助

教师原样导入：五场景 runner、回放候选及 provenance、分支保护 JSON。错误/正确 version 演示模板仅调整为 `.example` 文件名。小组新增：多阶段候选约束测试、六项门禁判定测试、阶段化 CI 配置及 E7 文档。

Codex 按用户授权协助准备 E7，依据三份课件、B 轨道指南、CI 指南与验收清单实现并检查上述材料。实际模型回复生成、E5/E6 实验、真实 CI 与 PR 结果由对应执行阶段记录。

一次独立合并审查覆盖 CI 权限、shell、证据标记及 E6 接口，发现上述基础镜像交接差异，已补充准确要求和前置校验；其余无阻断发现。文档调整后复查 YAML/JSON 和受影响的 shell 语法，已通过的单元测试输入与实现未改变，复用原结果。
