# DRAFT 实验说明

## 样例与固定输入

Tiny Greeting 在源码目录执行 `make` 生成 `hello`，再执行 `./hello`；两条命令均应退出 0，程序输出 `hello E3`。`Dockerfile.broken` 缺少构建工具；人工参考 `Dockerfile.reference` 增加 `gcc`、`make`、`libc6-dev` 的安装，再构建同一程序。

本次用 `git show` 从 [4ddc1f9](https://github.com/laolvfan/devops/commit/4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3) 导出 `E3实验包/fixtures/draft` 下的四个输入文件，在独立临时目录构建。[输入快照](evidence/draft-validation-005/source/) 与该提交逐字节一致，构建前后摘要一致；主仓库的文档修改不参与构建。

## 实际结果

完整结果见 [summary.json](evidence/draft-validation-005/summary.json)。[commands.json](evidence/draft-validation-005/commands.json) 保存实际命令、工作目录、预期和退出码；各命令的标准输出与错误输出见 [logs](evidence/draft-validation-005/logs/)。

| 场景 | 预期 | 实际记录 |
|---|---|---|
| 缺工具链 | 构建非零退出，错误可定位到 make | [构建输出](evidence/draft-validation-005/logs/broken-build.stdout.log) 含 `make: not found`；[错误输出](evidence/draft-validation-005/logs/broken-build.stderr.log) 定位 `RUN make`，整体退出 127 |
| 参考构建 | 安装工具链后构建成功 | [构建日志](evidence/draft-validation-005/logs/reference-build.stdout.log)，退出 0 |
| 功能验证 | 输出 `hello E3`，退出 0 | 按镜像 ID 执行 `docker run --rm --network none`，[输出](evidence/draft-validation-005/logs/reference-run.stdout.log) 和退出码均符合预期 |

## 环境与镜像

| 项目 | 本次实际值 | 证据 |
|---|---|---|
| 宿主 | Ubuntu 20.04.6 LTS，x86_64，WSL2 内核 `6.6.87.2-microsoft-standard-WSL2` | [系统](evidence/draft-validation-005/logs/host-os.stdout.log)、[内核与架构](evidence/draft-validation-005/logs/host-kernel-architecture.stdout.log) |
| Docker | 客户端与 Engine 均为 26.1.3，使用 legacy builder | [版本](evidence/draft-validation-005/logs/docker-version.stdout.log)、[daemon 环境](evidence/draft-validation-005/logs/docker-daemon.stdout.log) |
| 容器 | Debian 13（trixie），x86_64 | [系统](evidence/draft-validation-005/logs/container-os.stdout.log)、[架构](evidence/draft-validation-005/logs/container-architecture.stdout.log) |
| 构建工具 | GCC 14.2.0，GNU Make 4.4.1，libc6-dev `2.41-12+deb13u4` | [编译器](evidence/draft-validation-005/logs/container-compiler.stdout.log)、[Make](evidence/draft-validation-005/logs/container-make.stdout.log)、[包版本](evidence/draft-validation-005/logs/container-packages.stdout.log) |
| 基础镜像 | `python:3.13-slim`，两次构建使用同一个本地镜像；完整 ID 与仓库摘要已记录 | [构建前 inspect](evidence/draft-validation-005/logs/base-inspect.stdout.log)、[构建后 inspect](evidence/draft-validation-005/logs/base-inspect-after.stdout.log) |
| 参考镜像 | 通过 `docker build --iidfile` 采集 ID，并与 `docker image inspect` 的 `.Id` 核对一致 | [image_id.txt](evidence/draft-validation-005/image_id.txt)、[inspect](evidence/draft-validation-005/logs/reference-inspect.stdout.log) |

本机构建使用 `--network host` 与临时代理访问软件源，功能验证使用 `--network none`。临时代理在实验结束后关闭；配置与重试经过见 [执行上下文](evidence/draft-validation-005/execution-context.json)。

## 重跑命令

需要 Python 3、Git、可用的 Docker daemon 及镜像/软件源访问能力。在主仓库根目录执行：

```bash
mkdir -p work
e3_run=$(mktemp -d "$PWD/work/e3-draft-XXXXXX")
python3 scripts/e3/verify_draft.py --output "$e3_run/results"
```

[脚本](../../scripts/e3/verify_draft.py) 会导出固定输入并完成上表验证，通过时退出 0、`summary.json` 的 `passed` 为 `true`。输出目录须尚不存在；脚本保存输入、环境、命令、日志、镜像信息、自身快照和 `sha256.json`。网络需要代理时可指定 `--build-network host --build-proxy http://127.0.0.1:18443`，该地址须有可用代理监听。基础镜像标签和软件源可变，重跑以新采集的版本为准。

## 历史记录

同学原始材料见 [draft-original](evidence/draft-original/)，包含 `make: not found`、参考成功及早期排查日志。本次完整运行前还保留了 [001](evidence/draft-validation-001/summary.json) 的代理连接失败、[002](evidence/draft-validation-002/summary.json) 的软件源连接停滞及主动停止记录，以及 [003](evidence/draft-validation-003/summary.json)、[004](evidence/draft-validation-004/summary.json) 的软件下载失败记录；最终验收使用上面的 005 运行。
