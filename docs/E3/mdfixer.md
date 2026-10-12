# MDFixer 实验说明

## 固定输入与判断依据

[固定 MD 报告](evidence/mdfixer-original/oracle/mdfixer/md-report.json) 指出 `main.o` 缺少 `config.h`：`main.c` 包含该头文件并打印 `VALUE`，但原 Makefile 只声明 `main.o: main.c`。构建命令为 `make`，功能验证命令为 `./app`；仓库与源码 SHA 见 [来源表](README.md#来源与版本)。

报告标记为 `INSTRUCTOR_ORACLE`，属于人工预期答案；`producer_job_id` 是样例元数据。

## 参考补丁

四种人工参考补丁分别应用于同一 Target 基线的独立副本，得到四种修复后写法：

| 风格 | 参考文件 | 修复后的核心写法 |
|---|---|---|
| Target | [target.patch](evidence/mdfixer-validation-001/patches/target.patch) | `main.o: main.c config.h`，直接补依赖 |
| Macro | [macro.patch](evidence/mdfixer-validation-001/patches/macro.patch) | `DEPS = main.c config.h`，目标依赖 `$(DEPS)` |
| Hybrid | [hybrid.patch](evidence/mdfixer-validation-001/patches/hybrid.patch) | `HEADERS = config.h`，目标依赖 `main.c $(HEADERS)` |
| Implicit | [implicit.patch](evidence/mdfixer-validation-001/patches/implicit.patch) | `%.o: %.c` 配合 `-MMD -MP` 生成 `.d` 文件，再用 `-include` 读取 |

## 验证结果

[验证脚本](../../scripts/e3/verify_mdfixer.py) 对四种补丁均得到以下结果；完整记录见 [summary.json](evidence/mdfixer-validation-001/summary.json) 及各风格目录的 `commands.json`、步骤日志和文件快照。

| 操作 | 预期 | 实际 |
|---|---|---|
| `VALUE=1`，`make` 后运行 | 输出 1 | 输出 1，构建和运行退出码 0 |
| 改为 2，确认头文件比 `main.o` 新，直接 `make` | 漏重建，仍输出 1 | 输出 1，目标修改时间不变 |
| `git apply --check` 后应用补丁，clean 重建 | 补丁可应用，输出 2 | 各命令退出码 0，输出 2 |
| 再改为 3，不 clean，直接 `make` | 自动重建，输出 3 | 目标更新时间增加，输出 3 |

Implicit 生成的 [main.d](evidence/mdfixer-validation-001/implicit/main.d) 包含 `main.o` 和 `config.h`。最后一次不 clean 的重建是依赖修复有效的关键判据。

四个副本还分别执行了拒绝与恢复实验：在原 Makefile 的 `all` 中加入 `false`，候选能应用但 make 退出 2，因而被拒绝；随后按字节恢复原 Makefile，clean 重建和运行均退出 0、输出 3。恢复后的原 Makefile 仍有缺失依赖，该实验仅验证恢复可构建状态。

## 环境

| 运行 | 操作系统与架构 | 工具 | 覆盖 |
|---|---|---|---|
| 同学原始 B2 记录 | Ubuntu 24.04.4 LTS，x86_64 | GCC 13.3.0，GNU Make 4.3 | 修复前旧值复现 |
| 本机补充验证 | Ubuntu 20.04.6 LTS，x86_64 | GCC 9.4.0，GNU Make 4.2.1，Git 2.25.1 | 四种补丁、增量行为、拒绝与恢复 |

原报告配置为 `cfg-ubuntu24-gcc13-debug-v1`；补充验证属于独立环境。

## 重跑命令

需要 Git、GCC、GNU Make 和 Python 3。在主仓库根目录执行：

```bash
mkdir -p work
e3_replay=$(mktemp -d "$PWD/work/e3-mdfixer-XXXXXX")
git clone --no-checkout https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit.git "$e3_replay/lab"
git -C "$e3_replay/lab" checkout --detach 1efc4381cb1b5f5f8212c93cf082461eece50bb1
git -C "$e3_replay/lab" rev-parse 'e3-mdfixer-md-v1.0.0^{commit}'
python3 scripts/e3/verify_mdfixer.py \
    --lab-repo "$e3_replay/lab" \
    --output "$e3_replay/results"
```

脚本核对 tag 与报告的源码 SHA，在临时副本编译。输出目录必须尚不存在；通过时退出 0，`summary.json` 四项 `passed` 均为 `true`。每次重跑保留独立目录和环境记录。
