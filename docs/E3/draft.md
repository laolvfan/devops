# DRAFT 实验说明

## 样例目标

输入为课程人工样例 [Tiny Greeting](evidence/draft-original/fixtures/draft/)，版本见 [来源表](README.md#来源与版本)。在源码目录执行 `make` 生成 `hello`，再执行 `./hello`；两条命令均应退出 0，程序输出 `hello E3`。

`Dockerfile.broken` 缺少构建工具；人工参考 `Dockerfile.reference` 增加 `gcc`、`make`、`libc6-dev` 的安装，再构建并运行同一程序。

## 实际结果与环境

| 场景 | 预期 | 原始记录 |
|---|---|---|
| 缺工具链 | 构建非零退出，错误可定位到 make | [失败日志](evidence/draft-original/evidence/draft-broken-004/build.log) 含 `make: not found`；步骤退出 127，[整体退出码](evidence/draft-original/evidence/draft-broken-004/exit_code.txt) 为 1 |
| 参考成功 | 构建、运行均退出 0，输出 `hello E3` | [构建日志](evidence/draft-original/evidence/draft-reference-002/build.log)、[构建退出码](evidence/draft-original/evidence/draft-reference-002/build_exit_code.txt)、[运行输出](evidence/draft-original/evidence/draft-reference-002/run.log)、[运行退出码](evidence/draft-original/evidence/draft-reference-002/run_exit_code.txt) 均符合预期 |

两次日志的基础镜像均为 `python:3.13-slim@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b`。成功日志记录容器安装了 `gcc-14 14.2.0-19`、`make 4.4.1-2`、`libc6-dev 2.41-12+deb13u4`；镜像标识见 [image_id.txt](evidence/draft-original/evidence/draft-reference-002/image_id.txt)。历史信息缺口统一见 [README](README.md#已知缺口)。

其余失败记录为联网超时（`draft-broken`）、COPY 文件名不匹配（`draft-broken-002`）和 Docker 权限问题（`draft-broken-003`、`draft-reference-001`）。

## 重新执行并留证

以下命令供后续重跑使用，本次未重新执行 Docker。需要 Bash、可用的 Docker daemon 及镜像/软件源访问能力。在主仓库根目录创建独立构建上下文：

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

记录每条命令、输出和退出码，再执行失败候选：

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

确认失败日志含 `make: not found` 且退出码非零，再构建参考镜像并验证：

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

按上表判定结果，重试使用新目录。基础镜像标签和 apt 软件源可变，新运行以本次采集的版本信息为准。
