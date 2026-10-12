# MDFixer 样例与验证说明

## 固定输入与判断依据

实验仓库为 `https://github.com/WwNotVvvv/DevOps-E3-Lab-Kit.git`，报告与补丁的材料版本为 `1efc4381cb1b5f5f8212c93cf082461eece50bb1`。

固定源码 commit 为 `4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f`，对应 `e3-mdfixer-md-v1.0.0` 解引用后的 commit。在该版本中，源码位于仓库根目录，构建命令为 `make`，功能验证命令为 `./app`。

[固定 MD 报告](evidence/mdfixer-original/oracle/mdfixer/md-report.json) 指出 `main.o` 缺少 `config.h` 依赖，依据如下：

1. `main.c` 包含 `config.h`，并打印其中 `VALUE` 的值。
2. 原 Makefile 只声明 `main.o: main.c`，未声明头文件。
3. 首次构建输出 1；只将头文件的值改为 2，再执行 `make`，程序仍输出 1。

报告中的 `INSTRUCTOR_ORACLE` 表明它是课程人工预期答案。`producer_job_id` 是样例元数据，没有真实检测任务生成这份报告。

## 四种参考补丁及覆盖范围

四种补丁是同一份冻结 Makefile 的替代方案，每种单独应用在一个新副本中。

| 风格 | 参考文件 | 修复后的核心写法 |
|---|---|---|
| Target | [target.patch](evidence/mdfixer-validation-001/patches/target.patch) | `main.o: main.c config.h`，直接补依赖 |
| Macro | [macro.patch](evidence/mdfixer-validation-001/patches/macro.patch) | `DEPS = main.c config.h`，目标依赖 `$(DEPS)` |
| Hybrid | [hybrid.patch](evidence/mdfixer-validation-001/patches/hybrid.patch) | `HEADERS = config.h`，目标依赖 `main.c $(HEADERS)` |
| Implicit | [implicit.patch](evidence/mdfixer-validation-001/patches/implicit.patch) | `%.o: %.c` 配合 `-MMD -MP` 生成 `.d` 文件，再用 `-include` 读取 |

当前原始 Makefile 是 Target 写法，Macro、Hybrid、Implicit 补丁同时完成风格转换和依赖修复。这说明本次样例的实际覆盖范围。按提交清单中的“固定 MD 报告及修复样本”归档现有输入、四个参考补丁及真实验证记录；另建四种原始风格的故障基线不列为本次提交任务。

## 实际验证如何执行

[验证脚本](../../scripts/e3/verify_mdfixer.py) 从固定版本读取源码与参考补丁，为每种风格建立独立临时副本。`config.h` 中的 1、2、3 是用来观察重建行为的配置值。

| 步骤 | 操作 | 判定条件 |
|---|---|---|
| 1 | 保持 `VALUE=1`，执行 `make`、`./app` | 构建和运行退出码 0，输出 1 |
| 2 | 修改为 2，确认头文件时间晚于 `main.o`；直接执行 `make`、`./app` | 仍输出 1，且 `main.o` 时间不变，复现漏重建 |
| 3 | `git apply --check`，再 `git apply` 对应补丁 | 两条命令退出码均为 0 |
| 4 | 执行 `make clean`、`make`、`./app` | 输出 2，构建和运行成功 |
| 5 | 修改为 3，不执行 clean，直接 `make`、`./app` | `main.o` 更新时间增加，输出 3 |
| 6 | 对 Implicit 检查生成的 `main.d` | 内容包含 `main.o` 与 `config.h` |

第 5 步证明头文件变化会自动触发重建；仅有第 4 步的 clean build 成功不足以证明依赖修好。

## 无效补丁的拒绝与恢复

在各风格实验副本中，另行恢复原 Makefile，再构造一个额外的失败候选：给 `all: app` 添加执行 `false` 的命令。此时头文件保留 `VALUE=3`。

1. 候选通过 `git apply --check` 并成功应用，说明“能应用”不等于“有效”。
2. 执行 `make`，实际退出码为 2；脚本据此拒绝该候选。
3. 按字节恢复原始 Makefile，执行 `make clean`、`make`、`./app`。
4. 构建与运行退出码均为 0，输出 3，证明恢复后可以正常构建和运行。

这是验证脚本对人工构造候选的拒绝实验，尚不是自动 MDFixer 服务的运行记录。恢复的是带有原缺失依赖的 Makefile，因此不会声称恢复过程修复了 MD。

## 结果与证据位置

| 风格 | 修复前非 clean | 修复后 clean | 再改头文件非 clean | 无效候选 | 恢复后运行 | 命令记录 |
|---|---|---|---|---|---|---|
| Target | 1 | 2 | 3 | 拒绝 | 3 | [commands.json](evidence/mdfixer-validation-001/target/commands.json) |
| Macro | 1 | 2 | 3 | 拒绝 | 3 | [commands.json](evidence/mdfixer-validation-001/macro/commands.json) |
| Hybrid | 1 | 2 | 3 | 拒绝 | 3 | [commands.json](evidence/mdfixer-validation-001/hybrid/commands.json) |
| Implicit | 1 | 2 | 3 | 拒绝 | 3 | [commands.json](evidence/mdfixer-validation-001/implicit/commands.json) |

[summary.json](evidence/mdfixer-validation-001/summary.json) 保存总体结果和环境。每个风格目录还保存头文件修改时间、修复后的 Makefile、无效补丁及各步骤的标准输出/错误输出；Implicit 另保存 [main.d](evidence/mdfixer-validation-001/implicit/main.d)。

| 运行 | 操作系统与架构 | 工具 | 覆盖 |
|---|---|---|---|
| 同学原始 B2 记录 | Ubuntu 24.04.4 LTS，x86_64 | GCC 13.3.0，GNU Make 4.3 | 修复前旧值复现 |
| 本机补充验证 | Ubuntu 20.04.6 LTS，x86_64 | GCC 9.4.0，GNU Make 4.2.1，Git 2.25.1 | 四种补丁、增量行为、拒绝与恢复 |

原报告的 `cfg-ubuntu24-gcc13-debug-v1` 描述原配置。本机结果属于独立环境，不能将该配置 ID 当作本机配置。

## 重跑命令

需要 Git、GCC、GNU Make 和 Python 3。在主仓库根目录执行，创建新的工作目录并检出已审阅的实验包版本：

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

tag 解引用应得到固定源码 SHA；脚本也会核对它与报告一致。输出目录必须尚不存在。脚本成功时退出码为 0，`summary.json` 中四项 `passed` 均为 `true`；失败时保留该次输出，排查后使用新目录重跑。

脚本在临时副本编译，不修改实验仓库。它用于本次已审阅的小样例，重跑时固定上述材料版本，并独立保存新环境记录。
