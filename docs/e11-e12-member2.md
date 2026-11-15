# E11–E12 个人实验记录：成员二

## E11-B 固定样例联调

我在 `e11-e12-integration` 分支完成 E11-B 固定样例联调。运行请求为 `data/integration-sample/e11-b.json`，目标提交为 `0bbb12e66796dbd37adc8b39361dd7f85e61bb0d`。

DRAFT 首轮因缺少 `make` 得到 `MISSING_MAKE`。候选 Dockerfile 安装 `build-essential` 后，构建和程序验证成功。固定 MD 报告指出 `config.h`、`extra.h` 两条缺失依赖，以及 `unused.h` 一条冗余依赖。MDFixer 生成 Makefile 补丁，补丁验证接受；动态复验消除了 MD，仍保留 `unused.h` 的 RD。

任务状态为 `SUCCEEDED`，`job_id` 为 `job-37883ba208e048a699725a678fd7412b`，`trace_id` 为 `trace-fdcb985b09ca49579fe8480aae2576be`。运行证据保存在 `work/e11-b-241880581-05/`。

## 环境与候选调整

ECS 无法从 Docker Hub 拉取 Docker CLI 镜像，因此将 E11–E12 构建环境 Dockerfile 中的 Docker CLI 镜像地址改为 Daocloud，并保留原 digest。候选项目安装 `build-essential` 时，Debian 包索引下载多次停滞；在确认清华镜像可访问后，将实验样例候选 Dockerfile 的 Debian 软件源切换至清华镜像，原始候选备份为 `data/integration-sample/candidate.Dockerfile.before-mirror`。调整后 E11-B 成功。

## 自主测试

在 `labs/e11e12/test_contract.py` 新增两项测试：一项验证 macro 与 mixed 风格补丁位置，另一项明确断言过期报告错误码为 `STALE_REPORT`。E11–E12 契约测试共 12 项通过，退出码为 0。

## 尚待完成

跨组 E12 联调、GitHub Actions 远端 CI、代码提交与 PR 尚未完成。后续完成后补充对应记录和证据链接。
