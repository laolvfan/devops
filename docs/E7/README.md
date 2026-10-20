# B11 E7：第一阶段准备与交接

本阶段完成测试设计、自主扩展测试、五场景 runner、CI 配置和证据模板。正式运行需要 E6 的 `draft.auto-build` 实现。当前 workflow 仅支持手动触发；本地准备和真实 Docker/CI 结果分别记录。

## 已准备的文件

|文件|用途与来源|
|---|---|
|`services/draft/tests/test_team_extensions.py`|小组新增候选约束测试：拒绝新增最终阶段并直接 echo 的 Dockerfile|
|`tests/e7/test_gate_expectations.py`|小组新增六项判定测试：成功、预期故障、镜像错配、基础设施失败、构建超时与运行超时区分、失败后停止验证|
|`scripts/run_e7_b_gate.py`|从教师 B-draft 原样导入；运行服务测试和五个真实工作流场景|
|`.github/workflows/e7-quality-gate.yml`|基于教师流程适配：手动触发、E6 前置检查、独立判定测试、扫描、构建、门禁和归档|
|`fixtures/ci-candidates/`|教师保存的 DeepSeek 候选及来源记录；属于回放输入|
|`ci/B-main-protection.json`|教师分支保护配置，启用前核对 App ID|
|`ci/rejection-demo/B/`|教师错误/正确 version 测试，留到合并门禁演示时使用|
|`docs/E7/evidence-index.csv`|正式运行的证据索引，未执行条目标记 PENDING|
|`docs/E7/handoff.json`|向 E5/E6 同学索取的输入和版本信息|
|`docs/E7/validation.md`|第一阶段实际检查、来源、范围和后续事项|

原始课程包：`DevOps_1020_Student_Cloud/labs/B-draft/`，分支保护及演示测试来自包内 `ci/`。本分支保留现有 E4 核心代码，E6 的 `autobuild.py` 和 CLI 接入由 E6 同学负责。

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

自主候选测试依赖 E6 实现。E6 接入后，在服务目录执行：

```bash
cd services/draft
python3 -m pytest tests/test_team_extensions.py -q
```

准备期间可用显式配置的教师参考包验证兼容性，具体路径与结果写入 validation.md；正式测试从 E6 的 `draft.autobuild` 导入，不使用自动回退，也不跳过缺少的实现。

## E5/E6 交接清单

E5 同学提供：最终候选在仓库中的路径、模型来源记录、提交 SHA，以及成功构建并输出 hello E3 的日志。候选需保留 `RUN make` 与 `CMD ["./hello"]`，runner 使用它们注入故障。

E6 同学提供：可运行提交 SHA、`draft.auto-build` CLI、服务镜像构建方式、两轮 `result.json`、校验结果，以及需要保留的配置。请确认 `prepare_candidate(broken, candidate)` 拒绝多阶段候选；镜像中的 pytest 会收集新增测试。

当前样例存在一个明确的交接差异：仓库 `fixtures/draft/Dockerfile.broken` 首行是带摘要的 `FROM m.daocloud.io/docker.io/library/python@sha256:f82...`，教师候选则以 `FROM python:3.13-slim@sha256:707...` 开始。直接传给教师 `prepare_candidate` 会报 `Candidate changed the original base image tag`。

采用教师 E6 实现及本回放候选时，E6 同学需同步接入教学样例：初始文件的首行为 `FROM python:3.13-slim`，其余指令依次为 `WORKDIR /work`、`COPY main.c Makefile ./`、`RUN make`、`CMD ["./hello"]`；候选首行保持回放文件中的完整 70729b46... 摘要。E6 会根据候选摘要生成固定版本的首轮构建文件。若保留小组其他镜像命名方式，则由 E6 同学提供成套兼容的 fixture、候选和校验实现，再跑通 E6/E7。本阶段保留 E4 样例原内容。

将交接信息填写到 handoff.json，合并 E6 后先运行受影响测试，再完成一次正式集成门禁。核心实现缺陷通过用例、预期和日志交给 E6 同学处理。

## Linux 上正式运行

使用独立目录及带本人学号的镜像标签。以下命令在 E6 接入后的 Ubuntu 仓库根目录执行，替换学号和候选路径；输出目录每次使用新名称。

```bash
docker build --progress=plain -f services/draft/Dockerfile -t e7-draft:学号 .
python3 scripts/run_e7_b_gate.py \
  --image e7-draft:学号 \
  --candidate fixtures/ci-candidates/DeepSeek-E5.Dockerfile \
  --out work/学号/e7-01 --build-timeout 600
```

上述默认使用教师回放。E5 交付后，将 candidate 改成小组最终候选路径，并记录来源；本地与 CI 使用相同文件。调试某项时可使用 `--case success` 等参数，正式验收省略 `--case` 以运行全部场景。

构建服务使用 bridge 网络访问注册表，生成程序的验证容器使用 `--network none`。共享服务器上重型 gate 错峰执行。

## CI 启用顺序

1. 合并 E6，确认核心模块、CLI、兼容的 fixture/候选组合和镜像内测试可用。CI 前置检查会调用真实 `prepare_candidate`，提前报告交接不兼容。
2. 将 workflow 的 `CANDIDATE_PATH` 与 `CANDIDATE_SOURCE` 设置为所选候选及其真实来源；继续使用回放时保留已有取值。
3. 在 `on:` 下增加以下触发，保留 `workflow_dispatch:`：

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

此阶段仅准备保护配置与演示用例，未修改 GitHub 权限、创建 PR 或执行合并。完整 E7 验收以 evidence-index.csv 中的真实日志、运行链接和结果为准。
