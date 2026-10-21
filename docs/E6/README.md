# B11 E6 DRAFT 自动构建与验证

轨道：B / DRAFT。原始运行目录归属 `241880581`；最终 E6/E7 整合验证在 `241880100` 的独立目录执行，分别保留证据，不将历史日志标记为新版结果。

## 实现与修改

参考实现来自教师 B-draft 实验包。成员分支 `feat/e6-autobuild` 的提交 `1254f408761b0ee3a4ab4eef7b89b4c0f3956f7a` 及其父提交提供以下补充，已在整合分支纳入：

- CLI 和结构化报告区分 `student-candidate` 与 `teaching-replay`，校验器检查来源标记与候选哈希一致。
- 保存候选原始字节并按原始字节计算 SHA256，避免 Windows CRLF 换行导致输入与证据不一致。
- 接受初始 Dockerfile 已固定且未改变的基础镜像摘要，仍拒绝更换镜像或摘要的候选。
- 补充固定摘要、CRLF、CLI 和证据来源校验测试；整合时保留 E7 多阶段候选拒绝测试和全部故障门禁。

源码入口为 `scripts/lab_cloud.py`；`services/draft/draft/autobuild.py` 的 `auto_build` 依次完成两轮构建、镜像检查和运行验证。`prepare_candidate` 检查候选约束；`classify_failure` 判定首轮是否真正缺少 make。`scripts/verify_e6_b_evidence.py` 从已保存的输入、日志与镜像信息独立检查结果一致性，不重新调用模型或执行构建。

## 输入与来源

使用 E5 的 `work/candidate/error-mirror/Dockerfile`，SHA256 为 `5d4f3abf8f5aeb7907bb89baa9f94341af0ba4b3415cde3db21b07bab03c9f96`。两类 ChatGPT 5.6 回复生成日期为 `10.20`；来源、原始回复及人工换源差异见 `work/candidate/`。本次不是教师候选回放，也没有在 E6 中再次调用模型。

样例仍为输出 `hello E3` 的 C 程序；输入副本及逐文件哈希随各次运行保存。第一轮故意不安装 make；第二轮使用保存的候选。最终程序关闭网络，按第二轮构建所得镜像 ID 运行。

## 原始运行

原始源码提交为 `6600fe78347af499417ab7eab69832c568135a88`，相对证据目录为 `work/e6-original-241880581/`。其镜像为 `course1020-draft:local`，运行环境为 Ubuntu 22.04.5 LTS、x86_64、2 CPU、约 3.5 GiB 内存；Docker 29.1.3、Compose 2.40.3、Buildx 0.30.1、Python 3.10.12、GNU Make 4.3、Git 2.34.1。

| 检查项 | 原始运行结果 |
|---|---|
| 第一轮 | 构建退出 1，日志包含 make: not found，分类 MISSING_MAKE |
| 第二轮 | 构建退出 0 |
| 镜像 ID | `sha256:baf90131d47a9140eb2cf363bb3fbf2828bb7e922aa6e31501336dedc284c614` |
| 运行 | 同一镜像 ID，退出 0，输出 `hello E3`，标准错误为空 |
| 证据一致性 | 已核对输入与候选哈希、原始日志、镜像 ID、输出和退出码 |

原始记录早于成员分支的来源标记和 CRLF 修复，保留原文；不将该记录作为这些后续修改的运行证据。

## 最终整合验证

精确运行版本、服务镜像 ID、E6 校验结果及 E7 门禁结果见本目录的 `final-validation.json`。合并前本地 40 项相关测试通过，包括服务测试、E6 证据校验测试和 E7 独立判定测试；命令与范围见 `integration-check.json`。

在具有 Docker 的 Linux 主机仓库根目录执行，重跑时使用新的输出目录：

```bash
python3 scripts/lab_cloud.py build --image b11-draft:final-e67 --out work/final-e67-build --build-timeout 600
python3 scripts/lab_cloud.py e6 --image b11-draft:final-e67 --candidate work/candidate/error-mirror/Dockerfile --out work/final-e6 --build-timeout 600
python3 scripts/verify_e6_b_evidence.py --run-dir work/final-e6/evidence
python3 scripts/lab_cloud.py gate --image b11-draft:final-e67 --candidate work/candidate/error-mirror/Dockerfile --out work/final-e7 --build-timeout 600
```

## 证据索引

| 内容 | 相对路径 |
|---|---|
| 最终源码、环境和镜像信息 | `docs/E6/final-validation.json`、`work/final-e67-build/` |
| 最终 E6 调用、报告和日志 | `work/final-e6/invocation.json`、`work/final-e6/runner/`、`work/final-e6/evidence/` |
| 最终 E6 校验输出 | `docs/E6/final-evidence-check.json` |
| E7 集成回归 | `work/final-e7/gate/gate-result.json`、`work/final-e7/gate/results.csv` |
| 自主测试 | `services/draft/tests/test_autobuild.py`、`test_cli.py`、`test_workflow_failures.py`；`scripts/tests/test_verify_e6_b_evidence.py` |

失败时保留日志并区分网络故障和目标缺陷；构建失败不执行程序验证。本实验自动化的是教学样例的候选构建与验证，不包含完整论文候选搜索或真实项目基准评测。代码仓库为 <https://github.com/laolvfan/devops>，最终提交 SHA 由提交包的 `SUBMISSION.json` 记录。
