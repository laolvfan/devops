# B11 E5 DRAFT 实验结果

学号：241880100；轨道：B / DRAFT。实验已完成手工失败复现、两类提示比较、候选构建和运行验证，最终输出 `hello E3`，退出码为 `0`。

## 环境与输入

实验目录为服务器 `/root/241880100/devops`，仓库为 <https://github.com/laolvfan/devops>。

| 项目 | 实际值 |
|---|---|
| 系统与资源 | Ubuntu 22.04.5 LTS，x86_64，2 CPU，3.54 GiB 内存 |
| 工具 | Docker 29.1.3；Compose 2.40.3；Buildx 0.30.1；Python 3.10.12；GNU Make 4.3；Git 2.34.1 |
| 运行分支与基线 | `E5`；基线 `255f9d06da6d7ba05e4772aeabe6f5002b68c4fc` |
| 代码状态 | 运行时 E5 改动尚未提交；上述基线不是包含本次改动的最终提交 SHA |
| DRAFT 服务镜像 ID | `sha256:65268fea1c0f4216e2bd0055bb22df80895277185d85a6dbea304cfe04cccd50` |

参考实现来自教师学生实验包 `labs/B-draft/`，保留本组 E4 环境修正。服务镜像构建成功，服务测试为 `25 passed`（教师包 24 项，加本组 E4 回归测试 1 项）。

本次目标项目是教学 C 程序，不是 DRAFT 服务本身：`main.c` 输出 `hello E3`，Makefile 通过 `cc main.c -o hello` 编译。实际输入副本保存在 `work/e5-02/project/`；失败构建使用的 Dockerfile 为 `work/e5-02/iter-01/Dockerfile`，固定 Python 基础镜像摘要为 `sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f`。

## 失败复现与候选比较

执行 `python3 scripts/lab_cloud.py e5 --out work/e5-02 --build-timeout 600`，构建在 `RUN make` 处失败，日志为 `/bin/sh: 1: make: not found`。Docker 构建退出码为 `1`，该构建步骤内部退出码为 `127`。脚本正确采集失败并生成提示，因此脚本自身退出码为 `0`。

两份回复的模型来源均为 ChatGPT 5.6（按使用者提供的界面名称记录），未使用包内候选回放。

| 类型 | 提示与原始回复（仓库相对路径） | 候选 |
|---|---|---|
| 错误驱动 | `work/e5-02/iter-01/prompt-error-driven.txt`；`work/candidate/response-error.txt` | `work/candidate/error/Dockerfile` |
| 上下文驱动 | `work/e5-02/iter-01/prompt-context-driven.txt`；`work/candidate/response-context.txt` | `work/candidate/context/Dockerfile` |

错误驱动提示提供 Dockerfile 和错误日志，上下文驱动提示另提供 README。两份候选均安装 `gcc`、`make`、`libc6-dev`，仅包名顺序不同，修复方案相同：补齐 C 编译器、GNU Make 和 C 库开发文件，同时保留基础镜像、工作目录、源码复制、`RUN make` 和启动命令。

两者修复依赖相同，因此选择错误驱动候选继续验证；未另行构建上下文驱动候选。此前的综合候选 `work/candidate/candidate-01/` 保留作过程记录，不计作这两次回复，也未作为本次最终验证输入。

## 人工调整与验证结果

原始候选构建停在 Debian 索引下载阶段，随后人工中断，记录退出码为 `255`。在临时容器中验证阿里云 HTTPS 软件源可用后，另存换源版本 `work/candidate/error-mirror/Dockerfile`：替换 Debian 软件源，并为索引更新增加超时和一次重试，原始回复和候选保持不变。调整差异见 `work/candidate/error-mirror/adjustment.patch`，来源与选择记录见 `work/candidate/provenance.json`。

手工构建命令：

```bash
docker build --progress=plain \
  -f work/candidate/error-mirror/Dockerfile \
  -t b11-e5-repaired:241880100 work/e5-02/project
```

构建日志确认执行 `cc main.c -o hello`，退出码为 `0`。最终候选文件 SHA256 为 `5d4f3abf8f5aeb7907bb89baa9f94341af0ba4b3415cde3db21b07bab03c9f96`。

通过 `docker image inspect` 取得本次构建镜像的 ID，再执行 `docker run --rm --network none "$image_id"`，不覆盖镜像的默认启动命令。

| 检查项 | 实际结果 |
|---|---|
| 构建与运行使用的镜像 ID | `sha256:df4844a6863ebc8637114a5c45a513bf513e23e031feca1883cfebfdbdd3a8b1` |
| 标准输出 | `hello E3`，带结尾换行 |
| 标准错误 | 空 |
| 运行退出码 | `0` |

## 证据索引与实验范围

以下路径均相对于仓库根目录；`work/` 保存实际运行证据。

| 内容 | 路径 |
|---|---|
| 服务构建与测试 | `work/e5-service-01/build/`、`work/e5-service-01/unit-tests/` |
| 初始失败的命令、日志、退出码 | `work/e5-02/iter-01/build/`、`work/e5-02/iter-01/result-retry.json` |
| 错误定位 | `work/e5-02/iter-01/error-localization.json` |
| 候选构建中断 | `work/e5-02/candidate-build.log`、`work/e5-02/candidate-build-exit-code.txt` |
| 软件源验证 | `work/e5-apt-recovery-01/` |
| 最终构建日志与退出码 | `work/e5-02/candidate-build-retry-01.log`、`work/e5-02/candidate-build-retry-01-exit-code.txt` |
| 镜像身份 | `work/e5-02/candidate-image-id.txt`、`work/e5-02/candidate-image-inspect.json` |
| 程序输出与退出码 | `work/e5-02/candidate-run.stdout.log`、`work/e5-02/candidate-run.stderr.log`、`work/e5-02/candidate-run-exit-code.txt` |
| 文件完整性校验 | `work/e5-02/SHA256SUMS` |

更早的 `work/e5-01/` 因 Docker Hub 连接超时，未到达 `RUN make`，不计为缺少 make 的有效复现。经镜像站预取相同摘要的基础镜像后，才取得 `work/e5-02/` 的有效失败；恢复记录见 `work/e5-network-01/`。

本次以教学样例对应“失败日志 → 提示 → 候选 → 构建与运行验证”流程，由人工取得和选择候选、执行验证。没有实现论文的完整候选选择算法，也不能据此推断两类提示在其他项目上的效果。E6 自动化与 E7 故障测试、CI 门禁不属于本报告已完成的验证范围。
