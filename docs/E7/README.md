# B11 E7：测试、CI 门禁与提交证据

已完成服务器上的六项独立判定测试、26 项服务测试及五个真实场景门禁，正常 GitHub CI 全部通过。默认候选使用 P1 实际验证的 `work/candidate/error-mirror/Dockerfile`。workflow 已启用 PR、main 和手动触发；失败拦截与同一 PR 的修复恢复见 [实验报告](report.md)。

最终提交产物统一放在服务器 `/root/submit`，E7 建议使用 `/root/submit/E7/`，整理方式见 [提交归档说明](submission.md)。

## 已准备的文件

|文件|用途与来源|
|---|---|
|`services/draft/tests/test_team_extensions.py`|小组新增候选约束测试：拒绝新增最终阶段并直接 echo 的 Dockerfile|
|`tests/e7/test_gate_expectations.py`|小组新增六项判定测试：成功、预期故障、镜像错配、基础设施失败、构建超时与运行超时区分、失败后停止验证|
|`scripts/run_e7_b_gate.py`|从教师 B-draft 原样导入；运行服务测试和五个真实工作流场景|
|`.github/workflows/e7-quality-gate.yml`|PR/main/手动触发；交接检查、独立判定、扫描、构建、门禁和归档|
|`fixtures/ci-candidates/`|教师保存的 DeepSeek 候选及来源记录；属于回放输入|
|`work/candidate/error-mirror/Dockerfile`|P1 的错误驱动候选及记录过的换源调整；默认正式门禁输入，已由 main 跟踪|
|`ci/B-main-protection.json`|教师分支保护配置，启用前核对 App ID|
|`ci/rejection-demo/B/`|教师错误/正确 version 测试，留到合并门禁演示时使用|
|`docs/E7/evidence-index.csv`|正式运行的证据索引，未执行条目标记 PENDING|
|`docs/E7/handoff.json`|向 E5/E6 同学索取的输入和版本信息|
|`docs/E7/validation.md`|第一阶段实际检查、来源、范围和后续事项|
|`docs/E7/report.md`、`ci-evidence/`|正式实验报告、三阶段 CI 原始 artifact 与合并拒绝证据|

原始课程包：`DevOps_1020_Student_Cloud/labs/B-draft/`，分支保护及演示测试来自包内 `ci/`。本分支已合入 main 的基础 `autobuild.py` 和 CLI；E6 同学的后续核心修改与自动实验结果继续按提交版本交接。

## 五场景预期表

|case|输入或故障|工具状态 / 退出码|通过条件与证据|
|---|---|---|---|
|success|保存的有效候选|SUCCEEDED / 0|首轮 MISSING_MAKE，次轮 build=0；按次轮 image_id 运行；run=0，stdout=`hello E3\n`，output_matches=true|
|wrong-output|将预期文本改为 intentionally wrong output|FAILED / 1|次轮构建成功，程序仍输出 hello E3；output_matches=false|
|invalid-candidate|将 CMD 换为直接 echo hello E3|FAILED / 1|构建前拒绝；attempts 为空，无构建 project 副本|
|build-failed|在 RUN make 前插入 RUN exit 23|FAILED / 1|首轮缺 make；次轮 build=1，日志含 exit code: 23；无 verification|
|runtime-timeout|初始与候选 CMD 同时加入 sleep 10，运行预算 1 秒|TIMED_OUT / 1|次轮 build=0；记录 fault-injection.json；保存运行容器 ID，docker inspect 确认容器已移除|

单元测试计为另一项检查，完整 gate 共六项，全部 passed=true 时整体退出码为 0。单个故障场景工具退出 1 且符合预期时，该场景通过。单元测试中的人工 JSON 仅用于检查判定函数，正式场景的 JSON 由真实执行产生。

## 第一阶段的本地检查

在仓库根目录执行：

```bash
python3 -m unittest discover -s tests/e7 -v
```

自主候选测试依赖 E6 实现。当前 main 已提供基础实现，在服务目录执行：

```bash
cd services/draft
python3 -m pytest tests/test_team_extensions.py -q
```

准备期间可用显式配置的教师参考包验证兼容性，具体路径与结果写入 validation.md；正式测试从 E6 的 `draft.autobuild` 导入，不使用自动回退，也不跳过缺少的实现。

## E5/E6 交接清单

E5 已交接：`work/candidate/error-mirror/Dockerfile`、`work/candidate/provenance.json`、`docs/E5/report.md` 及 `work/e5-02/` 的成功构建和运行日志。来源记录包含两类 ChatGPT 提示、原始回复及人工换源调整；候选保留 `RUN make` 与 `CMD ["./hello"]`，runner 使用它们注入故障。

E6 同学提供：可运行提交 SHA、`draft.auto-build` CLI、服务镜像构建方式、两轮 `result.json`、校验结果，以及需要保留的配置。请确认 `prepare_candidate(broken, candidate)` 拒绝多阶段候选；镜像中的 pytest 会收集新增测试。

此前 E4 的 DaoCloud 初始镜像名与教师候选存在差异。main 已将初始样例首行改为 `FROM python:3.13-slim`，配套指令和 P1 候选均符合教学流程。E6 会根据候选摘要生成固定版本的首轮构建文件。后续若变更镜像命名，需成套交接 fixture、候选和校验实现。

将交接信息填写到 handoff.json，合并 E6 后先运行受影响测试，再完成一次正式集成门禁。核心实现缺陷通过用例、预期和日志交给 E6 同学处理。

## Linux 上正式运行

使用独立目录及带本人学号的镜像标签。以下命令在同步本分支后的 Ubuntu 仓库根目录执行，替换学号；输出目录每次使用新名称。

```bash
docker build --progress=plain -f services/draft/Dockerfile -t e7-draft:学号 .
python3 scripts/run_e7_b_gate.py \
  --image e7-draft:学号 \
  --candidate work/candidate/error-mirror/Dockerfile \
  --out work/学号/e7-01 --build-timeout 600
```

上述与 CI 均使用 P1 最终候选，来源和人工调整见 `work/candidate/provenance.json`。调试某项时可使用 `--case success` 等参数，正式验收省略 `--case` 以运行全部场景。选择教师回放时显式改为 `fixtures/ci-candidates/DeepSeek-E5.Dockerfile` 并相应记录来源。

构建服务使用 bridge 网络访问注册表，生成程序的验证容器使用 `--network none`。共享服务器上重型 gate 错峰执行。

## CI 与合并门禁流程

1. 确认 main 已同步的基础模块和 E6 后续版本可用，检查 CLI、fixture/候选组合和镜像内测试。CI 前置检查会调用真实 `prepare_candidate`，提前报告交接不兼容。
2. 将 workflow 的 `CANDIDATE_PATH` 与 `CANDIDATE_SOURCE` 设置为所选候选及其真实来源；继续使用回放时保留已有取值。
3. workflow 已使用以下自动触发，并保留 `workflow_dispatch:`：

```yaml
  pull_request:
  push:
    branches: [main]
```

4. 首次正常 CI 必须运行服务测试和全部五个场景；读取并下载 artifact。
5. 核对实际 check-runs 的 App ID，再配置 main：`e7-b-quality-gate`、strict=true、enforce_admins=true，审批人数为 0。
6. 创建单独演示 PR，将 `ci/rejection-demo/B/test_ci_reject_demo.py.example` 复制为 `services/draft/tests/test_ci_reject_demo.py`，取得错误 version 预期导致的失败记录。模板采用 `.example` 后缀，正常测试收集时不会执行故意失败用例。
7. 实际尝试普通合并，保存拒绝日志、退出码、OPEN/BLOCKED 和保护配置。
8. 在同一 PR 中将 `fixed/test_ci_reject_demo.py.example` 复制到同一个服务测试路径并提交；确认最新检查通过，下载恢复 artifact，再合并并保存最终记录。

CI 以只读 contents 权限检出触发版本；第三方 action 固定到官方 v4 标签核对过的提交。无论成功或失败都归档 work/ci，保留 14 天。触发 SHA、PR head SHA、实际检出 SHA 分别记录，PR 的合并测试提交与分支 head 可不同。

正常功能 PR #2 已合并；main 保护由所有者配置。PR #3 保存错误测试、真实拒绝与修复恢复流程。完整 E7 验收以 report.md、evidence-index.csv 和 ci-evidence 的实际记录为准；最终合并记录与服务器原始运行目录一并放入 `/root/submit/E7/`。
