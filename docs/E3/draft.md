# DRAFT 样例与重跑说明

## 样例目标

使用课程人工样例 Tiny Greeting，验证给定环境能否完成构建并正确运行。E3 中的 Dockerfile 是手工准备的失败候选和参考答案；后续 DRAFT 服务需要自动完成候选生成与迭代。

输入快照位于 [fixtures/draft](evidence/draft-original/fixtures/draft/)，包含 `main.c`、`Makefile`、原 README 和两份 Dockerfile。原 README 不完整，本说明补充重跑步骤，原归档保持不变。

| 项目 | 约定 |
|---|---|
| 原生构建 | 在样例源码目录执行 `make`，退出码 0，生成 `hello` |
| 功能验证 | 同目录执行 `./hello`，标准输出 `hello E3`，退出码 0 |
| Docker 构建上下文 | 同时含 `main.c`、`Makefile` 和 Dockerfile 的样例目录 |
| 失败候选 | `Dockerfile.broken`：在缺少工具链的基础镜像上执行 `make` |
| 参考方案 | `Dockerfile.reference`：安装 `gcc`、`make`、`libc6-dev` 后执行相同构建 |
| 判断成功 | Docker 构建成功，随后运行生成的镜像，输出和退出码同时符合功能约定 |

参考 Dockerfile 在 `COPY` 和 `RUN make` 之前增加：

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc make libc6-dev && \
    rm -rf /var/lib/apt/lists/*
```

`make` 负责执行 Makefile；`gcc` 和 `libc6-dev` 提供编译这个 C 程序所需的工具与开发文件。

## 固定材料与原始结果

仓库为 `https://github.com/laolvfan/devops.git`，原目录为 `E3实验包/fixtures/draft/`。

| 材料 | 提交 |
|---|---|
| 初始源码与输入 | `c70c1d5f827de0e6a519cd7fb0a4aaed261d54ab` |
| 失败 Dockerfile、文件名大小写修正与失败记录 | `42b1b7d444ca83332d44832e302f08e2bfd04bdd` |
| 参考 Dockerfile 与成功记录；本次归档版本 | `4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3` |

以上为素材提交，不能自动证明历史运行时检出的是该 SHA 或工作区干净。

- [目标失败](evidence/draft-original/evidence/draft-broken-004/build.log)：`RUN make` 中出现 `make: not found`，该步骤退出码 127；保存的整体构建退出码为 1。
- [参考成功](evidence/draft-original/evidence/draft-reference-002/build.log)：构建退出码 0；[容器运行](evidence/draft-original/evidence/draft-reference-002/run.log) 输出 `hello E3`，运行退出码 0。
- 两份日志的基础镜像均为 `python:3.13-slim@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b`。
- 成功日志记录安装的包包括 `gcc-14` 版本 `14.2.0-19`、`make` 版本 `4.4.1-2` 和 `libc6-dev` 版本 `2.41-12+deb13u4`。这些是容器安装日志中的包版本，未补造 `cc --version` 等命令输出。
- [image_id.txt](evidence/draft-original/evidence/draft-reference-002/image_id.txt) 保存 `sha256:8bd610f3943a2920e6d0c619fc2465343628a71a1be1ba0d6859a06043d440be`，与日志中的 manifest list 摘要相同。原记录未保留采集命令或 inspect 输出，提交材料按这一已知范围说明标识类型。

## 重新执行并留证

以下是根据归档输入整理的重跑方法，供后续需要时执行，尚未作为新一轮 Docker 实验运行。本次按现有结果和已知缺口整理提交材料。重跑需要可用的 Docker daemon；参考镜像构建还需要访问镜像和软件包源。

在主仓库根目录启动 Bash，先创建独立目录并复制固定输入：

```bash
mkdir -p work
e3_run=$(mktemp -d "$PWD/work/e3-draft-XXXXXX")
mkdir "$e3_run/input"
cp docs/E3/evidence/draft-original/fixtures/draft/{main.c,Makefile,Dockerfile.broken,Dockerfile.reference} "$e3_run/input/"
cp docs/E3/evidence/draft-original/provenance.json "$e3_run/input-provenance.json"
git rev-parse HEAD > "$e3_run/materials-commit.txt"
git status --short > "$e3_run/materials-worktree.txt"
sha256sum "$e3_run"/input/* > "$e3_run/input-sha256.txt"
e3_tag="e3-draft-reference:$(basename "$e3_run")"
printf '%s\n' "$e3_run"
```

接着定义记录函数，让每条实验命令都保存实际输出和退出码。函数自身返回成功，以便保存预期失败；后续按日志和退出码判定结果。

```bash
e3_record() {
    local label=$1
    shift
    printf '%s: ' "$label" >> "$e3_run/commands.txt"
    printf '%q ' "$@" >> "$e3_run/commands.txt"
    printf '\n' >> "$e3_run/commands.txt"
    local rc=0
    "$@" > "$e3_run/$label.log" 2>&1 || rc=$?
    printf '%s\n' "$rc" > "$e3_run/$label.exit_code.txt"
}

e3_record host-os cat /etc/os-release
e3_record host-architecture uname -m
e3_record docker-version docker version
e3_record docker-context docker context show
e3_record broken-build docker build --no-cache \
    -f "$e3_run/input/Dockerfile.broken" "$e3_run/input"
```

检查 `broken-build.exit_code.txt` 为非零，且 `broken-build.log` 含 `make: not found`。网络错误、权限错误或 COPY 失败需要另行排查，不能计作目标失败。

然后构建参考镜像。下面的代码在构建成功后才执行镜像检查和功能验证：

```bash
e3_record reference-build docker build --no-cache \
    -f "$e3_run/input/Dockerfile.reference" -t "$e3_tag" "$e3_run/input"
if [ "$(cat "$e3_run/reference-build.exit_code.txt")" = 0 ]; then
    e3_record image-inspect docker image inspect "$e3_tag"
    e3_record image-id docker image inspect --format '{{.Id}}' "$e3_tag"
    e3_record container-os docker run --rm --entrypoint cat "$e3_tag" /etc/os-release
    e3_record container-architecture docker run --rm --entrypoint uname "$e3_tag" -m
    e3_record compiler-version docker run --rm --entrypoint cc "$e3_tag" --version
    e3_record make-version docker run --rm --entrypoint make "$e3_tag" --version
    e3_record reference-run docker run --rm "$e3_tag"
fi
```

检查参考构建退出码为 0，`reference-run.log` 输出 `hello E3`，运行退出码为 0；环境采集命令也应成功。发生任何失败时保留该目录，重试时创建新目录。

原 Dockerfile 使用可变的 `python:3.13-slim` 标签及 apt 软件源，因此新的运行应保留实际解析到的基础镜像、inspect 结果和工具版本；不能据此宣称与历史环境完全相同。现有记录的缺口见 [提交清单核对](review.md#已知缺口)。
